# Motor de Búsqueda Semántica de Recetas

Sistema de búsqueda inteligente para recetas usando embeddings vectoriales y FAISS.

## Características

-  **Búsqueda Semántica**: Encuentra recetas por significado, no solo palabras clave
-  **Tres Niveles Escalables**: 100, 450 o 550 recetas según tus necesidades
-  **Filtros Avanzados**: Por tags, ingredientes, tiempo, salubridad
-  **IA de Última Generación**: Embeddings Voyage AI (1024-dim) + Índice FAISS
-  **Procesamiento Eficiente**: Checkpoints, procesamiento paralelo, caché
-  **Datos Estandarizados**: 10 campos consistentes en todos los niveles

## Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|------------|-----------||
| **Datos** | Spoonacular API | 100/450/550 recetas de alta calidad |
| **Embeddings** | Voyage AI (voyage-large-2) | Vectores semánticos de 1024 dimensiones |
| **Búsqueda** | FAISS (FlatIP/IVFFlat) | Búsqueda de similitud ultrarrápida |
| **Storage** | Parquet + Joblib | Almacenamiento comprimido eficiente |
| **Procesamiento** | Pandas + NumPy | Manipulación y análisis de datos |

##  Inicio Rápido

### 1. Instalación

```powershell
# Crear entorno virtual
python -m venv embeddings
.\embeddings\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar API Keys

Crear archivo `.env` en la raíz del proyecto:
```env
SPOONACULAR_API_KEY=tu_key_de_spoonacular
VOYAGE_API_KEY=tu_key_de_voyage
```

>  Obtén tus API keys gratis:
> - **Spoonacular**: https://spoonacular.com/food-api (150 puntos/día)
> - **Voyage AI**: https://www.voyageai.com (300 requests gratis)

### 3. Generar Dataset e Índice

El sistema ofrece **3 niveles escalables**:

```powershell
# Paso 1: Cosechar recetas (menú interactivo)
python src/scripts/1_harvest.py

# Opciones disponibles:
# 1. PEQUEÑO: 100 recetas (~30 seg, ~100 puntos API)
# 2. MEDIO: 450 recetas (~5-10 min, ~900 puntos API)
# 3. GRANDE: 550 recetas (~12-15 min, ~1100 puntos API)

# Paso 2: Generar índice de embeddings
python src/scripts/2_build_index.py
# El script detecta automáticamente los datasets disponibles

# Paso 3: Probar el motor de búsqueda
python src/scripts/test_search.py
```

> **Recomendación**: Empieza con **PEQUEÑO** para validar, luego usa **MEDIO** para prototipado o **GRANDE** para producción.

####  **Campos Estandarizados** (todos los niveles)
Todas las recetas incluyen estos 10 campos:
- `id`, `title`, `ingredients`, `instructions`, `link`
- `tags`, `pricePerServing`, `readyInMinutes`, `servings`, `healthScore`

>  Ver **[GUIA_USO.md](GUIA_USO.md)** para instrucciones detalladas.


## Arquitectura del Sistema

```
┌─────────────────────┐
│  Spoonacular API    │  Recetas de alta calidad
│  (3 niveles)        │  100 / 450 / 550
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  1_harvest.py       │  Cosecha y normalización
│                     │  • Búsqueda por categorías
│                     │  • Doble llamada API (medio/grande)
│                     │  • 10 campos estandarizados
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Voyage AI          │  Generación de embeddings
│  voyage-large-2     │  • Vectores 1024-dim
│                     │  • Batch processing paralelo
│                     │  • Sistema de checkpoints
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2_build_index.py   │  Construcción de índice FAISS
│                     │  • FlatIP (100-450 recetas)
│                     │  • IVFFlat (550+ recetas)
│                     │  • Auto-detección de datasets
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  SmartEngine        │  Motor de búsqueda
│  (search_engine.py) │  • Búsqueda semántica
│                     │  • Filtros avanzados
│                     │  • Cache de queries
│                     │  • Diversificación de resultados
└─────────────────────┘
```

##  Estructura del Proyecto

```
ML_embeddings/
├── data/
│   ├── raw/                              # Datasets cosechados
│   │   ├── spoonacular_recipes.parquet   # 100 recetas
│   │   ├── spoonacular_medium.parquet    # 450 recetas
│   │   └── spoonacular_large.parquet     # 550 recetas
│   └── checkpoints_*/                    # Checkpoints por nivel
├── models/
│   ├── spoonacular.index                 # Índice pequeño
│   ├── spoonacular_medium.index          # Índice medio
│   ├── spoonacular_large.index           # Índice grande
│   └── *_metadata.pkl                    # Metadatos asociados
├── src/
│   ├── app/
│   │   └── search_engine.py              # Motor de búsqueda
│   └── scripts/
│       ├── 1_harvest.py                  # Cosecha de datos
│       ├── 2_build_index.py              # Generación de índices
│       ├── test_search.py                # Tests automáticos
│       └── busqueda_interactiva.py       # Búsqueda interactiva
├── .env                                   # API keys (no commitear)
├── requirements.txt
├── README.md
└── GUIA_USO.md                           # Guía detallada
```

