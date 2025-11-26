# API de predicción de precios de alimentos

API para predecir precios de alimentos usando modelos Prophet. 

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Prophet](https://img.shields.io/badge/Prophet-1.1+-orange.svg)](https://facebook.github.io/prophet/)

## Características

-  **87 productos** con modelos de predicción entrenados
-  **Predicciones diarias** con intervalos de confianza
-  **Búsqueda inteligente** con sugerencias de productos similares
-  **Detección automática** del mejor día/período para comprar
-  **Gráficas PNG** 
-  **API RESTful** lista para integrar
-  **CORS habilitado** para desarrollo frontend

##  Inicio Rápido

### Instalación Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python app_flask.py

# API disponible en:
# http://localhost:5000/api
```

## Endpoints de la API

### Health Check
```bash
GET /api/health
```

### Obtener Productos
```bash
GET /api/productos
# Retorna: Lista de 87 productos disponibles
```

### Buscar Producto
```bash
GET /api/productos/buscar?q=leche
# Retorna: Producto exacto o sugerencias similares
```

### Generar Predicciones
```bash
POST /api/predicciones
Content-Type: application/json

{
  "productos": ["Tortilla de maíz", "Arroz", "Huevo"],
  "fecha_inicio": "2026-01-01",
  "fecha_fin": "2026-01-31",
  "generar_graficas": true
}
```

## Formato de Respuestas

```json
{
  "success": true,
  "fecha_consulta": "2025-11-25 19:20:54",
  "periodo": {
    "inicio": "2026-01-01",
    "fin": "2026-01-31"
  },
  "total_productos": 3,
  "productos": [
    {
      "alimento": "Tortilla de maíz",
      "mejor_dia_compra": {
        "tipo": "rango",
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

### Mejor Día de Compra

**Día único:**
```json
{
  "tipo": "dia_unico",
  "fecha": "2026-01-15",
  "precio_esperado": 17.43
}
```

**Rango de días:** 
```json
{
  "tipo": "rango",
  "fecha_inicio": "2026-01-12",
  "fecha_fin": "2026-01-16",
  "precio_esperado": 17.43,
  "dias_disponibles": 5
}
```

## Productos Disponibles

**87 productos** con modelos entrenados:
- Tortilla de maíz, Arroz, Frijol, Huevo, Leche
- Carnes: Pollo, Res, Cerdo, Pescado
- Frutas: Manzana, Plátano, Naranja, Aguacate
- Verduras: Jitomate, Cebolla, Papa, Lechuga
- Y muchos más...

Endpoint: `GET /api/productos` para lista completa.

## Estructura del Proyecto

```
ML_prediccioncostos/
├── api_predictor.py         # Lógica core de la API
├── app_flask.py             # Servidor REST
├── requirements.txt         # Dependencias
├── Procfile                 # Configuración de deploy
├── Dockerfile               # Contenedor Docker
├── modelos_join/            # 87 modelos Prophet (.pkl)
├── predicciones/            # JSONs generados
├── graficas/                # Gráficas PNG generadas
```

## Tecnologías

- **Python 3.11** - Lenguaje principal
- **Flask 2.3+** - Framework web
- **Prophet 1.1+** - Predicción de series temporales
- **Pandas 2.0+** - Manipulación de datos
- **Matplotlib 3.7+** - Generación de gráficas
- **Gunicorn** - Servidor WSGI para producción

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

