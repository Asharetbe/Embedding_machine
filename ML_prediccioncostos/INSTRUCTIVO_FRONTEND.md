# Guía de integración - API de predicción de precios

---

## Información básica

### URL Base de la API
```
https://price-predictor-api-02g8.onrender.com/api
```

### Características
- 87 productos disponibles con modelos de predicción
- Predicciones diarias con intervalos de confianza
- Búsqueda inteligente de productos
- Detección automática del mejor día/período para comprar
- Gráficas PNG de alta calidad
- CORS habilitado

---

## 🎯 Endpoints disponibles

### 1. Health Check
Verifica que la API está funcionando.

```javascript
GET /api/health
```

**Respuesta:**
```json
{
  "status": "ok",
  "service": "Predictor de Precios API",
  "timestamp": "2025-11-25T20:30:00"
}
```

---

### 2. Obtener Lista de Productos
Retorna todos los productos disponibles (87 productos).

```javascript
GET /api/productos
```

**Respuesta:**
```json
{
  "success": true,
  "total": 87,
  "productos": [
    "Aceites Y Grasas Vegetales Comestibles",
    "Agua Embotellada",
    "Aguacate",
    "Arroz",
    "Frijol",
    "Huevo",
    "Leche Pasteurizada Y Fresca",
    "Tortilla de maíz",
    ...
  ]
}
```

**Ejemplo de uso:**
```javascript
const API_URL = 'https://price-predictor-api-02g8.onrender.com/api';

async function obtenerProductos() {
  const response = await fetch(`${API_URL}/productos`);
  const data = await response.json();
  
  if (data.success) {
    return data.productos; // Array de 87 productos
  }
}
```

---

### 3. Buscar Producto
Busca un producto específico. Si no encuentra coincidencia exacta, retorna sugerencias.

```javascript
GET /api/productos/buscar?q={nombre}
```

**Parámetros:**
- `q` (requerido): Nombre del producto a buscar

**Ejemplo - Búsqueda exacta:**
```javascript
GET /api/productos/buscar?q=Arroz
```
**Respuesta:**
```json
{
  "success": true,
  "encontrado": true,
  "producto_exacto": "Arroz",
  "sugerencias": []
}
```

**Ejemplo - Con sugerencias:**
```javascript
GET /api/productos/buscar?q=leche
```
**Respuesta:**
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

**Ejemplo de uso:**
```javascript
async function buscarProducto(nombre) {
  const response = await fetch(
    `${API_URL}/productos/buscar?q=${encodeURIComponent(nombre)}`
  );
  const data = await response.json();
  
  if (data.encontrado) {
    return data.producto_exacto;
  } else {
    return data.sugerencias; // Mostrar opciones al usuario
  }
}
```

---

### 4. Generar predicciones  (PRINCIPAL)
Genera predicciones de precios para uno o más productos en un rango de fechas.

```javascript
POST /api/predicciones
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "productos": ["Arroz", "Frijol", "Huevo"],
  "fecha_inicio": "2026-01-01",
  "fecha_fin": "2026-01-31",
  "generar_graficas": true
}
```

**Parámetros:**
- `productos` (array, requerido): Lista de nombres de productos
- `fecha_inicio` (string, requerido): Fecha inicial formato YYYY-MM-DD
- `fecha_fin` (string, requerido): Fecha final formato YYYY-MM-DD
- `generar_graficas` (boolean, opcional): Si se generan gráficas PNG. Default: true

**Respuesta completa:**
```json
{
  "success": true,
  "fecha_consulta": "2025-11-25 20:30:00",
  "periodo": {
    "inicio": "2026-01-01",
    "fin": "2026-01-31"
  },
  "total_productos": 3,
  "productos_procesados": 3,
  "productos_con_error": 0,
  "productos": [
    {
      "alimento": "Arroz",
      "fecha_inicio": "2026-01-01",
      "fecha_fin": "2026-01-31",
      "unidad": "kg/litro",
      "total_registros": 31,
      "mejor_dia_compra": {
        "tipo": "rango",
        "fecha_inicio": "2026-01-09",
        "fecha_fin": "2026-01-13",
        "precio_esperado": 26.24,
        "precio_min": 18.69,
        "precio_max": 33.87,
        "dias_disponibles": 5
      },
      "grafica": "./graficas/arroz_2026-01-01_a_2026-01-31.png",
      "predicciones": [
        {
          "fecha": "2026-01-01",
          "precio_esperado": 26.89,
          "precio_min": 19.21,
          "precio_max": 34.65
        },
        {
          "fecha": "2026-01-02",
          "precio_esperado": 26.78,
          "precio_min": 19.10,
          "precio_max": 34.52
        },
        ...
      ]
    },
    ...
  ],
  "ruta_json": "./predicciones/predicciones_2026-01-01_a_2026-01-31.json"
}
```

**Ejemplo de uso completo:**
```javascript
async function generarPredicciones(productos, fechaInicio, fechaFin) {
  const response = await fetch(`${API_URL}/predicciones`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      productos: productos,
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
      generar_graficas: true
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    return data;
  } else {
    throw new Error(data.error);
  }
}

// Usar la función
generarPredicciones(['Arroz', 'Frijol'], '2026-01-01', '2026-01-31')
  .then(data => {
    console.log('Predicciones:', data);
    
    // Iterar sobre cada producto
    data.productos.forEach(producto => {
      console.log(`Producto: ${producto.alimento}`);
      console.log(`Mejor día: ${producto.mejor_dia_compra.fecha_inicio}`);
      console.log(`Precio: $${producto.mejor_dia_compra.precio_esperado}`);
    });
  })
  .catch(error => console.error('Error:', error));
```

---

### 5. Obtener Gráfica
Retorna la imagen PNG de una gráfica generada.

```javascript
GET /api/graficas/{filename}
```

**Ejemplo:**
```javascript
GET /api/graficas/arroz_2026-01-01_a_2026-01-31.png
```

**Uso en HTML:**
```html
<img src="https://price-predictor-api-02g8.onrender.com/graficas/arroz_2026-01-01_a_2026-01-31.png" 
     alt="Predicción de Arroz" />
```

**O dinámicamente:**
```javascript
// Después de recibir la predicción
const producto = data.productos[0];
const urlGrafica = `https://price-predictor-api-02g8.onrender.com/${producto.grafica}`;

// Mostrar en img
document.getElementById('grafica').src = urlGrafica;
```

---

## Entendiendo el Campo "mejor_dia_compra"

El sistema detecta automáticamente el mejor momento para comprar. Puede retornar 2 tipos:

### Tipo 1: Día Único
Cuando hay un solo día con el precio más bajo:

```json
{
  "tipo": "dia_unico",
  "fecha": "2026-01-15",
  "precio_esperado": 30.52,
  "precio_min": 16.99,
  "precio_max": 44.51
}
```

**En tu frontend:**
```javascript
if (mejor.tipo === 'dia_unico') {
  mostrarMensaje(`Mejor día: ${mejor.fecha} - $${mejor.precio_esperado}`);
}
```

### Tipo 2: Rango de Días
Cuando varios días consecutivos tienen precios similares (±0.5%):

```json
{
  "tipo": "rango",
  "fecha_inicio": "2026-01-09",
  "fecha_fin": "2026-01-13",
  "precio_esperado": 26.24,
  "precio_min": 18.69,
  "precio_max": 33.87,
  "dias_disponibles": 5
}
```

**En tu frontend:**
```javascript
if (mejor.tipo === 'rango') {
  mostrarMensaje(
    `Mejor período: ${mejor.fecha_inicio} al ${mejor.fecha_fin} ` +
    `(${mejor.dias_disponibles} días) - $${mejor.precio_esperado}`
  );
}
```

---

## Ejemplos completos por framework

### React (con Hooks)

```jsx
import { useState, useEffect } from 'react';

const API_URL = 'https://price-predictor-api-02g8.onrender.com/api';

function PredictorPrecios() {
  const [productos, setProductos] = useState([]);
  const [productosSeleccionados, setProductosSeleccionados] = useState([]);
  const [fechaInicio, setFechaInicio] = useState('2026-01-01');
  const [fechaFin, setFechaFin] = useState('2026-01-31');
  const [predicciones, setPredicciones] = useState(null);
  const [loading, setLoading] = useState(false);

  // Cargar productos al iniciar
  useEffect(() => {
    fetch(`${API_URL}/productos`)
      .then(res => res.json())
      .then(data => setProductos(data.productos));
  }, []);

  // Generar predicciones
  const handleGenerar = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/predicciones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          productos: productosSeleccionados,
          fecha_inicio: fechaInicio,
          fecha_fin: fechaFin,
          generar_graficas: true
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setPredicciones(data);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Predictor de Precios</h1>
      
      {/* Selector de productos */}
      <select onChange={(e) => setProductosSeleccionados([...productosSeleccionados, e.target.value])}>
        <option value="">Seleccionar producto</option>
        {productos.map(prod => (
          <option key={prod} value={prod}>{prod}</option>
        ))}
      </select>

      {/* Fechas */}
      <input 
        type="date" 
        value={fechaInicio}
        onChange={(e) => setFechaInicio(e.target.value)}
      />
      <input 
        type="date" 
        value={fechaFin}
        onChange={(e) => setFechaFin(e.target.value)}
      />

      {/* Botón generar */}
      <button onClick={handleGenerar} disabled={loading}>
        {loading ? 'Generando...' : 'Generar Predicciones'}
      </button>

      {/* Resultados */}
      {predicciones && (
        <div>
          {predicciones.productos.map(prod => (
            <div key={prod.alimento}>
              <h2>{prod.alimento}</h2>
              
              {/* Mejor día */}
              <div>
                <strong>Mejor momento para comprar:</strong>
                {prod.mejor_dia_compra.tipo === 'rango' ? (
                  <p>
                    Del {prod.mejor_dia_compra.fecha_inicio} 
                    al {prod.mejor_dia_compra.fecha_fin} 
                    - ${prod.mejor_dia_compra.precio_esperado}
                  </p>
                ) : (
                  <p>
                    {prod.mejor_dia_compra.fecha} 
                    - ${prod.mejor_dia_compra.precio_esperado}
                  </p>
                )}
              </div>

              {/* Gráfica */}
              <img 
                src={`https://price-predictor-api-02g8.onrender.com/${prod.grafica}`}
                alt={`Gráfica de ${prod.alimento}`}
              />

              {/* Tabla de predicciones */}
              <table>
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Precio</th>
                    <th>Mín</th>
                    <th>Máx</th>
                  </tr>
                </thead>
                <tbody>
                  {prod.predicciones.map(pred => (
                    <tr key={pred.fecha}>
                      <td>{pred.fecha}</td>
                      <td>${pred.precio_esperado}</td>
                      <td>${pred.precio_min}</td>
                      <td>${pred.precio_max}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PredictorPrecios;
```

---

### Vue 3 (Composition API)

```vue
<template>
  <div class="predictor">
    <h1>Predictor de Precios</h1>

    <!-- Selector de productos -->
    <select @change="agregarProducto($event.target.value)">
      <option value="">Seleccionar producto</option>
      <option v-for="prod in productos" :key="prod" :value="prod">
        {{ prod }}
      </option>
    </select>

    <!-- Productos seleccionados -->
    <div v-if="productosSeleccionados.length > 0">
      <span v-for="(prod, idx) in productosSeleccionados" :key="idx">
        {{ prod }}
        <button @click="quitarProducto(idx)">×</button>
      </span>
    </div>

    <!-- Fechas -->
    <input v-model="fechaInicio" type="date" />
    <input v-model="fechaFin" type="date" />

    <!-- Generar -->
    <button @click="generarPredicciones" :disabled="loading">
      {{ loading ? 'Generando...' : 'Generar Predicciones' }}
    </button>

    <!-- Resultados -->
    <div v-if="predicciones">
      <div v-for="prod in predicciones.productos" :key="prod.alimento">
        <h2>{{ prod.alimento }}</h2>
        
        <!-- Mejor día -->
        <div>
          <strong>Mejor momento:</strong>
          <p v-if="prod.mejor_dia_compra.tipo === 'rango'">
            Del {{ prod.mejor_dia_compra.fecha_inicio }} 
            al {{ prod.mejor_dia_compra.fecha_fin }}
            - ${{ prod.mejor_dia_compra.precio_esperado }}
          </p>
          <p v-else>
            {{ prod.mejor_dia_compra.fecha }} 
            - ${{ prod.mejor_dia_compra.precio_esperado }}
          </p>
        </div>

        <!-- Gráfica -->
        <img 
          :src="`https://price-predictor-api-02g8.onrender.com/${prod.grafica}`"
          :alt="`Gráfica de ${prod.alimento}`"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const API_URL = 'https://price-predictor-api-02g8.onrender.com/api';

const productos = ref([]);
const productosSeleccionados = ref([]);
const fechaInicio = ref('2026-01-01');
const fechaFin = ref('2026-01-31');
const predicciones = ref(null);
const loading = ref(false);

onMounted(async () => {
  const res = await fetch(`${API_URL}/productos`);
  const data = await res.json();
  productos.value = data.productos;
});

const agregarProducto = (producto) => {
  if (producto && !productosSeleccionados.value.includes(producto)) {
    productosSeleccionados.value.push(producto);
  }
};

const quitarProducto = (idx) => {
  productosSeleccionados.value.splice(idx, 1);
};

const generarPredicciones = async () => {
  loading.value = true;
  try {
    const res = await fetch(`${API_URL}/predicciones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        productos: productosSeleccionados.value,
        fecha_inicio: fechaInicio.value,
        fecha_fin: fechaFin.value,
        generar_graficas: true
      })
    });
    
    const data = await res.json();
    if (data.success) {
      predicciones.value = data;
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    loading.value = false;
  }
};
</script>
```

---

### JavaScript Vanilla

```javascript
const API_URL = 'https://price-predictor-api-02g8.onrender.com/api';

// Cargar productos al iniciar
async function cargarProductos() {
  const response = await fetch(`${API_URL}/productos`);
  const data = await response.json();
  
  const select = document.getElementById('productos-select');
  data.productos.forEach(producto => {
    const option = document.createElement('option');
    option.value = producto;
    option.textContent = producto;
    select.appendChild(option);
  });
}

// Generar predicciones
async function generarPredicciones() {
  const productos = Array.from(
    document.getElementById('productos-select').selectedOptions
  ).map(opt => opt.value);
  
  const fechaInicio = document.getElementById('fecha-inicio').value;
  const fechaFin = document.getElementById('fecha-fin').value;
  
  const loadingDiv = document.getElementById('loading');
  loadingDiv.style.display = 'block';
  
  try {
    const response = await fetch(`${API_URL}/predicciones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        productos: productos,
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        generar_graficas: true
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      mostrarResultados(data);
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    loadingDiv.style.display = 'none';
  }
}

// Mostrar resultados
function mostrarResultados(data) {
  const container = document.getElementById('resultados');
  container.innerHTML = '';
  
  data.productos.forEach(producto => {
    const div = document.createElement('div');
    div.className = 'producto-card';
    
    const mejor = producto.mejor_dia_compra;
    const textoMejorDia = mejor.tipo === 'rango'
      ? `Del ${mejor.fecha_inicio} al ${mejor.fecha_fin} - $${mejor.precio_esperado}`
      : `${mejor.fecha} - $${mejor.precio_esperado}`;
    
    div.innerHTML = `
      <h2>${producto.alimento}</h2>
      <p><strong>Mejor momento:</strong> ${textoMejorDia}</p>
      <img src="https://price-predictor-api-02g8.onrender.com/${producto.grafica}" 
           alt="Gráfica de ${producto.alimento}" />
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Precio</th>
            <th>Mín</th>
            <th>Máx</th>
          </tr>
        </thead>
        <tbody>
          ${producto.predicciones.map(pred => `
            <tr>
              <td>${pred.fecha}</td>
              <td>$${pred.precio_esperado}</td>
              <td>$${pred.precio_min}</td>
              <td>$${pred.precio_max}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
    
    container.appendChild(div);
  });
}

// Inicializar
cargarProductos();
```

---

## Consideraciones importantes

### 1. Primera Petición (Cold Start)
La API usa el plan Free de Render, que se "duerme" después de 15 min sin uso.

**La primera petición después de dormir puede tardar 30-60 segundos.**

```javascript
// Mostrar mensaje de carga al usuario
setLoading(true);
setMensaje('Iniciando servidor... esto puede tardar hasta 1 minuto');

try {
  const response = await fetch(url, { timeout: 120000 }); // 2 min timeout
  // ...
} catch (error) {
  if (error.name === 'TimeoutError') {
    setMensaje('El servidor está iniciando. Intenta de nuevo en 30 segundos.');
  }
}
```

### 2. Timeout recomendado
```javascript
// Para predicciones, usa timeout largo
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minutos

try {
  const response = await fetch(url, {
    signal: controller.signal,
    // ...
  });
} catch (error) {
  if (error.name === 'AbortError') {
    console.log('Timeout: La API está procesando');
  }
} finally {
  clearTimeout(timeoutId);
}
```

### Validación de fechas
```javascript
// Validar formato YYYY-MM-DD
function validarFecha(fecha) {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  if (!regex.test(fecha)) return false;
  
  const date = new Date(fecha);
  return date instanceof Date && !isNaN(date);
}

// Validar que fecha_fin > fecha_inicio
function validarRango(inicio, fin) {
  return new Date(fin) > new Date(inicio);
}
```

### Manejo de errores
```javascript
try {
  const response = await fetch(url, options);
  const data = await response.json();
  
  if (!data.success) {
    // Mostrar error al usuario
    mostrarError(data.error || 'Error desconocido');
  }
} catch (error) {
  console.error('Error de conexión:', error);
  mostrarError('No se pudo conectar con la API');
}
```

---

## Ejemplo de UI completa (HTML + CSS + JS)

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Predictor de Precios</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #f5f7fa;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      padding: 30px;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h1 {
      color: #2c3e50;
      margin-bottom: 30px;
      text-align: center;
    }
    .form-group {
      margin-bottom: 20px;
    }
    label {
      display: block;
      margin-bottom: 5px;
      color: #34495e;
      font-weight: 600;
    }
    input, select {
      width: 100%;
      padding: 10px;
      border: 2px solid #e0e6ed;
      border-radius: 5px;
      font-size: 14px;
    }
    button {
      background: #3498db;
      color: white;
      padding: 12px 30px;
      border: none;
      border-radius: 5px;
      font-size: 16px;
      cursor: pointer;
      width: 100%;
      margin-top: 10px;
    }
    button:hover { background: #2980b9; }
    button:disabled {
      background: #95a5a6;
      cursor: not-allowed;
    }
    .loading {
      text-align: center;
      padding: 20px;
      color: #7f8c8d;
    }
    .producto-card {
      margin: 30px 0;
      padding: 20px;
      border: 2px solid #ecf0f1;
      border-radius: 8px;
    }
    .producto-card h2 {
      color: #2c3e50;
      margin-bottom: 15px;
    }
    .mejor-dia {
      background: #e8f8f5;
      padding: 15px;
      border-radius: 5px;
      margin: 15px 0;
      border-left: 4px solid #1abc9c;
    }
    .mejor-dia strong {
      color: #16a085;
    }
    img {
      width: 100%;
      max-width: 800px;
      height: auto;
      margin: 20px 0;
      border-radius: 5px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #ecf0f1;
    }
    th {
      background: #34495e;
      color: white;
      font-weight: 600;
    }
    tr:hover { background: #f8f9fa; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🛒 Predictor de Precios de Alimentos</h1>
    
    <div class="form-group">
      <label for="productos-select">Selecciona productos:</label>
      <select id="productos-select" multiple size="5">
        <option value="">Cargando...</option>
      </select>
    </div>
    
    <div class="form-group">
      <label for="fecha-inicio">Fecha de inicio:</label>
      <input type="date" id="fecha-inicio" value="2026-01-01">
    </div>
    
    <div class="form-group">
      <label for="fecha-fin">Fecha final:</label>
      <input type="date" id="fecha-fin" value="2026-01-31">
    </div>
    
    <button onclick="generarPredicciones()" id="btn-generar">
      Generar Predicciones
    </button>
    
    <div id="loading" class="loading" style="display: none;">
      Generando predicciones... esto puede tardar hasta 1 minuto
    </div>
    
    <div id="resultados"></div>
  </div>

  <script>
    const API_URL = 'https://price-predictor-api-02g8.onrender.com/api';

    // Cargar productos
    async function cargarProductos() {
      const response = await fetch(`${API_URL}/productos`);
      const data = await response.json();
      
      const select = document.getElementById('productos-select');
      select.innerHTML = '';
      
      data.productos.forEach(producto => {
        const option = document.createElement('option');
        option.value = producto;
        option.textContent = producto;
        select.appendChild(option);
      });
    }

    // Generar predicciones
    async function generarPredicciones() {
      const select = document.getElementById('productos-select');
      const productos = Array.from(select.selectedOptions).map(opt => opt.value);
      
      if (productos.length === 0) {
        alert('Selecciona al menos un producto');
        return;
      }
      
      const fechaInicio = document.getElementById('fecha-inicio').value;
      const fechaFin = document.getElementById('fecha-fin').value;
      
      const loadingDiv = document.getElementById('loading');
      const btnGenerar = document.getElementById('btn-generar');
      
      loadingDiv.style.display = 'block';
      btnGenerar.disabled = true;
      
      try {
        const response = await fetch(`${API_URL}/predicciones`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            productos: productos,
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin,
            generar_graficas: true
          })
        });
        
        const data = await response.json();
        
        if (data.success) {
          mostrarResultados(data);
        } else {
          alert('Error: ' + data.error);
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error al conectar con la API');
      } finally {
        loadingDiv.style.display = 'none';
        btnGenerar.disabled = false;
      }
    }

    // Mostrar resultados
    function mostrarResultados(data) {
      const container = document.getElementById('resultados');
      container.innerHTML = '';
      
      data.productos.forEach(producto => {
        const div = document.createElement('div');
        div.className = 'producto-card';
        
        const mejor = producto.mejor_dia_compra;
        const textoMejorDia = mejor.tipo === 'rango'
          ? `Del <strong>${mejor.fecha_inicio}</strong> al <strong>${mejor.fecha_fin}</strong> (${mejor.dias_disponibles} días) - <strong>$${mejor.precio_esperado.toFixed(2)}</strong>`
          : `<strong>${mejor.fecha}</strong> - <strong>$${mejor.precio_esperado.toFixed(2)}</strong>`;
        
        div.innerHTML = `
          <h2>📦 ${producto.alimento}</h2>
          <div class="mejor-dia">
            <strong>🛒 Mejor momento para comprar:</strong><br>
            ${textoMejorDia}
          </div>
          <img src="https://price-predictor-api-02g8.onrender.com/${producto.grafica}" 
               alt="Gráfica de ${producto.alimento}" />
          <details>
            <summary style="cursor: pointer; font-weight: 600; margin: 20px 0;">
              Ver ${producto.predicciones.length} predicciones detalladas
            </summary>
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Precio Esperado</th>
                  <th>Precio Mín</th>
                  <th>Precio Máx</th>
                </tr>
              </thead>
              <tbody>
                ${producto.predicciones.map(pred => `
                  <tr>
                    <td>${pred.fecha}</td>
                    <td>$${pred.precio_esperado.toFixed(2)}</td>
                    <td>$${pred.precio_min.toFixed(2)}</td>
                    <td>$${pred.precio_max.toFixed(2)}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </details>
        `;
        
        container.appendChild(div);
      });
    }

    // Inicializar
    cargarProductos();
  </script>
</body>
</html>
```


