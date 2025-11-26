"""
Ejemplo: Buscar producto y luego obtener predicciones
"""

import requests
import json

API_URL = 'https://price-predictor-api-02g8.onrender.com/api'

def buscar_y_predecir(nombre_producto, fecha_inicio, fecha_fin):
    """
    Busca un producto y genera predicciones
    """
    
    print("="*80)
    print(f"🔍 Buscando: '{nombre_producto}'")
    print("="*80)
    
    # Paso 1: Buscar el producto
    try:
        response = requests.get(
            f'{API_URL}/productos/buscar',
            params={'q': nombre_producto}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['encontrado']:
                # Producto encontrado exactamente
                producto_exacto = data['producto_exacto']
                print(f"✅ Producto encontrado: {producto_exacto}")
                productos_a_usar = [producto_exacto]
                
            else:
                # No encontrado - mostrar sugerencias
                print(f"⚠️  '{nombre_producto}' no encontrado exactamente.")
                print(f"\n📋 Productos similares disponibles:")
                
                for i, sug in enumerate(data['sugerencias'], 1):
                    print(f"   {i}. {sug}")
                
                if data['sugerencias']:
                    # Usar el primero por defecto (o pedir al usuario que elija)
                    producto_seleccionado = data['sugerencias'][0]
                    print(f"\n✓ Usando: {producto_seleccionado}")
                    productos_a_usar = [producto_seleccionado]
                else:
                    print(f"\n❌ No hay productos similares disponibles")
                    return None
            
            # Paso 2: Generar predicciones con el producto correcto
            print(f"\n🔄 Generando predicciones...")
            print(f"   Período: {fecha_inicio} al {fecha_fin}")
            print(f"   Producto: {productos_a_usar[0]}")
            print(f"\n⏳ Esperando respuesta...\n")
            
            response_pred = requests.post(
                f'{API_URL}/predicciones',
                json={
                    "productos": productos_a_usar,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "generar_graficas": True
                },
                timeout=120
            )
            
            if response_pred.status_code == 200:
                pred_data = response_pred.json()
                
                print("✅ ¡Predicciones generadas!\n")
                print("="*80)
                
                for producto in pred_data['productos']:
                    print(f"\n📦 {producto['alimento']}")
                    print("-"*80)
                    
                    mejor = producto['mejor_dia_compra']
                    
                    print(f"\n🛒 MEJOR MOMENTO PARA COMPRAR:")
                    if mejor['tipo'] == 'rango':
                        print(f"   📅 Del {mejor['fecha_inicio']} al {mejor['fecha_fin']}")
                        print(f"   💰 ${mejor['precio_esperado']:.2f}")
                        print(f"   🗓️  {mejor['dias_disponibles']} días con este precio")
                    else:
                        print(f"   📅 {mejor['fecha']}")
                        print(f"   💰 ${mejor['precio_esperado']:.2f}")
                    
                    print(f"\n📋 PREDICCIONES DIARIAS:")
                    print(f"   {'Fecha':<15} {'Precio':<12} {'Mín':<12} {'Máx':<12}")
                    print("   " + "-"*50)
                    
                    for pred in producto['predicciones'][:10]:  # Primeros 10 días
                        print(f"   {pred['fecha']:<15} "
                              f"${pred['precio_esperado']:<11.2f} "
                              f"${pred['precio_min']:<11.2f} "
                              f"${pred['precio_max']:<11.2f}")
                    
                    if len(producto['predicciones']) > 10:
                        print(f"   ... y {len(producto['predicciones']) - 10} días más")
                    
                    if 'grafica' in producto:
                        print(f"\n📈 Gráfica:")
                        print(f"   https://price-predictor-api-02g8.onrender.com/{producto['grafica']}")
                
                print("\n" + "="*80)
                return pred_data
                
            else:
                print(f"❌ Error al generar predicciones: {response_pred.text}")
                return None
                
        else:
            print(f"❌ Error en búsqueda: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ============================================================
# EJEMPLOS DE USO
# ============================================================

if __name__ == "__main__":
    
    # Ejemplo 1: Producto que NO existe exacto (mostrará sugerencias)
    print("\n🧪 PRUEBA 1: Buscar 'Leche'")
    buscar_y_predecir(
        nombre_producto="Leche",
        fecha_inicio="2026-01-01",
        fecha_fin="2026-01-15"
    )
    
    print("\n\n")
    
    # Ejemplo 2: Producto que SÍ existe exacto
    print("🧪 PRUEBA 2: Buscar 'Arroz'")
    buscar_y_predecir(
        nombre_producto="Arroz",
        fecha_inicio="2026-01-01",
        fecha_fin="2026-01-15"
    )
    
    print("\n\n")
    
    # Ejemplo 3: Usar nombre completo directamente
    print("🧪 PRUEBA 3: Nombre exacto 'Leche Pasteurizada Y Fresca'")
    buscar_y_predecir(
        nombre_producto="Leche Pasteurizada Y Fresca",
        fecha_inicio="2026-01-01",
        fecha_fin="2026-01-15"
    )
