"""
Script de cosecha de datos para el sistema de búsqueda de recetas.
Arquitectura de 3 niveles usando Spoonacular API:
  - Pequeño: 100 recetas (pruebas y desarrollo)
  - Medio: 450 recetas (balance entre cantidad y costo)
  - Grande: 550 recetas (máxima variedad)

Todos los datasets tienen campos estandarizados:
  id, title, ingredients, instructions, link, tags,
  pricePerServing, readyInMinutes, servings, healthScore
"""

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# Cargar configuración
load_dotenv()
SPOON_KEY = os.getenv("SPOONACULAR_API_KEY")

# ============================================================================
# OPCIÓN 1: SPOONACULAR (100 recetas) - Dataset pequeño para pruebas
# ============================================================================
OUTPUT_FILE_SMALL = 'data/raw/spoonacular_recipes.parquet'
NUM_RECIPES_SMALL = 100

def harvest_spoonacular():
    """
    Descarga 100 recetas de Spoonacular API.
    Bueno para: Pruebas rápidas, desarrollo, demo.
    Requiere: SPOONACULAR_API_KEY en .env
    """
    if not SPOON_KEY:
        print("Falta SPOONACULAR_API_KEY en .env")
        return
    
    print(f"--- COSECHA SPOONACULAR ({NUM_RECIPES_SMALL} recetas) ---")
    
    all_recipes = []
    params = {
        "apiKey": SPOON_KEY,
        "number": NUM_RECIPES_SMALL,
        "addRecipeInformation": True,
        "fillIngredients": True
    }
    
    try:
        print("Contactando API de Spoonacular...")
        response = requests.get("https://api.spoonacular.com/recipes/random", params=params)
        
        if response.status_code == 200:
            data = response.json()
            recipes = data.get('recipes', [])
            print(f"Recibidas {len(recipes)} recetas.")
            
            for r in recipes:
                ingredientes_txt = ", ".join([ing['original'] for ing in r.get('extendedIngredients', [])])
                tags = []
                if r.get('vegetarian'): tags.append('vegetarian')
                if r.get('vegan'): tags.append('vegan')
                if r.get('glutenFree'): tags.append('glutenFree')
                if r.get('veryPopular'): tags.append('popular')
                
                all_recipes.append({
                    'id': str(r.get('id')),
                    'title': r.get('title'),
                    'ingredients': ingredientes_txt,
                    'instructions': r.get('instructions', ''),
                    'link': r.get('sourceUrl', ''),
                    'tags': " ".join(tags),
                    'pricePerServing': r.get('pricePerServing', 0),
                    'readyInMinutes': r.get('readyInMinutes', 0),
                    'servings': r.get('servings', 0),
                    'healthScore': r.get('healthScore', 0)
                })
        elif response.status_code == 402:
            print("Error 402: Se acabaron tus puntos diarios de Spoonacular.")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Error de conexión: {e}")

    if all_recipes:
        df = pd.DataFrame(all_recipes)
        os.makedirs('data/raw', exist_ok=True)
        df.to_parquet(OUTPUT_FILE_SMALL)
        print(f"💾 Guardado en: {OUTPUT_FILE_SMALL}")
        print(df.head(2))
    else:
        print("No se guardaron datos.")


# ============================================================================
# OPCIÓN 2: Spoonacular Medio (450 recetas)
# ============================================================================
OUTPUT_FILE_MEDIUM = 'data/raw/spoonacular_medium.parquet'
TARGET_RECIPES_MEDIUM = 450

def harvest_spoonacular_medium():
    """
    Descarga 450 recetas usando Spoonacular API.
    Balance entre cantidad y calidad.
    Requiere: SPOONACULAR_API_KEY
    """
    if not SPOON_KEY:
        print("❌ Falta SPOONACULAR_API_KEY en .env")
        return
    
    print(f"--- 🥕 COSECHA SPOONACULAR MEDIO ({TARGET_RECIPES_MEDIUM} recetas) ---")
    print("⚠️  Esto consumirá ~450 puntos API")
    
    confirm = input("¿Continuar? (s/n): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado por usuario")
        return
    
    all_recipes = []
    seen_ids = set()
    
    # Queries para maximizar variedad
    search_queries = [
        'chicken', 'pasta', 'beef', 'salad', 'soup', 'dessert',
        'vegetarian', 'seafood', 'rice', 'breakfast', 'mexican', 'italian'
    ]
    
    try:
        print("📡 Buscando recetas en múltiples categorías...")
        
        for query in tqdm(search_queries, desc="Buscando"):
            if len(all_recipes) >= TARGET_RECIPES_MEDIUM:
                break
            
            # Búsqueda con información completa
            params = {
                'apiKey': SPOON_KEY,
                'query': query,
                'number': 50,
                'addRecipeInformation': True,
                'fillIngredients': True
            }
            
            response = requests.get(
                'https://api.spoonacular.com/recipes/complexSearch',
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                for recipe in results:
                    recipe_id = str(recipe.get('id'))
                    
                    if recipe_id in seen_ids:
                        continue
                    
                    seen_ids.add(recipe_id)
                    
                    # Segunda llamada para obtener información completa incluyendo instructions
                    info_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
                    info_response = requests.get(
                        info_url,
                        params={'apiKey': SPOON_KEY},
                        timeout=30
                    )
                    
                    if info_response.status_code == 200:
                        recipe = info_response.json()
                        
                        # Extraer ingredientes
                        ingredients = []
                        if 'extendedIngredients' in recipe:
                            ingredients = [ing['original'] for ing in recipe.get('extendedIngredients', [])]
                        
                        # Tags
                        tags = []
                        if recipe.get('vegetarian'): tags.append('vegetarian')
                        if recipe.get('vegan'): tags.append('vegan')
                        if recipe.get('glutenFree'): tags.append('glutenFree')
                        if recipe.get('dairyFree'): tags.append('dairyFree')
                        if recipe.get('veryHealthy'): tags.append('healthy')
                        
                        all_recipes.append({
                            'id': f"spoon_{recipe_id}",
                            'title': recipe.get('title', ''),
                            'ingredients': ", ".join(ingredients),
                            'instructions': recipe.get('instructions', ''),
                            'link': recipe.get('sourceUrl', ''),
                            'tags': " ".join(tags),
                            'pricePerServing': recipe.get('pricePerServing', 0),
                            'readyInMinutes': recipe.get('readyInMinutes', 0),
                            'servings': recipe.get('servings', 0),
                            'healthScore': recipe.get('healthScore', 0)
                        })
                        
                        time.sleep(0.3)  # Rate limiting para la llamada extra
                        
                        if len(all_recipes) >= TARGET_RECIPES_MEDIUM:
                            break
            
            elif response.status_code == 402:
                print("\n❌ Límite de puntos alcanzado")
                break
            
            elif response.status_code == 429:
                print("\nRate limit. Esperando 60s...")
                time.sleep(60)
            
            time.sleep(0.5)  # Rate limiting entre queries
        
        if all_recipes:
            print(f"\n💾 Guardando {len(all_recipes):,} recetas únicas...")
            df = pd.DataFrame(all_recipes)
            os.makedirs('data/raw', exist_ok=True)
            df.to_parquet(OUTPUT_FILE_MEDIUM, compression='snappy', index=False)
            
            file_size_mb = os.path.getsize(OUTPUT_FILE_MEDIUM) / (1024 * 1024)
            print(f"\n✅ ¡ÉXITO! Guardado en: {OUTPUT_FILE_MEDIUM}")
            print(f"📊 Total recetas: {len(df):,}")
            print(f"💽 Tamaño archivo: {file_size_mb:.2f} MB")
            print(f"\n📋 Muestra:")
            print(df[['title', 'healthScore']].head(3))
        else:
            print("⚠️ No se guardaron datos.")
            
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# OPCIÓN 3: Spoonacular Grande (550 recetas)
# ============================================================================
OUTPUT_FILE_SPOON_LARGE = 'data/raw/spoonacular_large.parquet'
TARGET_SPOON_LARGE = 550

def harvest_spoonacular_large():
    """
    Descarga 550 recetas usando Spoonacular API.
    Estrategia: Búsquedas exhaustivas en múltiples categorías.
    Requiere: SPOONACULAR_API_KEY
    """
    if not SPOON_KEY:
        print("❌ Falta SPOONACULAR_API_KEY en .env")
        return
    
    print(f"--- 🥕 COSECHA SPOONACULAR GRANDE ({TARGET_SPOON_LARGE} recetas) ---")
    print("⚠️  Esto consumirá ~1300 puntos API (doble llamada por receta)")
    
    confirm = input("¿Continuar? (s/n): ").strip().lower()
    if confirm != 's':
        print("Cancelado por usuario")
        return
    
    all_recipes = []
    seen_ids = set()
    
    search_queries = [
        'chicken', 'pasta', 'beef', 'salad', 'soup', 'dessert', 'cake',
        'vegetarian', 'vegan', 'seafood', 'pork', 'rice', 'bread',
        'breakfast', 'lunch', 'dinner', 'appetizer', 'side dish',
        'mexican', 'italian', 'chinese', 'indian', 'thai', 'japanese',
        'healthy', 'quick', 'easy', 'gourmet', 'comfort food'
    ]
    
    print(f"\nBuscando recetas en {len(search_queries)} categorías...")
    
    for query in tqdm(search_queries, desc="Buscando"):
        if len(all_recipes) >= TARGET_SPOON_LARGE:
            break
        
        try:
            # Búsqueda compleja con muchos resultados
            params = {
                'apiKey': SPOON_KEY,
                'query': query,
                'number': 100,  # Máximo por request
                'addRecipeInformation': True,
                'fillIngredients': True,
                'sort': 'popularity',
                'sortDirection': 'desc'
            }
            
            response = requests.get(
                'https://api.spoonacular.com/recipes/complexSearch',
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                for recipe in results:
                    recipe_id = str(recipe.get('id'))
                    
                    # Evitar duplicados
                    if recipe_id in seen_ids:
                        continue
                    
                    seen_ids.add(recipe_id)
                    
                    # Extraer ingredientes
                    ingredients = []
                    if 'extendedIngredients' in recipe:
                        ingredients = [
                            ing['original'] 
                            for ing in recipe.get('extendedIngredients', [])
                        ]
                    
                    # Tags
                    tags = []
                    if recipe.get('vegetarian'): tags.append('vegetarian')
                    if recipe.get('vegan'): tags.append('vegan')
                    if recipe.get('glutenFree'): tags.append('glutenFree')
                    if recipe.get('dairyFree'): tags.append('dairyFree')
                    if recipe.get('veryHealthy'): tags.append('healthy')
                    if recipe.get('cheap'): tags.append('budget')
                    if recipe.get('veryPopular'): tags.append('popular')
                    
                    # Obtener detalles completos de la receta (instrucciones)
                    detail_response = requests.get(
                        f"https://api.spoonacular.com/recipes/{recipe_id}/information",
                        params={'apiKey': SPOON_KEY},
                        timeout=10
                    )
                    
                    instructions = ''
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        instructions = detail_data.get('instructions', '')
                    
                    all_recipes.append({
                        'id': f"spoon_{recipe_id}",
                        'title': recipe.get('title', ''),
                        'ingredients': ", ".join(ingredients),
                        'instructions': instructions,
                        'link': recipe.get('sourceUrl', ''),
                        'tags': " ".join(tags),
                        'pricePerServing': recipe.get('pricePerServing', 0),
                        'readyInMinutes': recipe.get('readyInMinutes', 0),
                        'servings': recipe.get('servings', 0),
                        'healthScore': recipe.get('healthScore', 0)
                    })
                    
                    time.sleep(0.3)  # Rate limiting para la llamada extra
                    
                    if len(all_recipes) >= TARGET_SPOON_LARGE:
                        break
            
            elif response.status_code == 402:
                print("\nError 402: Límite de puntos alcanzado")
                break
            
            elif response.status_code == 429:
                print("\nRate limit. Esperando 60s...")
                time.sleep(60)
            
            time.sleep(0.5)  # Rate limiting
        
        except Exception as e:
            print(f"\nError en query '{query}': {e}")
            continue
    
    # Guardar resultados
    if all_recipes:
        print(f"\nGuardando {len(all_recipes):,} recetas...")
        df = pd.DataFrame(all_recipes)
        os.makedirs('data/raw', exist_ok=True)
        df.to_parquet(OUTPUT_FILE_SPOON_LARGE, compression='snappy', index=False)
        
        file_size_mb = os.path.getsize(OUTPUT_FILE_SPOON_LARGE) / (1024 * 1024)
        print(f"\n¡ÉXITO! Guardado en: {OUTPUT_FILE_SPOON_LARGE}")
        print(f"Total recetas únicas: {len(df):,}")
        print(f"Tamaño archivo: {file_size_mb:.2f} MB")
        print(f"\n Muestra:")
        print(df[['title', 'healthScore']].head(3))
    else:
        print("No se guardaron datos.")


# ============================================================================

# MENÚ PRINCIPAL

def main():
    print("\n" + "="*70)
    print("COSECHA DE RECETAS - Selecciona una opción:")
    print("="*70)
    print("\n1. PEQUEÑO: Spoonacular (100 recetas)")
    print("   → Rápido, bueno para pruebas")
    print("   → Requiere: SPOONACULAR_API_KEY")
    print("   → Tiempo: ~30 segundos")
    print("   → Costo: ~100 puntos API")
    print("\n2. MEDIO: Spoonacular (450 recetas)")
    print("   → Balance entre cantidad y variedad")
    print("   → Requiere: SPOONACULAR_API_KEY")
    print("   → Tiempo: ~5-10 minutos")
    print("   → Costo: ~900 puntos API (doble llamada por receta)")
    print("\n3. GRANDE: Spoonacular (550 recetas)")
    print("   → Máxima calidad y variedad")
    print("   → Requiere: SPOONACULAR_API_KEY")
    print("   → Tiempo: ~12-15 minutos")
    print("   → Costo: ~1100 puntos API (doble llamada por receta)")
    print("\n" + "="*70)
    
    choice = input("\nElige opción (1, 2 o 3): ").strip()
    
    if choice == "1":
        harvest_spoonacular()
    elif choice == "2":
        harvest_spoonacular_medium()
    elif choice == "3":
        harvest_spoonacular_large()
    else:
        print("Opción inválida. Usa 1, 2 o 3")

if __name__ == "__main__":
    main()