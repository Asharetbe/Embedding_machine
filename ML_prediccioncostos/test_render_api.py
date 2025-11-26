"""
Script de prueba para API desplegada en Render
"""

import requests
import json

# URL de tu API en Render
API_BASE_URL = 'https://price-predictor-api-02g8.onrender.com/api'

print("="*70)
print("🧪 PRUEBAS DE API EN RENDER")
print("="*70)

# 1. Health Check
print("\n1️⃣ HEALTH CHECK")
print("-" * 70)
try:
    response = requests.get(f'{API_BASE_URL}/health')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ API funcionando correctamente")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Error: Status {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. Obtener Productos
print("\n\n2️⃣ OBTENER LISTA DE PRODUCTOS")
print("-" * 70)
try:
    response = requests.get(f'{API_BASE_URL}/productos')
    data = response.json()
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Total productos: {data['total']}")
        print(f"Primeros 10 productos:")
        for i, prod in enumerate(data['productos'][:10], 1):
            print(f"  {i}. {prod}")
except Exception as e:
    print(f"❌ Error: {e}")

# 3. Buscar Producto (Exacto)
print("\n\n3️⃣ BUSCAR PRODUCTO - 'Arroz' (Exacto)")
print("-" * 70)
try:
    response = requests.get(f'{API_BASE_URL}/productos/buscar?q=Arroz')
    data = response.json()
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        if data['encontrado']:
            print(f"✅ Producto encontrado: {data['producto_exacto']}")
        else:
            print(f"⚠️ No encontrado, sugerencias: {data['sugerencias']}")
except Exception as e:
    print(f"❌ Error: {e}")

# 4. Buscar Producto (Con sugerencias)
print("\n\n4️⃣ BUSCAR PRODUCTO - 'leche' (Con sugerencias)")
print("-" * 70)
try:
    response = requests.get(f'{API_BASE_URL}/productos/buscar?q=leche')
    data = response.json()
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        if data['encontrado']:
            print(f"✅ Encontrado: {data['producto_exacto']}")
        else:
            print(f"⚠️ No encontrado exacto. Sugerencias:")
            for i, sug in enumerate(data['sugerencias'], 1):
                print(f"  {i}. {sug}")
except Exception as e:
    print(f"❌ Error: {e}")

# 5. Generar Predicciones
print("\n\n5️⃣ GENERAR PREDICCIONES")
print("-" * 70)
print("Solicitando predicciones para:")
print("  • Arroz")
print("  • Frijol")
print("Del 2026-01-01 al 2026-01-10")
print("\n⏳ Generando predicciones (puede tardar ~30 seg en primera petición)...")

try:
    payload = {
        "productos": ["Arroz", "Frijol"],
        "fecha_inicio": "2026-01-01",
        "fecha_fin": "2026-01-10",
        "generar_graficas": True
    }
    
    response = requests.post(
        f'{API_BASE_URL}/predicciones',
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=120  # 2 minutos de timeout
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Predicciones generadas exitosamente!")
        print(f"\n📊 Resumen:")
        print(f"  • Fecha consulta: {data['fecha_consulta']}")
        print(f"  • Período: {data['periodo']['inicio']} al {data['periodo']['fin']}")
        print(f"  • Productos procesados: {data['productos_procesados']}")
        
        print(f"\n🛒 MEJORES DÍAS PARA COMPRAR:")
        print("-" * 70)
        for prod in data['productos']:
            print(f"\n📦 {prod['alimento']}")
            mejor = prod['mejor_dia_compra']
            
            if mejor['tipo'] == 'rango':
                print(f"  📅 Período: {mejor['fecha_inicio']} al {mejor['fecha_fin']}")
                print(f"  💰 Precio: ${mejor['precio_esperado']}")
                print(f"  🗓️  Días disponibles: {mejor['dias_disponibles']}")
            else:
                print(f"  📅 Fecha: {mejor['fecha']}")
                print(f"  💰 Precio: ${mejor['precio_esperado']}")
            
            print(f"  📝 Total predicciones: {prod['total_registros']}")
            
            if 'grafica' in prod:
                url_grafica = f"https://price-predictor-api-02g8.onrender.com/{prod['grafica']}"
                print(f"  📈 Gráfica: {url_grafica}")
        
        # Mostrar algunas predicciones
        if data['productos']:
            primer_prod = data['productos'][0]
            print(f"\n\n📋 PREDICCIONES DETALLADAS - {primer_prod['alimento']}")
            print("-" * 70)
            print(f"{'Fecha':<15} {'Precio':<12} {'Mín':<12} {'Máx':<12}")
            print("-" * 70)
            for pred in primer_prod['predicciones']:
                print(f"{pred['fecha']:<15} ${pred['precio_esperado']:<11.2f} "
                      f"${pred['precio_min']:<11.2f} ${pred['precio_max']:<11.2f}")
    else:
        print(f"❌ Error: {response.text}")
        
except requests.exceptions.Timeout:
    print(f"⏰ Timeout: La API está procesando (es normal en primera petición)")
    print(f"   Espera ~30-60 segundos y vuelve a intentar")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n\n" + "="*70)
print("✅ PRUEBAS COMPLETADAS")
print("="*70)
print("\n🌐 Tu API está disponible en:")
print(f"   {API_BASE_URL}")
print("\n💡 Endpoints:")
print(f"   • GET  {API_BASE_URL}/health")
print(f"   • GET  {API_BASE_URL}/productos")
print(f"   • GET  {API_BASE_URL}/productos/buscar?q=nombre")
print(f"   • POST {API_BASE_URL}/predicciones")
print("="*70)
