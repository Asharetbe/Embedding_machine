# Guía de Despliegue de la API

## 🚀 Desplegar en Railway

1. Ve a [railway.app](https://railway.app)
2. Conecta tu repositorio de GitHub
3. Railway detectará automáticamente:
   - `Procfile` → Comando de inicio
   - `requirements.txt` → Dependencias Python
   - `runtime.txt` → Versión de Python

4. Variables de entorno (opcional):
   ```
   PORT=5000
   ```

5. Deploy automático. URL generada: `https://tu-app.railway.app`

---

## 🌊 Desplegar en Render

1. Ve a [render.com](https://render.com)
2. Crea un nuevo "Web Service"
3. Conecta tu repositorio
4. Configuración:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app_flask:app --bind 0.0.0.0:$PORT`
   - **Environment:** Python 3

5. Deploy. URL: `https://tu-app.onrender.com`

---

## ☁️ Desplegar en Fly.io

```bash
# Instalar Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly launch
fly deploy
```

---

## 🔧 Desplegar en VPS/Servidor Propio

### Con Nginx + Gunicorn (Ubuntu/Debian):

```bash
# 1. Instalar dependencias del sistema
sudo apt update
sudo apt install python3-pip nginx

# 2. Clonar proyecto
git clone tu-repo.git
cd ML_prediccioncostos

# 3. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Iniciar Gunicorn
gunicorn app_flask:app --bind 127.0.0.1:5000 --daemon

# 6. Configurar Nginx (crear /etc/nginx/sites-available/api)
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 7. Activar sitio
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🐳 Desplegar con Docker

Usa el `Dockerfile` incluido:

```bash
# Build
docker build -t predictor-api .

# Run
docker run -p 5000:5000 predictor-api
```

---

## 📝 Después del Deploy

1. **Obtén la URL pública:** `https://tu-api.com`

2. **Actualiza CORS** en `app_flask.py`:
   ```python
   CORS(app, origins=["https://tu-frontend.com"])
   ```

3. **Comparte con frontend:**
   - URL base: `https://tu-api.com/api`
   - Documentación: `README_API.md`
   - Ejemplos: `ejemplos_frontend.py`

4. **Endpoints disponibles:**
   - `GET /api/health`
   - `GET /api/productos`
   - `GET /api/productos/buscar?q=nombre`
   - `POST /api/predicciones`
   - `GET /api/graficas/<filename>`
   - `GET /api/predicciones/<filename>`
