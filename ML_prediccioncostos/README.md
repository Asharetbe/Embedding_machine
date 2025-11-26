# Sistema de Predicción de Precios de Alimentos

Sistema interactivo para predecir precios de productos alimenticios en México.

## 📋 Requisitos

```bash
pip install -r requirements.txt
```

## 🚀 Uso

### Opción 1: Script Interactivo (Recomendado)

```bash
python predictor_precios.py
```

El script te guiará paso a paso:

1. **Ver productos disponibles**: Lista todos los productos con modelos entrenados
2. **Generar predicciones**: 
   - Ingresa el período de fechas (formato: YYYY-MM-DD)
   - Agrega productos uno por uno (escribe 'ver' para ver disponibles)
   - Escribe 'fin' cuando termines
   - Confirma y procesa

### Opción 2: Notebook Jupyter

```bash
jupyter notebook prueba_de_modelos.ipynb
```

## 📊 Salidas Generadas

### 1. JSON Consolidado
**Ubicación**: `./predicciones/predicciones_FECHA-INICIO_a_FECHA-FIN.json`

**Estructura**:
```json
{
  "fecha_consulta": "2025-11-25 19:20:54",
  "periodo": {
    "inicio": "2026-01-01",
    "fin": "2026-01-31"
  },
  "total_productos": 5,
  "productos": [
    {
      "alimento": "Tortilla de maíz",
      "mejor_dia_compra": {
        "fecha_inicio": "2026-01-12",
        "fecha_fin": "2026-01-16",
        "precio_esperado": 17.43,
        "dias_disponibles": 5
      },
      "grafica": "./graficas/tortilla_de_maiz_2026-01-01_a_2026-01-31.png",
      "predicciones": [
        {
          "fecha": "2026-01-01",
          "precio_esperado": 18.96,
          "precio_min": 14.91,
          "precio_max": 23.31
        }
      ]
    }
  ]
}
```

### 2. Gráficas
**Ubicación**: `./graficas/`

- Una gráfica por producto en formato PNG
- Resolución: 300 DPI
- Incluye precio esperado e intervalo de confianza

## 🎯 Características

✅ **Predicciones diarias** para cualquier rango de fechas  
✅ **Mejor día/período de compra** detectado automáticamente  
✅ **Rangos de fechas** cuando el precio mínimo se mantiene varios días  
✅ **Gráficas automáticas** con intervalos de confianza  
✅ **JSON listo para frontend** con rutas relativas  
✅ **Interfaz interactiva** con validación de datos  

## 📦 Productos Disponibles

El sistema incluye modelos para:
- Tortilla de maíz
- Arroz
- Frijol
- Huevo
- Leche pasteurizada y fresca
- Y muchos más...

Usa la opción 1 del menú para ver la lista completa.

## 🔧 Estructura del Proyecto

```
ML_prediccioncostos/
├── predictor_precios.py     # Script interactivo principal
├── prueba_de_modelos.ipynb  # Notebook alternativo
├── requirements.txt          # Dependencias
├── modelos_join/            # Modelos entrenados (.pkl)
├── predicciones/            # JSONs generados
└── graficas/                # Gráficas generadas
```

## 💡 Ejemplo de Uso

```bash
$ python predictor_precios.py

============================================================
   SISTEMA DE PREDICCIÓN DE PRECIOS DE ALIMENTOS
============================================================

1. Ver productos disponibles
2. Generar predicciones para productos
3. Salir

Seleccione una opción (1-3): 2

📅 CONFIGURACIÓN DEL PERÍODO
------------------------------------------------------------
Fecha de inicio (YYYY-MM-DD, ejemplo: 2026-01-01): 2026-01-01
Fecha de fin (YYYY-MM-DD, ejemplo: 2026-01-31): 2026-01-31

🛒 SELECCIÓN DE PRODUCTOS
------------------------------------------------------------
Producto 1: Tortilla de maíz
✓ 'Tortilla de maíz' agregado (1 producto(s) en total)

Producto 2: Arroz
✓ 'Arroz' agregado (2 producto(s) en total)

Producto 3: fin

[Procesando...]
```

## 🤝 Soporte

Para problemas o preguntas, revisa que:
- Todos los archivos de modelos estén en `modelos_join/`
- Las dependencias estén instaladas correctamente
- Las fechas estén en formato YYYY-MM-DD
