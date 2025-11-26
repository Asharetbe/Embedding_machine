# Guía de Uso - Sistema de Búsqueda Semántica de Recetas

## Tres Niveles Disponibles

El sistema ofrece **3 configuraciones escalables** usando Spoonacular API:

### **1. PEQUEÑO** (100 recetas)
 **Ideal para:** Pruebas rápidas, desarrollo, demos  
 **Tiempo total:** ~3-5 minutos  
 **Costo API:** ~100 puntos Spoonacular

### **2. MEDIO** (450 recetas)
 **Ideal para:** Balance entre cantidad y costo, prototipado  
 **Tiempo total:** ~15-20 minutos  
 **Costo API:** ~900 puntos Spoonacular 

### **3. GRANDE** (550 recetas)
 **Ideal para:** Producción, máxima variedad y calidad  
 **Tiempo total:** ~25-30 minutos  
 **Costo API:** ~1100 puntos Spoonacular 

---

## Inicio Rápido (3 Pasos)

### **Paso 1: Configurar API Keys**

Crea archivo `.env` en la raíz del proyecto:
```env
SPOONACULAR_API_KEY=tu_key_de_spoonacular
VOYAGE_API_KEY=tu_key_de_voyage
```

**Obtener keys gratuitas:**
- Spoonacular: https://spoonacular.com/food-api (150 puntos/día gratis)
- Voyage AI: https://www.voyageai.com (300 requests gratis)

---

### **Paso 2: Recolecta recetas**

```powershell
python src/scripts/1_harvest.py
```

Se abrirá un menú interactivo:
```
1. PEQUEÑO: Spoonacular (100 recetas)    → ~30 segundos
2. MEDIO: Spoonacular (450 recetas)      → ~5-10 minutos  
3. GRANDE: Spoonacular (550 recetas)     → ~12-15 minutos
```

**Archivos generados:**
- `data/raw/spoonacular_recipes.parquet` (opción 1)
- `data/raw/spoonacular_medium.parquet` (opción 2)
- `data/raw/spoonacular_large.parquet` (opción 3)

---

### **Paso 3: Generar Índice de Embeddings**

```powershell
python src/scripts/2_build_index.py
```

El script detecta automáticamente qué datasets tienes y permite elegir cuál indexar.

**Archivos generados:**
- `models/spoonacular.index` + metadata
- `models/spoonacular_medium.index` + metadata
- `models/spoonacular_large.index` + metadata

 **Sistema de checkpoints:** Si el proceso se interrumpe, simplemente vuelve a ejecutar el script. Continuará desde donde quedó.

---

##  Uso del motor de búsqueda

### **Desde Python (Para integrar en tu aplicación)**

```python
from src.app.search_engine import SmartEngine

# Inicializar motor (detecta automáticamente el índice disponible)
engine = SmartEngine()

# Búsqueda básica
results = engine.search("pasta with tomato and basil", k=5)
print(results[['title', 'score', 'ingredients']])

# Búsqueda por ingredientes
results = engine.search_by_ingredients(
    ["chicken", "garlic", "lemon"],
    k=10
)

# Búsqueda con filtros
results = engine.search(
    "healthy breakfast",
    k=5,
    filters={
        'max_time': 30,           # Máximo 30 minutos
        'min_health_score': 50,   # Mínimo health score
        'tags': ['vegetarian']    # Solo vegetarianas
    }
)

# Recetas similares
similar = engine.get_similar_recipes(recipe_id="spoon_12345", k=5)
```

### **Búsqueda Interactiva (Para pruebas)**

```powershell
# Pruebas automáticas
python src/scripts/test_search.py

# Búsqueda interactiva manual
python src/scripts/busqueda_interactiva.py
```

---

##  Campos Estandarizados de Recetas

Todos los datasets tienen **10 campos consistentes**:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único (formato: `spoon_12345`) |
| `title` | string | Nombre de la receta |
| `ingredients` | string | Lista de ingredientes separados por coma |
| `instructions` | string | Pasos de preparación |
| `link` | string | URL a la receta original |
| `tags` | string | Etiquetas (vegetarian, vegan, glutenFree, etc.) |
| `pricePerServing` | float | Costo aproximado por porción |
| `readyInMinutes` | int | Tiempo total de preparación |
| `servings` | int | Número de porciones |
| `healthScore` | int | Puntuación de salubridad (0-100) |

---

##  Recomendaciones por Caso de Uso

### ** Para Desarrollo y Pruebas**
- Usa **PEQUEÑO (100 recetas)**
- Iteración rápida, bajo costo
- Perfecto para validar tu pipeline

### ** Para Prototipado/MVP**
- Usa **MEDIO (450 recetas)**  
- Balance ideal entre variedad y tiempo
- Suficiente para demos realistas

### ** Para Producción**
- Usa **GRANDE (550 recetas)**
- Máxima variedad y calidad
- Genera índice una vez, reutiliza indefinidamente

---

##  Integración con Otros Módulos del Proyecto

Este sistema de embeddings está diseñado para integrarse con los demás componentes:

### ** Módulo de App (Interfaz de Usuario)**
```python
from src.app.search_engine import SmartEngine

engine = SmartEngine()

# Búsqueda desde input de usuario
user_query = "recetas con pollo"
results = engine.search(user_query, k=10)

# Enviar resultados a la UI
return results.to_dict('records')
```

### ** Módulo de Visión (Imagen → Ingredientes)**
```python
# Recibe lista de ingredientes detectados en imagen
detected_ingredients = ["tomato", "mozzarella", "basil", "olive oil"]

# Buscar recetas que usen esos ingredientes
recipes = engine.search_by_ingredients(detected_ingredients, k=10)
```

### ** Módulo de NLP (Texto → Ingredientes)**
```python
# Tu compañera extrae ingredientes del texto natural
user_text = "quiero hacer algo con pollo, ajo y limón"
extracted_ingredients = nlp_module.extract_ingredients(user_text)

# Hacer match con embeddings
matches = engine.search_by_ingredients(extracted_ingredients, k=10)

# Filtrar por preferencias adicionales
filtered = engine.search(
    user_text,
    k=10,
    filters={'tags': ['healthy'], 'max_time': 45}
)
```

