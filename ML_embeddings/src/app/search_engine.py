# src/app/search_engine.py
import os
import requests
import faiss
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict, Optional
import time

load_dotenv()
VOYAGE_KEY = os.getenv("VOYAGE_API_KEY")

# Rutas dinámicas - soporte para ambos datasets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDEX_PATH = os.path.join(BASE_DIR, 'models', 'recipes_200k.index')
META_PATH = os.path.join(BASE_DIR, 'models', 'recipes_200k_metadata.pkl')

# Fallback al dataset pequeño si 200k no existe
if not os.path.exists(INDEX_PATH):
    INDEX_PATH = os.path.join(BASE_DIR, 'models', 'spoonacular.index')
    META_PATH = os.path.join(BASE_DIR, 'models', 'spoonacular_metadata.pkl')

class SmartEngine:
    """
    Motor de búsqueda semántica optimizado para 200k+ recetas.
    Features:
    - Búsqueda vectorial con FAISS
    - Filtros avanzados (tags, ingredientes)
    - Reranking por diversidad
    - Cache de queries
    """
    
    def __init__(self):
        print("⚙️ Inicializando SmartEngine...")
        
        if os.path.exists(INDEX_PATH):
            print(f" Cargando índice: {INDEX_PATH}")
            self.index = faiss.read_index(INDEX_PATH)
            self.meta = joblib.load(META_PATH)
            
            # Configurar búsqueda para precisión/velocidad
            if isinstance(self.index, faiss.IndexIVFFlat):
                self.index.nprobe = 50  # Balance velocidad/precisión
            
            print(f" Motor listo. {self.index.ntotal:,} recetas indexadas.")
            self.query_cache = {}  # Cache simple
        else:
            print(f" ERROR: Índice no encontrado en {INDEX_PATH}")
            print("   Ejecuta primero: python src/scripts/2_build_index.py")
            self.index = None
            self.meta = None

    def _get_embedding(self, text: str, use_cache: bool = True) -> Optional[np.ndarray]:
        """Obtiene embedding con cache y retry."""
        cache_key = hash(text)
        
        if use_cache and cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        headers = {"Authorization": f"Bearer {VOYAGE_KEY}"}
        payload = {
            "input": [text],
            "model": "voyage-large-2",
            "input_type": "query"
        }
        
        for attempt in range(3):
            try:
                res = requests.post(
                    "https://api.voyageai.com/v1/embeddings",
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if res.status_code == 200:
                    vec = np.array([res.json()['data'][0]['embedding']], dtype='float32')
                    faiss.normalize_L2(vec)  # Normalizar para cosine similarity
                    
                    if use_cache:
                        self.query_cache[cache_key] = vec
                    
                    return vec
                
                elif res.status_code == 429:
                    wait = (2 ** attempt) * 2
                    print(f" Rate limit. Esperando {wait}s...")
                    time.sleep(wait)
                else:
                    print(f" Error API {res.status_code}: {res.text[:100]}")
                    return None
                    
            except Exception as e:
                print(f" Error embedding (intento {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(2)
        
        return None

    def search(
        self,
        query: str,
        k: int = 10,
        filters: Optional[Dict] = None,
        diversity_boost: bool = False
    ) -> pd.DataFrame:
        """
        Búsqueda semántica con filtros y opciones avanzadas.
        
        Args:
            query: Texto de búsqueda
            k: Número de resultados
            filters: Dict con filtros opcionales:
                - tags: List[str] - Filtrar por tags
                - exclude_ingredients: List[str] - Excluir ingredientes
                - include_ingredients: List[str] - Debe incluir ingredientes
            diversity_boost: Si True, diversifica resultados por título
        
        Returns:
            DataFrame con resultados ordenados por relevancia
        """
        if not self.index or self.meta is None:
            return pd.DataFrame()

        # 1. Obtener Embedding
        vec = self._get_embedding(query)
        if vec is None:
            return pd.DataFrame()

        # 2. Búsqueda FAISS (sobre-recuperar para filtros)
        search_k = k * 5 if filters else k * 2
        D, I = self.index.search(vec, search_k)

        # 3. Obtener Resultados Iniciales
        results = self.meta.iloc[I[0]].copy()
        results['score'] = D[0]
        results['rank'] = range(len(results))

        # 4. Aplicar Filtros
        if filters:
            # Filtro por tags
            if 'tags' in filters and filters['tags']:
                mask = results['tags'].apply(
                    lambda x: any(tag.lower() in str(x).lower() for tag in filters['tags'])
                )
                results = results[mask]
            
            # Filtro excluir ingredientes
            if 'exclude_ingredients' in filters and filters['exclude_ingredients']:
                for ingredient in filters['exclude_ingredients']:
                    mask = ~results['ingredients'].str.contains(ingredient, case=False, na=False)
                    results = results[mask]
            
            # Filtro incluir ingredientes
            if 'include_ingredients' in filters and filters['include_ingredients']:
                mask = results['ingredients'].apply(
                    lambda x: all(
                        ing.lower() in str(x).lower() 
                        for ing in filters['include_ingredients']
                    )
                )
                results = results[mask]

        # 5. Diversificación (evitar recetas muy similares)
        if diversity_boost and len(results) > k:
            results = self._diversify_results(results, k)

        # 6. Limitar a k resultados
        results = results.head(k)

        return results.reset_index(drop=True)

    def _diversify_results(self, results: pd.DataFrame, k: int) -> pd.DataFrame:
        """
        Selecciona k resultados maximizando diversidad de títulos.
        Evita recetas con nombres muy similares.
        """
        selected = []
        selected_titles = []
        
        for _, row in results.iterrows():
            title_words = set(row['title'].lower().split())
            
            # Verificar si es suficientemente diferente
            is_diverse = True
            for prev_title in selected_titles:
                prev_words = set(prev_title.lower().split())
                overlap = len(title_words & prev_words) / max(len(title_words), 1)
                
                if overlap > 0.6:  # 60% de overlap = muy similar
                    is_diverse = False
                    break
            
            if is_diverse:
                selected.append(row)
                selected_titles.append(row['title'])
            
            if len(selected) >= k:
                break
        
        return pd.DataFrame(selected)

    def search_by_ingredients(self, ingredients: List[str], k: int = 10) -> pd.DataFrame:
        """Búsqueda optimizada por lista de ingredientes."""
        query = "Recipe with ingredients: " + ", ".join(ingredients)
        return self.search(
            query=query,
            k=k,
            filters={'include_ingredients': ingredients}
        )

    def get_similar_recipes(self, recipe_id: str, k: int = 5) -> pd.DataFrame:
        """Encuentra recetas similares a una receta específica."""
        recipe = self.meta[self.meta['id'] == recipe_id]
        
        if recipe.empty:
            return pd.DataFrame()
        
        # Usar título + ingredientes de la receta como query
        query = f"{recipe.iloc[0]['title']} {recipe.iloc[0]['ingredients'][:200]}"
        results = self.search(query, k=k+1)
        
        # Excluir la receta original
        return results[results['id'] != recipe_id].head(k)

    def stats(self) -> Dict:
        """Estadísticas del índice."""
        if not self.index or self.meta is None:
            return {}
        
        return {
            'total_recipes': self.index.ntotal,
            'index_type': type(self.index).__name__,
            'vector_dimension': self.index.d,
            'cache_size': len(self.query_cache),
            'metadata_columns': list(self.meta.columns)
        }


# ============================================================================
# DEMO
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print(" DEMO - Motor de Búsqueda Semántica")
    print("="*70)
    
    # Inicializar motor
    engine = SmartEngine()
    
    if engine.index is None:
        print("\nNo hay índice disponible. Ejecuta primero:")
        print("   1. python src/scripts/1_harvest.py")
        print("   2. python src/scripts/2_build_index.py")
        exit(1)
    
    # Mostrar estadísticas
    stats = engine.stats()
    print(f"\n Estadísticas:")
    print(f"   • Recetas indexadas: {stats['total_recipes']:,}")
    print(f"   • Tipo de índice: {stats['index_type']}")
    print(f"   • Dimensión de vectores: {stats['vector_dimension']}")
    
    # Búsquedas de ejemplo
    print("\n" + "="*70)
    print(" Ejemplo 1: Búsqueda simple")
    print("="*70)
    
    results = engine.search("chocolate cake", k=3)
    if not results.empty:
        print("\nResultados para 'chocolate cake':")
        for idx, row in results.iterrows():
            print(f"\n{idx+1}. {row['title']}")
            print(f"   Score: {row['score']:.4f}")
            print(f"   Tiempo: {row.get('readyInMinutes', 'N/A')} min")
            print(f"   Ingredientes: {row['ingredients'][:80]}...")
    
    # Búsqueda por ingredientes
    print("\n" + "="*70)
    print(" Ejemplo 2: Búsqueda por ingredientes")
    print("="*70)
    
    results = engine.search_by_ingredients(['chicken', 'garlic', 'lemon'], k=3)
    if not results.empty:
        print("\nResultados para ingredientes [chicken, garlic, lemon]:")
        for idx, row in results.iterrows():
            print(f"\n{idx+1}. {row['title']}")
            print(f"   Score: {row['score']:.4f}")
            print(f"   Tags: {row.get('tags', 'N/A')}")
    
    # Búsqueda con filtros
    print("\n" + "="*70)
    print(" Ejemplo 3: Búsqueda con filtros")
    print("="*70)
    
    results = engine.search(
        "healthy breakfast",
        k=3,
        filters={'max_time': 30, 'min_health_score': 50}
    )
    if not results.empty:
        print("\nResultados para 'healthy breakfast' (máx 30 min, health score > 50):")
        for idx, row in results.iterrows():
            print(f"\n{idx+1}. {row['title']}")
            print(f"   Score: {row['score']:.4f}")
            print(f"   Tiempo: {row.get('readyInMinutes', 'N/A')} min")
            print(f"   Health Score: {row.get('healthScore', 'N/A')}")
    
    print("\n" + "="*70)
    print(" Demo completado!")
