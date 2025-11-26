"""
Script para generar embeddings y construir índice FAISS.
Detecta automáticamente qué datasets tienes disponibles y te permite elegir.
"""

import os
import time
import requests
import pandas as pd
import numpy as np
import faiss
import joblib
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# --- CONFIGURACIÓN ---
load_dotenv()
API_KEY = os.getenv("VOYAGE_API_KEY")

# ============================================================================
# CONFIGURACIONES DISPONIBLES
# ============================================================================

# OPCIÓN 1: Spoonacular pequeño (100 recetas)
CONFIG_SMALL = {
    'name': 'Spoonacular (100 recetas)',
    'input_data': 'data/raw/spoonacular_recipes.parquet',
    'checkpoint_dir': 'data/checkpoints_spoon',
    'output_index': 'models/spoonacular.index',
    'output_metadata': 'models/spoonacular_metadata.pkl',
    'batch_size': 32,
    'max_workers': 2,
    'rate_limit_delay': 0.5,
    'use_ivf': False,
    'metadata_cols': ['id', 'title', 'ingredients', 'instructions', 'link', 'tags', 'pricePerServing', 'readyInMinutes', 'servings', 'healthScore']
}

# OPCIÓN 2: Spoonacular medio (450 recetas)
CONFIG_MEDIUM = {
    'name': 'Spoonacular Medio (450 recetas)',
    'input_data': 'data/raw/spoonacular_medium.parquet',
    'checkpoint_dir': 'data/checkpoints_medium',
    'output_index': 'models/spoonacular_medium.index',
    'output_metadata': 'models/spoonacular_medium_metadata.pkl',
    'batch_size': 64,
    'max_workers': 3,
    'rate_limit_delay': 0.3,
    'use_ivf': False,
    'metadata_cols': ['id', 'title', 'ingredients', 'instructions', 'link', 'tags', 'pricePerServing', 'readyInMinutes', 'servings', 'healthScore']
}

# OPCIÓN 3: Spoonacular grande (550 recetas)
CONFIG_LARGE = {
    'name': 'Spoonacular Grande (550 recetas)',
    'input_data': 'data/raw/spoonacular_large.parquet',
    'checkpoint_dir': 'data/checkpoints_large',
    'output_index': 'models/spoonacular_large.index',
    'output_metadata': 'models/spoonacular_large_metadata.pkl',
    'batch_size': 128,
    'max_workers': 4,
    'rate_limit_delay': 0.2,
    'use_ivf': True,
    'metadata_cols': ['id', 'title', 'ingredients', 'instructions', 'link', 'tags', 'pricePerServing', 'readyInMinutes', 'servings', 'healthScore']
}

# Config API Voyage
VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"
MODEL_NAME = "voyage-large-2"

# Variables globales (se asignarán después de elegir)
CONFIG = None
INPUT_DATA = None
CHECKPOINT_DIR = None
OUTPUT_INDEX = None
OUTPUT_METADATA = None
BATCH_SIZE = None
MAX_WORKERS = None
RATE_LIMIT_DELAY = None
HEADERS = None

# Lock para manejo de rate limits
rate_limit_lock = threading.Lock()
last_request_time = [0]  # Mutable para acceso desde threads

def get_embeddings_with_retry(texts, batch_id, retry_count=0, max_retries=5):
    """
    Obtiene embeddings con retry exponencial y manejo de rate limits.
    """
    # Rate limiting manual
    with rate_limit_lock:
        time_since_last = time.time() - last_request_time[0]
        if time_since_last < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - time_since_last)
        last_request_time[0] = time.time()
    
    payload = {
        "input": texts,
        "model": MODEL_NAME,
        "input_type": "document"
    }
    
    try:
        response = requests.post(VOYAGE_URL, headers=HEADERS, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()["data"]
        
        elif response.status_code == 429:
            if retry_count >= max_retries:
                print(f"Batch {batch_id}: Max retries alcanzado")
                return None
            wait = min((2 ** retry_count) * 5, 120)  # Max 2 min
            print(f"Batch {batch_id}: Rate limit. Esperando {wait}s... (retry {retry_count + 1})")
            time.sleep(wait)
            return get_embeddings_with_retry(texts, batch_id, retry_count + 1, max_retries)
        
        else:
            print(f"Batch {batch_id} Error {response.status_code}: {response.text[:200]}")
            if retry_count < max_retries:
                time.sleep(5)
                return get_embeddings_with_retry(texts, batch_id, retry_count + 1, max_retries)
            return None
            
    except Exception as e:
        print(f"Batch {batch_id} Exception: {str(e)[:100]}")
        if retry_count < max_retries:
            time.sleep(5)
            return get_embeddings_with_retry(texts, batch_id, retry_count + 1, max_retries)
        return None

def process_batch(batch_id, batch_texts):
    """Procesa un batch y retorna embeddings con su ID."""
    result = get_embeddings_with_retry(batch_texts, batch_id)
    if result:
        return (batch_id, [x['embedding'] for x in result])
    return (batch_id, None)

def select_dataset():
    """Detecta datasets disponibles y permite al usuario elegir"""
    print("\n" + "="*70)
    print("GENERACIÓN DE EMBEDDINGS - Selecciona dataset:")
    print("="*70)
    
    # Detectar qué archivos existen
    available_configs = []
    
    if os.path.exists(CONFIG_SMALL['input_data']):
        available_configs.append(('1', CONFIG_SMALL))
    
    if os.path.exists(CONFIG_MEDIUM['input_data']):
        available_configs.append(('2', CONFIG_MEDIUM))
    
    if os.path.exists(CONFIG_LARGE['input_data']):
        available_configs.append(('3', CONFIG_LARGE))
    
    if not available_configs:
        print("\nNo se encontraron datasets.")
        print("   Ejecuta primero: python src/scripts/1_harvest.py")
        return None
    
    # Mostrar opciones disponibles
    print()
    for num, config in available_configs:
        # Calcular tamaño y número de recetas
        try:
            df = pd.read_parquet(config['input_data'])
            num_recipes = len(df)
            file_size = os.path.getsize(config['input_data']) / (1024 * 1024)
            
            print(f"{num}. {config['name']}")
            print(f"   → {num_recipes} recetas")
            print(f"   → Tamaño: {file_size:.2f} MB")
            print(f"   → Archivo: {config['input_data']}")
            
            # Verificar si ya tiene índice
            if os.path.exists(config['output_index']):
                print(f" Ya existe índice: {config['output_index']}")
            print()
        except Exception as e:
            print(f"{num}. {config['name']} (Error leyendo archivo)")
            print()
    
    print("="*70)
    
    # Solicitar elección
    valid_choices = [num for num, _ in available_configs]
    choice = input(f"\nElige opción ({', '.join(valid_choices)}): ").strip()
    
    # Buscar configuración elegida
    for num, config in available_configs:
        if choice == num:
            return config
    
    print("Opción inválida")
    return None

def process_dataset(config):
    """Procesa el dataset seleccionado"""
    global CONFIG, INPUT_DATA, CHECKPOINT_DIR, OUTPUT_INDEX, OUTPUT_METADATA
    global BATCH_SIZE, MAX_WORKERS, RATE_LIMIT_DELAY, HEADERS
    
    # Asignar configuración
    CONFIG = config
    INPUT_DATA = config['input_data']
    CHECKPOINT_DIR = config['checkpoint_dir']
    OUTPUT_INDEX = config['output_index']
    OUTPUT_METADATA = config['output_metadata']
    BATCH_SIZE = config['batch_size']
    MAX_WORKERS = config['max_workers']
    RATE_LIMIT_DELAY = config['rate_limit_delay']
    HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # Crear directorios
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    print(f"\n--- PROCESANDO: {config['name']} ---")
    print(f"Input: {INPUT_DATA}")
    print(f"Output: {OUTPUT_INDEX}")
    
    # Confirmar si ya existe índice
    if os.path.exists(OUTPUT_INDEX):
        print(f"\nYa existe un índice: {OUTPUT_INDEX}")
        overwrite = input("¿Sobrescribir? (s/n): ").strip().lower()
        if overwrite != 's':
            print("Cancelado por usuario")
            return
    
    # 1. Cargar Datos
    print(f"\nCargando dataset...")
    df = pd.read_parquet(INPUT_DATA)
    print(f"Cargadas {len(df):,} recetas.")

    # 2. Crear Sopa Semántica
    print("Generando representaciones textuales...")
    
    # Adaptar según columnas disponibles
    if 'instructions' in df.columns:
        df['soup'] = (
            "Recipe: " + df['title'].fillna('') + ". " +
            "Ingredients: " + df['ingredients'].fillna('').str[:800] + ". " +
            "Instructions: " + df['instructions'].fillna('').str[:600] + ". " +
            ("Tags: " + df['tags'].fillna('') if 'tags' in df.columns else "")
        )
    else:
        # Fallback para datasets sin instrucciones
        df['soup'] = (
            "Title: " + df['title'].fillna('') + "; " +
            "Ingredients: " + df['ingredients'].fillna('') + "; " +
            ("Tags: " + df['tags'].fillna('') if 'tags' in df.columns else "")
        )
    
    # Limpieza básica
    df['soup'] = df['soup'].str.replace(r'\s+', ' ', regex=True).str.strip()
    texts = df['soup'].tolist()
    
    print(f"Longitud promedio: {sum(len(t) for t in texts) / len(texts):.0f} caracteres")

    # 3. Cargar Checkpoints Existentes
    embeddings_dict = {}  # {batch_id: vectors}
    
    if os.path.exists(CHECKPOINT_DIR):
        saved_batches = [f for f in os.listdir(CHECKPOINT_DIR) if f.endswith('.pkl')]
        if saved_batches:
            print(f"Encontrados {len(saved_batches)} checkpoints previos. Cargando...")
            for f in tqdm(saved_batches, desc="Cargando checkpoints"):
                batch_id = int(f.split('_')[1].split('.')[0])
                embeddings_dict[batch_id] = joblib.load(os.path.join(CHECKPOINT_DIR, f))
    
    completed_batches = set(embeddings_dict.keys())
    print(f"Ya procesados: {len(completed_batches) * BATCH_SIZE:,} textos")

    # 4. Preparar Batches Pendientes
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
    pending_batches = []
    
    for i in range(total_batches):
        if i not in completed_batches:
            idx_start = i * BATCH_SIZE
            idx_end = min((i + 1) * BATCH_SIZE, len(texts))
            pending_batches.append((i, texts[idx_start:idx_end]))
    
    print(f"\nEstadísticas:")
    print(f"   Total recetas: {len(texts):,}")
    print(f"   Total batches: {total_batches:,}")
    print(f"   Completados: {len(completed_batches):,}")
    print(f"   Pendientes: {len(pending_batches):,}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Workers paralelos: {MAX_WORKERS}")

    # 5. Procesamiento Paralelo con Progress Bar
    if pending_batches:
        print(f"\nIniciando procesamiento paralelo...")
        print(f"Tiempo estimado: {len(pending_batches) * 2 / 60:.1f} minutos")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit todos los batches
            future_to_batch = {
                executor.submit(process_batch, batch_id, batch_texts): batch_id
                for batch_id, batch_texts in pending_batches
            }
            
            # Progress bar
            with tqdm(total=len(pending_batches), desc="Generando embeddings") as pbar:
                for future in as_completed(future_to_batch):
                    batch_id, vectors = future.result()
                    
                    if vectors:
                        embeddings_dict[batch_id] = vectors
                        # Guardar checkpoint
                        joblib.dump(vectors, os.path.join(CHECKPOINT_DIR, f"batch_{batch_id:06d}.pkl"))
                        pbar.update(1)
                    else:
                        print(f"\nBatch {batch_id} falló. Puedes reintentar después.")
                        pbar.update(1)

    # 6. Ensamblar Embeddings en Orden
    print("\n🔧 Ensamblando embeddings en orden...")
    embeddings_list = []
    for i in range(total_batches):
        if i in embeddings_dict:
            embeddings_list.extend(embeddings_dict[i])
        else:
            print(f"Batch {i} faltante. Rellenando con ceros.")
            # Fallback: vector cero (se puede mejorar)
            dim = len(embeddings_dict[0][0]) if embeddings_dict else 1024
            embeddings_list.extend([[0.0] * dim] * BATCH_SIZE)

    # 7. Crear Índice FAISS (Simple o Optimizado según dataset)
    if embeddings_list:
        print(f"\nConstruyendo índice FAISS con {len(embeddings_list):,} vectores...")
        matrix = np.array(embeddings_list[:len(texts)], dtype='float32')
        
        # Normalizar para usar Inner Product como cosine similarity
        faiss.normalize_L2(matrix)
        dim = matrix.shape[1]
        
        # Elegir tipo de índice según tamaño del dataset
        if CONFIG['use_ivf'] and len(matrix) > 10000:
            # IndexIVFFlat: Para datasets grandes (>10k)
            print("Tipo: IndexIVFFlat (optimizado para búsqueda rápida)")
            nlist = min(1000, int(np.sqrt(len(matrix))))  # Clusters adaptativos
            quantizer = faiss.IndexFlatIP(dim)
            index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
            
            print(f"Entrenando índice ({nlist} clusters)...")
            index.train(matrix)
            
            print("Agregando vectores al índice...")
            index.add(matrix)
            
            # Balance velocidad/precisión
            index.nprobe = min(50, nlist // 20)
            print(f"nprobe configurado a {index.nprobe}")
        else:
            # IndexFlatIP: Para datasets pequeños (<10k) - Búsqueda exacta
            print("Tipo: IndexFlatIP (búsqueda exacta)")
            index = faiss.IndexFlatIP(dim)
            index.add(matrix)
        
        print(f" Guardando índice...")
        faiss.write_index(index, OUTPUT_INDEX)
        
        # 8. Guardar Metadata
        print(" Guardando metadata...")
        meta_cols = CONFIG['metadata_cols']
        available_cols = [col for col in meta_cols if col in df.columns]
        meta_df = df[available_cols].copy()
        joblib.dump(meta_df, OUTPUT_METADATA, compress=3)
        
        # Stats finales
        index_size_mb = os.path.getsize(OUTPUT_INDEX) / (1024 * 1024)
        meta_size_mb = os.path.getsize(OUTPUT_METADATA) / (1024 * 1024)
        
        print("\n" + "="*60)
        print("¡INDEXACIÓN COMPLETA!")
        print("="*60)
        print(f"Vectores indexados: {index.ntotal:,}")
        print(f"Dimensión vectores: {dim}")
        print(f"Tamaño índice: {index_size_mb:.2f} MB")
        print(f"Tamaño metadata: {meta_size_mb:.2f} MB")
        print(f" Ubicación: {OUTPUT_INDEX}")
        print("="*60)
    else:
        print(" No hay embeddings para indexar.")

def main():
    """Función principal con menú interactivo"""
    if not API_KEY:
        print("Error: VOYAGE_API_KEY no encontrada en .env")
        print("   Configura tu API key de Voyage AI")
        return
    
    # Seleccionar dataset
    config = select_dataset()
    
    if config:
        process_dataset(config)
    else:
        print("\n❌ No se pudo continuar")

if __name__ == "__main__":
    main()