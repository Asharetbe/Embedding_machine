"""
Ejemplo simple de consulta de predicciones de precios
"""

import requests
import json

# URL de tu API
API_URL = 'https://price-predictor-api-02g8.onrender.com/api'

# Parámetros de la consulta
consulta = {
    "productos": ["Tortilla de maíz", "Arroz", "Frijol"],
    "fecha_inicio": "2026-01-01",
    "fecha_fin": "2026-01-20",
    "generar_graficas": True
}

print("🔄 Enviando consulta a la API...")
print(f"   Productos: {', '.join(consulta['productos'])}")
print(f"   Período: {consulta['fecha_inicio']} al {consulta['fecha_fin']}")
print("\n⏳ Esperando respuesta (puede tardar 30-60 seg)...\n")

try:
    # Hacer la petición
    response = requests.post(
        f'{API_URL}/predicciones',
        json=consulta,
        timeout=120
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ ¡Predicciones recibidas exitosamente!\n")
        print("="*80)
        
        # Mostrar información por producto
        for producto in data['productos']:
            print(f"\n📦 {producto['alimento'].upper()}")
            print("-"*80)
            
            # Mejor día para comprar
            mejor = producto['mejor_dia_compra']
            print(f"\n🛒 MEJOR MOMENTO PARA COMPRAR:")
            
            if mejor['tipo'] == 'rango':
                print(f"   📅 Del {mejor['fecha_inicio']} al {mejor['fecha_fin']}")
                print(f"   💰 Precio esperado: ${mejor['precio_esperado']:.2f}")
                print(f"   📊 Rango: ${mejor['precio_min']:.2f} - ${mejor['precio_max']:.2f}")
                print(f"   🗓️  {mejor['dias_disponibles']} días disponibles con este precio")
            else:
                print(f"   📅 {mejor['fecha']}")
                print(f"   💰 Precio esperado: ${mejor['precio_esperado']:.2f}")
                print(f"   📊 Rango: ${mejor['precio_min']:.2f} - ${mejor['precio_max']:.2f}")
            
            # Mostrar todas las predicciones diarias
            print(f"\n📋 PREDICCIONES DIARIAS ({len(producto['predicciones'])} días):")
            print(f"   {'Fecha':<15} {'Precio':<12} {'Mín':<12} {'Máx':<12}")
            print("   " + "-"*50)
            
            for pred in producto['predicciones']:
                print(f"   {pred['fecha']:<15} "
                      f"${pred['precio_esperado']:<11.2f} "
                      f"${pred['precio_min']:<11.2f} "
                      f"${pred['precio_max']:<11.2f}")
            
            # URL de la gráfica
            if 'grafica' in producto:
                print(f"\n📈 Gráfica disponible en:")
                print(f"   https://price-predictor-api-02g8.onrender.com/{producto['grafica']}")
            
            print("\n" + "="*80)
        
        # Guardar en archivo JSON local
        filename = f"predicciones_{consulta['fecha_inicio']}_a_{consulta['fecha_fin']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Predicciones guardadas en: {filename}")
        
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

except requests.exceptions.Timeout:
    print("⏰ La petición tardó demasiado. La API puede estar 'dormida' (plan Free).")
    print("   Espera 1 minuto y vuelve a intentar.")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
