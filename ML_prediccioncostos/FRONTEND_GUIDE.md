# 🎯 Entrega para Desarrollador Frontend

## 📋 Lo que necesitas compartir

### 1. **URL de la API** (después de deploy)
```
https://tu-api.railway.app/api
```

o si es local:
```
http://localhost:5000/api
```

---

## 🔗 Endpoints Disponibles

### Health Check
```javascript
GET /api/health
Response: { "status": "ok", "timestamp": "..." }
```

### Obtener Productos
```javascript
GET /api/productos
Response: {
  "success": true,
  "total": 87,
  "productos": ["Arroz", "Frijol", ...]
}
```

### Buscar Producto
```javascript
GET /api/productos/buscar?q=leche
Response: {
  "success": true,
  "encontrado": false,
  "sugerencias": ["Leche Pasteurizada Y Fresca", ...]
}
```

### Generar Predicciones
```javascript
POST /api/predicciones
Body: {
  "productos": ["Tortilla de maíz", "Arroz"],
  "fecha_inicio": "2026-01-01",
  "fecha_fin": "2026-01-31",
  "generar_graficas": true
}

Response: {
  "success": true,
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
      "predicciones": [...]
    }
  ]
}
```

### Obtener Gráfica
```javascript
GET /api/graficas/tortilla_de_maiz_2026-01-01_a_2026-01-31.png
Response: Imagen PNG
```

---

## 💻 Ejemplos de Código para Frontend

### JavaScript (Fetch)
```javascript
const API_URL = 'http://localhost:5000/api';

// Obtener productos
const productos = await fetch(`${API_URL}/productos`)
  .then(res => res.json());

// Generar predicciones
const predicciones = await fetch(`${API_URL}/predicciones`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    productos: ['Arroz', 'Frijol'],
    fecha_inicio: '2026-01-01',
    fecha_fin: '2026-01-31',
    generar_graficas: true
  })
}).then(res => res.json());
```

### React
```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [productos, setProductos] = useState([]);
  const [predicciones, setPredicciones] = useState(null);
  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    axios.get(`${API_URL}/productos`)
      .then(res => setProductos(res.data.productos));
  }, []);

  const generar = async () => {
    const res = await axios.post(`${API_URL}/predicciones`, {
      productos: ['Arroz'],
      fecha_inicio: '2026-01-01',
      fecha_fin: '2026-01-31',
      generar_graficas: true
    });
    setPredicciones(res.data);
  };

  return (
    <div>
      <button onClick={generar}>Generar</button>
      {predicciones?.productos?.map(prod => (
        <div key={prod.alimento}>
          <h3>{prod.alimento}</h3>
          <img src={`http://localhost:5000/${prod.grafica}`} />
          <p>Mejor día: {prod.mejor_dia_compra.fecha}</p>
          <p>Precio: ${prod.mejor_dia_compra.precio_esperado}</p>
        </div>
      ))}
    </div>
  );
}
```

### Vue
```vue
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';
const productos = ref([]);
const predicciones = ref(null);

onMounted(async () => {
  const res = await axios.get(`${API_URL}/productos`);
  productos.value = res.data.productos;
});

const generar = async () => {
  const res = await axios.post(`${API_URL}/predicciones`, {
    productos: ['Arroz'],
    fecha_inicio: '2026-01-01',
    fecha_fin: '2026-01-31',
    generar_graficas: true
  });
  predicciones.value = res.data;
};
</script>

<template>
  <button @click="generar">Generar</button>
  <div v-for="prod in predicciones?.productos" :key="prod.alimento">
    <h3>{{ prod.alimento }}</h3>
    <img :src="`http://localhost:5000/${prod.grafica}`" />
  </div>
</template>
```

---

## 📁 Archivos a Compartir

✅ `README_API.md` - Documentación completa  
✅ `ejemplos_frontend.py` - Ejemplos de React/Vue/JavaScript  
✅ `FRONTEND_GUIDE.md` - Este archivo (guía rápida)  
✅ URL de la API desplegada

---

## 🔐 CORS

La API ya tiene CORS habilitado para desarrollo:
```python
CORS(app)  # Permite todas las origenes
```

Para producción, limitar a tu dominio:
```python
CORS(app, origins=["https://tu-frontend.com"])
```

---

## 🐛 Testing

Puedes probar la API con:

**Browser:**
```
http://localhost:5000/api/health
http://localhost:5000/api/productos
```

**Postman/Insomnia:**
Importa la colección desde `README_API.md`

**cURL:**
```bash
curl http://localhost:5000/api/productos
```

---

## 📞 Soporte

Si el frontend tiene dudas:
1. Ver `README_API.md` para documentación completa
2. Ver `ejemplos_frontend.py` para código de ejemplo
3. Ejecutar `test_api.py` para ver respuestas reales
