# 🚀 Deploy en Render - Guía Paso a Paso

## Paso 1: Subir a GitHub

### 1.1 Crear repositorio en GitHub
1. Ve a [github.com](https://github.com)
2. Click en "+" → "New repository"
3. Nombre: `predictor-precios-api` (o el que prefieras)
4. Descripción: "API de predicción de precios de alimentos"
5. **Público o Privado** (Render funciona con ambos)
6. **NO inicialices** con README, .gitignore, o licencia
7. Click "Create repository"

### 1.2 Subir tu código
Ejecuta estos comandos en tu terminal:

```powershell
# Inicializar git (si no lo has hecho)
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "Initial commit - API de predicción de precios"

# Conectar con GitHub (reemplaza con tu URL)
git remote add origin https://github.com/TuUsuario/predictor-precios-api.git

# Subir código
git branch -M main
git push -u origin main
```

---

## Paso 2: Deploy en Render

### 2.1 Crear cuenta en Render
1. Ve a [render.com](https://render.com)
2. Click "Get Started"
3. Regístrate con GitHub (recomendado) o email

### 2.2 Crear Web Service
1. En el dashboard, click **"New +"** → **"Web Service"**
2. Click **"Connect account"** para conectar GitHub
3. Busca y selecciona tu repositorio `predictor-precios-api`
4. Click **"Connect"**

### 2.3 Configurar el servicio

**Configuración básica:**
- **Name:** `predictor-precios-api` (o el que prefieras)
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** (dejar vacío)
- **Runtime:** `Python 3`
- **Build Command:** 
  ```
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```
  gunicorn app_flask:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2
  ```

**Plan:**
- Selecciona **"Free"** (0$/mes, suficiente para empezar)
- Nota: El plan free se duerme después de 15 min de inactividad

### 2.4 Variables de Entorno (Opcional)
En "Environment Variables" puedes agregar:
- `PYTHON_VERSION`: `3.11.4`
- Otras variables si las necesitas

### 2.5 Deploy
1. Click **"Create Web Service"**
2. Render comenzará a construir y desplegar tu API
3. Verás los logs en tiempo real
4. El proceso toma **5-10 minutos** la primera vez

---

## Paso 3: Verificar el Deploy

### 3.1 Obtener la URL
Una vez completado, verás:
- **URL pública:** `https://predictor-precios-api.onrender.com`
- Estado: **"Live"** 🟢

### 3.2 Probar la API
Abre en tu navegador:
```
https://predictor-precios-api.onrender.com/api/health
```

Deberías ver:
```json
{
  "status": "ok",
  "service": "Predictor de Precios API",
  "timestamp": "..."
}
```

### 3.3 Probar todos los endpoints
```
https://tu-api.onrender.com/api/productos
https://tu-api.onrender.com/api/productos/buscar?q=arroz
```

---

## Paso 4: Compartir con Frontend

### 4.1 URL Base
Comparte esta URL con el desarrollador frontend:
```
https://predictor-precios-api.onrender.com/api
```

### 4.2 Archivos a compartir
- `FRONTEND_GUIDE.md` - Guía de integración
- `README_API.md` - Documentación completa
- `ejemplos_frontend.py` - Código de ejemplo
- **URL de la API** en producción

### 4.3 Ejemplo de uso desde frontend
```javascript
const API_URL = 'https://predictor-precios-api.onrender.com/api';

// Funciona igual que en local, solo cambias la URL
fetch(`${API_URL}/productos`)
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 🔧 Problemas Comunes

### Error: "Build failed"
**Solución:** Verifica que `requirements.txt` esté correcto
```powershell
pip install -r requirements.txt
```

### Error: "Port binding"
**Solución:** Ya está configurado con `$PORT` en el start command

### Error: "Memory limit"
**Solución:** En plan free hay límite de 512MB RAM
- Reduce workers: `--workers 1`
- O upgradea a plan Starter ($7/mes con 512MB garantizados)

### API muy lenta
**Plan free se duerme después de 15 min sin uso**
- Primera petición tarda ~30 seg (cold start)
- Solución: Plan Starter mantiene API siempre activa

---

## 🔄 Actualizar el Deploy

### Cuando hagas cambios en el código:

```powershell
# Hacer cambios en tu código

# Commit
git add .
git commit -m "Descripción de los cambios"

# Push
git push origin main
```

**Render detecta el push automáticamente y redespliega en 2-3 minutos**

---

## 📊 Monitoreo

En el dashboard de Render puedes ver:
- **Logs en tiempo real**
- **Uso de CPU/Memoria**
- **Peticiones HTTP**
- **Errores y excepciones**

---

## 💰 Planes de Render

### Free Plan (Actual)
- ✅ HTTPS incluido
- ✅ Auto-deploy desde GitHub
- ✅ 750 horas/mes
- ⚠️ Se duerme después de 15 min inactividad
- ⚠️ 512MB RAM

### Starter Plan ($7/mes)
- ✅ Todo del Free
- ✅ Siempre activo (no se duerme)
- ✅ 512MB RAM garantizados
- ✅ Sin límite de horas

---

## ✅ Checklist Final

- [ ] Código subido a GitHub
- [ ] Web Service creado en Render
- [ ] Deploy exitoso (status: Live 🟢)
- [ ] URL funciona: `/api/health`
- [ ] URL compartida con frontend
- [ ] `FRONTEND_GUIDE.md` enviado al frontend
- [ ] CORS configurado para el dominio del frontend

---

## 🎯 Resultado Final

Tu API estará disponible globalmente en:
```
https://predictor-precios-api.onrender.com/api
```

El frontend puede consumirla desde cualquier lugar:
- React
- Vue
- Angular
- Aplicación móvil
- Cualquier cliente HTTP

🎉 ¡Listo para producción!
