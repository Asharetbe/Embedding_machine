# API de Predicción de Precios - Documentación para Frontend

Sistema backend optimizado para ser consumido por aplicaciones frontend (React, Vue, Angular, etc.)

## 📋 Tabla de Contenidos

- [Instalación](#instalación)
- [Iniciar el Servidor](#iniciar-el-servidor)
- [Endpoints de la API](#endpoints-de-la-api)
- [Ejemplos de Integración](#ejemplos-de-integración)
- [Estructura de Respuestas](#estructura-de-respuestas)

---

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Verificar que existe la carpeta de modelos

Asegúrate de tener la carpeta `modelos_join/` con los archivos `.pkl` de los modelos.

---

## ▶️ Iniciar el Servidor

### Opción 1: Flask (Recomendado para desarrollo)

```bash
python app_flask.py
```

El servidor estará disponible en: `http://localhost:5000`

### Opción 2: Usar API directamente (sin servidor web)

```python
from api_predictor import inicializar_api, generar_predicciones_api

# Usar las funciones directamente
resultado = generar_predicciones_api(
    productos=["Tortilla de maíz", "Arroz"],
    fecha_inicio="2026-01-01",
    fecha_fin="2026-01-31"
)
```

---

## 🌐 Endpoints de la API

### 1. Health Check

**GET** `/api/health`

Verifica que el servicio está funcionando.

**Response:**
```json
{
  "status": "ok",
  "service": "Predictor de Precios API",
  "timestamp": "2025-11-25T10:30:00"
}
```

---

### 2. Obtener Productos Disponibles

**GET** `/api/productos`

Retorna la lista completa de productos que tienen modelos disponibles.

**Response:**
```json
{
  "success": true,
  "total": 87,
  "productos": [
    "Arroz",
    "Frijol",
    "Huevo",
    "Leche Pasteurizada Y Fresca",
    "Tortilla de maíz",
    ...
  ]
}
```

---

### 3. Buscar Producto

**GET** `/api/productos/buscar?q=<nombre>`

Busca un producto por nombre. Si no encuentra coincidencia exacta, sugiere productos similares.

**Query Parameters:**
- `q` (requerido): Nombre del producto a buscar

**Ejemplos:**

```bash
# Búsqueda exacta
GET /api/productos/buscar?q=Arroz

# Búsqueda con sugerencias
GET /api/productos/buscar?q=leche
```

**Response (encontrado):**
```json
{
  "success": true,
  "encontrado": true,
  "producto_exacto": "Arroz",
  "sugerencias": []
}
```

**Response (sugerencias):**
```json
{
  "success": true,
  "encontrado": false,
  "producto_exacto": null,
  "sugerencias": [
    "Leche Pasteurizada Y Fresca",
    "Leche En Polvo",
    "Crema De Leche",
    "Leche Evaporada Condensada Y Maternizada"
  ]
}
```

---

### 4. Generar Predicciones

**POST** `/api/predicciones`

Genera predicciones de precios para una lista de productos en un rango de fechas.

**Request Body:**
```json
{
  "productos": ["Tortilla de maíz", "Arroz", "Huevo"],
  "fecha_inicio": "2026-01-01",
  "fecha_fin": "2026-01-31",
  "generar_graficas": true
}
```

**Response:**
```json
{
  "success": true,
  "fecha_consulta": "2025-11-25 10:30:00",
  "periodo": {
    "inicio": "2026-01-01",
    "fin": "2026-01-31"
  },
  "total_productos": 3,
  "productos_procesados": 3,
  "productos_con_error": 0,
  "productos": [
    {
      "alimento": "Tortilla de maíz",
      "fecha_inicio": "2026-01-01",
      "fecha_fin": "2026-01-31",
      "unidad": "kg/litro",
      "total_registros": 31,
      "mejor_dia_compra": {
        "tipo": "rango",
        "fecha_inicio": "2026-01-12",
        "fecha_fin": "2026-01-16",
        "precio_esperado": 17.43,
        "precio_min": 15.20,
        "precio_max": 19.66,
        "dias_disponibles": 5
      },
      "grafica": "./graficas/tortilla_de_maiz_2026-01-01_a_2026-01-31.png",
      "predicciones": [
        {
          "fecha": "2026-01-01",
          "precio_esperado": 17.55,
          "precio_min": 15.30,
          "precio_max": 19.80
        },
        ...
      ]
    },
    ...
  ],
  "ruta_json": "./predicciones/predicciones_2026-01-01_a_2026-01-31.json"
}
```

---

### 5. Obtener Gráfica

**GET** `/api/graficas/<filename>`

Retorna la imagen PNG de una gráfica generada.

**Ejemplo:**
```bash
GET /api/graficas/tortilla_de_maiz_2026-01-01_a_2026-01-31.png
```

**Response:** Imagen PNG

---

### 6. Obtener JSON de Predicción

**GET** `/api/predicciones/<filename>`

Retorna el archivo JSON de una predicción previamente generada.

**Ejemplo:**
```bash
GET /api/predicciones/predicciones_2026-01-01_a_2026-01-31.json
```

**Response:** Archivo JSON

---

## 💻 Ejemplos de Integración

### JavaScript (Fetch API)

```javascript
const API_BASE_URL = 'http://localhost:5000/api';

// Obtener productos
async function obtenerProductos() {
  const response = await fetch(`${API_BASE_URL}/productos`);
  const data = await response.json();
  console.log(data.productos);
}

// Generar predicciones
async function generarPredicciones() {
  const response = await fetch(`${API_BASE_URL}/predicciones`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      productos: ['Tortilla de maíz', 'Arroz'],
      fecha_inicio: '2026-01-01',
      fecha_fin: '2026-01-31',
      generar_graficas: true
    })
  });
  const data = await response.json();
  console.log(data);
}
```

### React

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function PredictorPrecios() {
  const [productos, setProductos] = useState([]);
  const [predicciones, setPredicciones] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:5000/api/productos')
      .then(res => setProductos(res.data.productos));
  }, []);

  const generar = async () => {
    const res = await axios.post('http://localhost:5000/api/predicciones', {
      productos: ['Tortilla de maíz', 'Arroz'],
      fecha_inicio: '2026-01-01',
      fecha_fin: '2026-01-31',
      generar_graficas: true
    });
    setPredicciones(res.data);
  };

  return (
    <div>
      <button onClick={generar}>Generar Predicciones</button>
      {predicciones && (
        <div>
          {predicciones.productos.map((prod, idx) => (
            <div key={idx}>
              <h3>{prod.alimento}</h3>
              <img src={`http://localhost:5000/${prod.grafica}`} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Vue.js

```vue
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const productos = ref([]);
const predicciones = ref(null);

onMounted(async () => {
  const res = await axios.get('http://localhost:5000/api/productos');
  productos.value = res.data.productos;
});

const generar = async () => {
  const res = await axios.post('http://localhost:5000/api/predicciones', {
    productos: ['Tortilla de maíz', 'Arroz'],
    fecha_inicio: '2026-01-01',
    fecha_fin: '2026-01-31',
    generar_graficas: true
  });
  predicciones.value = res.data;
};
</script>

<template>
  <div>
    <button @click="generar">Generar Predicciones</button>
    <div v-if="predicciones">
      <div v-for="prod in predicciones.productos" :key="prod.alimento">
        <h3>{{ prod.alimento }}</h3>
        <img :src="`http://localhost:5000/${prod.grafica}`" />
      </div>
    </div>
  </div>
</template>
```

---

## 📊 Estructura de Respuestas

### Mejor Día de Compra

El campo `mejor_dia_compra` puede tener dos formatos:

#### Día Único
```json
{
  "tipo": "dia_unico",
  "fecha": "2026-01-15",
  "precio_esperado": 17.43,
  "precio_min": 15.20,
  "precio_max": 19.66
}
```

#### Rango de Días
Cuando varios días consecutivos tienen precios similares (±0.5%):

```json
{
  "tipo": "rango",
  "fecha_inicio": "2026-01-12",
  "fecha_fin": "2026-01-16",
  "precio_esperado": 17.43,
  "precio_min": 15.20,
  "precio_max": 19.66,
  "dias_disponibles": 5
}
```

---

## ⚙️ Configuración CORS

El servidor Flask ya tiene CORS habilitado para permitir peticiones desde cualquier origen:

```python
from flask_cors import CORS
CORS(app)
```

Para producción, es recomendable limitar los orígenes:

```python
CORS(app, origins=["https://tu-frontend.com"])
```

---

## 🔧 Manejo de Errores

Todas las respuestas incluyen un campo `success`:

```json
{
  "success": false,
  "error": "Descripción del error"
}
```

**Códigos HTTP:**
- `200`: Éxito
- `400`: Error en los parámetros de entrada
- `404`: Recurso no encontrado
- `500`: Error interno del servidor

---

## 📁 Estructura de Archivos

```
.
├── api_predictor.py          # Lógica principal de la API
├── app_flask.py              # Servidor Flask con endpoints REST
├── ejemplos_frontend.py      # Ejemplos de integración
├── README_API.md            # Esta documentación
├── requirements.txt          # Dependencias del proyecto
├── modelos_join/            # Modelos Prophet (.pkl)
├── predicciones/            # JSONs generados
└── graficas/                # Imágenes PNG generadas
```

---

## 🎯 Características Clave

✅ **Búsqueda Inteligente**: Sugiere productos similares si no hay coincidencia exacta  
✅ **Mejor Día de Compra**: Detecta automáticamente períodos con precios óptimos  
✅ **Intervalos de Confianza**: Muestra rangos min/max para cada predicción  
✅ **Gráficas Automáticas**: Genera visualizaciones PNG de alta calidad  
✅ **JSON Export**: Toda la información disponible en formato JSON  
✅ **CORS Habilitado**: Listo para integrarse con cualquier frontend  
✅ **Validación de Datos**: Verifica fechas y parámetros automáticamente  

---

## 🚀 Despliegue en Producción

Para producción, considera usar:

- **Gunicorn** (Linux/Mac):
  ```bash
  gunicorn -w 4 -b 0.0.0.0:5000 app_flask:app
  ```

- **Waitress** (Windows):
  ```bash
  pip install waitress
  waitress-serve --host=0.0.0.0 --port=5000 app_flask:app
  ```

---

## 📞 Soporte

Para más información, consulta:
- `ejemplos_frontend.py` - Ejemplos completos de integración
- `README.md` - Documentación general del proyecto
