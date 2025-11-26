# 🚀 DEPLOY RÁPIDO - Comandos Exactos

## 1️⃣ Preparar Git (Ejecuta estos comandos)

```powershell
# Agregar archivos
git add .

# Ver qué se va a subir
git status

# Hacer commit
git commit -m "Deploy: API de predicción de precios lista"
```

---

## 2️⃣ Subir a GitHub

### Opción A: Crear nuevo repositorio
```powershell
# Ve a github.com/new y crea: predictor-precios-api
# Luego ejecuta:
git remote add origin https://github.com/TU_USUARIO/predictor-precios-api.git
git branch -M main
git push -u origin main
```

### Opción B: Usar repositorio existente
```powershell
# Si ya tienes repo Embedding_machine:
git remote set-url origin https://github.com/Asharetbe/Embedding_machine.git
git push
```

---

## 3️⃣ Deploy en Render

1. **Ve a:** [render.com](https://render.com) y registrate con GitHub

2. **Click:** "New +" → "Web Service"

3. **Conecta** tu repositorio

4. **Configura:**
   - **Name:** `predictor-precios-api`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app_flask:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2`
   - **Instance:** Free

5. **Click:** "Create Web Service"

6. **Espera** 5-10 minutos (Prophet es pesado)

7. **Tu API estará en:** `https://tu-app.onrender.com`

---

## 4️⃣ Probar

```bash
# En navegador o Postman:
https://tu-app.onrender.com/api/health
https://tu-app.onrender.com/api/productos
```

---

## 5️⃣ Compartir con Frontend

**URL:** `https://tu-app.onrender.com/api`

**Archivos:** `FRONTEND_GUIDE.md` + `README_API.md`

---

## ⚠️ Notas

- Plan Free se duerme después de 15 min sin uso
- Primera petición después de dormir tarda ~30 seg
- Auto-deploy en cada git push

---

## 📝 Archivos que se subirán

✅ api_predictor.py  
✅ app_flask.py  
✅ requirements.txt  
✅ Procfile  
✅ runtime.txt  
✅ modelos_join/ (87 archivos .pkl)  
✅ READMEs y guías  

❌ dev_testing/ (ignorado)  
❌ ejemplos_frontend.py (ignorado)  
❌ .precios/ (ignorado)  
❌ __pycache__/ (ignorado)  

---

¡Listo para deploy! 🎉
