"""
API Backend para Sistema de Predicción de Precios
Diseñado para ser consumido por un frontend
"""

import joblib
import pandas as pd
import os
import unicodedata
import matplotlib.pyplot as plt
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


class PredictorPreciosAPI:
    """
    Clase principal para el sistema de predicción de precios
    Optimizada para ser usada desde un frontend
    """
    
    def __init__(self, carpetas_modelos='modelos_join'):
        self.carpetas_modelos = carpetas_modelos
        self._productos_cache = None
    
    def _limpiar_nombre(self, texto: str) -> str:
        """Limpia el nombre del producto para encontrar el archivo del modelo"""
        texto_nfkd = unicodedata.normalize('NFKD', str(texto))
        texto_sin_tildes = texto_nfkd.encode('ASCII', 'ignore').decode('utf-8')
        texto_limpio = texto_sin_tildes.replace(',', '').replace('.', '')
        return texto_limpio.strip().replace(' ', '_').lower()
    
    def obtener_productos_disponibles(self) -> List[str]:
        """
        Retorna lista de todos los productos disponibles
        
        Returns:
            List[str]: Lista de nombres de productos
        """
        if self._productos_cache is not None:
            return self._productos_cache
        
        if not os.path.exists(self.carpetas_modelos):
            return []
        
        archivos = os.listdir(self.carpetas_modelos)
        productos = []
        
        for archivo in archivos:
            if archivo.endswith('_model.pkl'):
                nombre = archivo.replace('_model.pkl', '').replace('_', ' ').title()
                productos.append(nombre)
        
        self._productos_cache = sorted(productos)
        return self._productos_cache
    
    def buscar_producto(self, nombre_buscado: str) -> Dict[str, Any]:
        """
        Busca un producto exacto o similares
        
        Args:
            nombre_buscado: Nombre del producto a buscar
            
        Returns:
            Dict con: {
                "encontrado": bool,
                "producto_exacto": str | None,
                "sugerencias": List[str]
            }
        """
        productos_disponibles = self.obtener_productos_disponibles()
        nombre_limpio = self._limpiar_nombre(nombre_buscado).lower()
        
        # Buscar coincidencia exacta
        for producto in productos_disponibles:
            if self._limpiar_nombre(producto).lower() == nombre_limpio:
                return {
                    "encontrado": True,
                    "producto_exacto": producto,
                    "sugerencias": []
                }
        
        # Buscar similares
        similares = []
        palabras_buscadas = nombre_limpio.split('_')
        
        for producto in productos_disponibles:
            producto_limpio = self._limpiar_nombre(producto).lower()
            palabras_producto = producto_limpio.split('_')
            
            coincidencias = 0
            for palabra_buscada in palabras_buscadas:
                for palabra_producto in palabras_producto:
                    if palabra_buscada in palabra_producto or palabra_producto in palabra_buscada:
                        coincidencias += 1
                        break
            
            if coincidencias > 0:
                similares.append((producto, coincidencias))
        
        similares.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "encontrado": False,
            "producto_exacto": None,
            "sugerencias": [prod[0] for prod in similares[:5]]
        }
    
    def _obtener_prediccion_producto(self, nombre_alimento: str, fecha_inicio: str, 
                                     fecha_fin: str) -> Dict[str, Any]:
        """Obtiene predicciones diarias para un producto"""
        nombre_archivo = self._limpiar_nombre(nombre_alimento)
        ruta_modelo = os.path.join(self.carpetas_modelos, f'{nombre_archivo}_model.pkl')
        
        if not os.path.exists(ruta_modelo):
            archivos = os.listdir(self.carpetas_modelos)
            archivo_encontrado = None
            for archivo in archivos:
                if archivo.lower() == f'{nombre_archivo}_model.pkl'.lower():
                    archivo_encontrado = archivo
                    break
            
            if archivo_encontrado:
                ruta_modelo = os.path.join(self.carpetas_modelos, archivo_encontrado)
            else:
                return {"error": f"No se encontró modelo para '{nombre_alimento}'"}
        
        try:
            modelo = joblib.load(ruta_modelo)
            
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            fecha_fin_dt = pd.to_datetime(fecha_fin)
            ultima_fecha_entrenamiento = modelo.history['ds'].max()
            
            dias_diferencia = (fecha_fin_dt - ultima_fecha_entrenamiento).days
            if dias_diferencia < 1:
                dias_diferencia = (fecha_fin_dt - fecha_inicio_dt).days + 1
            
            future = modelo.make_future_dataframe(periods=dias_diferencia + 30, freq='D')
            forecast = modelo.predict(future)
            
            fechas_solicitadas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
            
            predicciones = []
            for fecha in fechas_solicitadas:
                mask = forecast['ds'] == fecha
                if mask.any():
                    fila = forecast[mask].iloc[0]
                else:
                    idx = (forecast['ds'] - fecha).abs().idxmin()
                    fila = forecast.iloc[idx]
                
                predicciones.append({
                    "fecha": fecha.strftime('%Y-%m-%d'),
                    "precio_esperado": round(float(fila['yhat']), 2),
                    "precio_min": round(float(fila['yhat_lower']), 2),
                    "precio_max": round(float(fila['yhat_upper']), 2)
                })
            
            return {
                "alimento": nombre_alimento,
                "predicciones": predicciones
            }
        except Exception as e:
            return {"error": f"Error al procesar '{nombre_alimento}': {str(e)}"}
    
    def _generar_grafica(self, nombre_alimento: str, predicciones: List[Dict], 
                         fecha_inicio: str, fecha_fin: str, 
                         carpeta_graficas: str = './graficas') -> str:
        """Genera y guarda la gráfica de un producto"""
        if not os.path.exists(carpeta_graficas):
            os.makedirs(carpeta_graficas)
        
        fechas = [p['fecha'] for p in predicciones]
        precios = [p['precio_esperado'] for p in predicciones]
        precios_min = [p['precio_min'] for p in predicciones]
        precios_max = [p['precio_max'] for p in predicciones]
        
        plt.figure(figsize=(14, 7))
        plt.plot(fechas, precios, 'b-', linewidth=2, label='Precio Esperado', 
                marker='o', markersize=2)
        plt.fill_between(range(len(fechas)), precios_min, precios_max, 
                         alpha=0.3, color='blue', label='Intervalo de Confianza')
        
        plt.xlabel('Fecha', fontsize=13)
        plt.ylabel('Precio ($/kg o $/litro)', fontsize=13)
        plt.title(f'Predicción: {nombre_alimento}\n{fecha_inicio} al {fecha_fin}', 
                 fontsize=15, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3, linestyle='--')
        
        total_dias = len(fechas)
        step = max(1, total_dias // 15)
        plt.xticks(range(0, len(fechas), step), 
                   [fechas[i] for i in range(0, len(fechas), step)], 
                   rotation=45, ha='right')
        
        plt.tight_layout()
        
        nombre_limpio = self._limpiar_nombre(nombre_alimento)
        nombre_archivo = f'{nombre_limpio}_{fecha_inicio}_a_{fecha_fin}.png'
        ruta_completa = os.path.join(carpeta_graficas, nombre_archivo)
        plt.savefig(ruta_completa, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"{carpeta_graficas}/{nombre_archivo}"
    
    def _calcular_mejor_dia(self, predicciones: List[Dict]) -> Dict[str, Any]:
        """Calcula el mejor día o rango de días para comprar"""
        precio_minimo = min(predicciones, key=lambda x: x['precio_esperado'])['precio_esperado']
        tolerancia = precio_minimo * 0.005
        
        dias_minimos = [
            p for p in predicciones 
            if abs(p['precio_esperado'] - precio_minimo) <= tolerancia
        ]
        
        if len(dias_minimos) > 1:
            return {
                "tipo": "rango",
                "fecha_inicio": dias_minimos[0]['fecha'],
                "fecha_fin": dias_minimos[-1]['fecha'],
                "precio_esperado": precio_minimo,
                "precio_min": dias_minimos[0]['precio_min'],
                "precio_max": dias_minimos[0]['precio_max'],
                "dias_disponibles": len(dias_minimos)
            }
        else:
            return {
                "tipo": "dia_unico",
                "fecha": dias_minimos[0]['fecha'],
                "precio_esperado": dias_minimos[0]['precio_esperado'],
                "precio_min": dias_minimos[0]['precio_min'],
                "precio_max": dias_minimos[0]['precio_max']
            }
    
    def generar_predicciones(self, productos: List[str], fecha_inicio: str, 
                            fecha_fin: str, generar_graficas: bool = True,
                            carpeta_json: str = './predicciones',
                            carpeta_graficas: str = './graficas') -> Dict[str, Any]:
        """
        Genera predicciones para una lista de productos
        
        Args:
            productos: Lista de nombres de productos
            fecha_inicio: Fecha inicial (YYYY-MM-DD)
            fecha_fin: Fecha final (YYYY-MM-DD)
            generar_graficas: Si se deben generar las gráficas
            carpeta_json: Carpeta donde guardar el JSON
            carpeta_graficas: Carpeta donde guardar las gráficas
            
        Returns:
            Dict con todas las predicciones y metadatos
        """
        if not os.path.exists(carpeta_json):
            os.makedirs(carpeta_json)
        
        productos_procesados = []
        errores = []
        
        for producto in productos:
            try:
                # Obtener predicciones
                datos = self._obtener_prediccion_producto(producto, fecha_inicio, fecha_fin)
                
                if "error" in datos:
                    errores.append({
                        "producto": producto,
                        "error": datos['error']
                    })
                    continue
                
                # Generar gráfica si está habilitado
                ruta_grafica = None
                if generar_graficas:
                    ruta_grafica = self._generar_grafica(
                        producto,
                        datos['predicciones'],
                        fecha_inicio,
                        fecha_fin,
                        carpeta_graficas
                    )
                
                # Calcular mejor día
                mejor_dia_info = self._calcular_mejor_dia(datos['predicciones'])
                
                # Preparar datos del producto
                producto_data = {
                    "alimento": producto,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "unidad": "kg/litro",
                    "total_registros": len(datos['predicciones']),
                    "mejor_dia_compra": mejor_dia_info,
                    "predicciones": datos['predicciones']
                }
                
                if ruta_grafica:
                    producto_data["grafica"] = ruta_grafica
                
                productos_procesados.append(producto_data)
                
            except Exception as e:
                errores.append({
                    "producto": producto,
                    "error": str(e)
                })
        
        # Preparar respuesta final
        resultado = {
            "fecha_consulta": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "periodo": {
                "inicio": fecha_inicio,
                "fin": fecha_fin
            },
            "total_productos": len(productos_procesados),
            "productos_procesados": len(productos_procesados),
            "productos_con_error": len(errores),
            "productos": productos_procesados
        }
        
        if errores:
            resultado["errores"] = errores
        
        # Guardar JSON
        nombre_archivo = f'predicciones_{fecha_inicio}_a_{fecha_fin}.json'
        ruta_json = os.path.join(carpeta_json, nombre_archivo)
        
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        resultado["ruta_json"] = ruta_json
        
        return resultado


# ============================================================
# FUNCIONES DE UTILIDAD PARA EL FRONTEND
# ============================================================

def inicializar_api(carpeta_modelos: str = 'modelos_join') -> PredictorPreciosAPI:
    """
    Inicializa la API del predictor
    
    Args:
        carpeta_modelos: Ruta a la carpeta con los modelos
        
    Returns:
        Instancia de PredictorPreciosAPI
    """
    return PredictorPreciosAPI(carpetas_modelos=carpeta_modelos)


def obtener_lista_productos() -> Dict[str, Any]:
    """
    Obtiene la lista completa de productos disponibles
    
    Returns:
        {
            "success": bool,
            "total": int,
            "productos": List[str]
        }
    """
    api = inicializar_api()
    productos = api.obtener_productos_disponibles()
    
    return {
        "success": True,
        "total": len(productos),
        "productos": productos
    }


def buscar_producto_api(nombre: str) -> Dict[str, Any]:
    """
    Busca un producto por nombre
    
    Args:
        nombre: Nombre del producto a buscar
        
    Returns:
        {
            "success": bool,
            "encontrado": bool,
            "producto_exacto": str | None,
            "sugerencias": List[str]
        }
    """
    api = inicializar_api()
    resultado = api.buscar_producto(nombre)
    
    return {
        "success": True,
        **resultado
    }


def generar_predicciones_api(productos: List[str], fecha_inicio: str, 
                             fecha_fin: str, generar_graficas: bool = True) -> Dict[str, Any]:
    """
    Genera predicciones para una lista de productos
    
    Args:
        productos: Lista de nombres de productos
        fecha_inicio: Fecha inicial (YYYY-MM-DD)
        fecha_fin: Fecha final (YYYY-MM-DD)
        generar_graficas: Si se deben generar gráficas
        
    Returns:
        Diccionario con todas las predicciones
    """
    try:
        api = inicializar_api()
        resultado = api.generar_predicciones(
            productos=productos,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            generar_graficas=generar_graficas
        )
        
        return {
            "success": True,
            **resultado
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# EJEMPLO DE USO PARA EL FRONTEND
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("API de Predicción de Precios - Ejemplo de Uso")
    print("="*60)
    
    # 1. Obtener lista de productos
    print("\n1. Obtener productos disponibles:")
    productos_resp = obtener_lista_productos()
    print(f"   Total productos: {productos_resp['total']}")
    print(f"   Primeros 5: {productos_resp['productos'][:5]}")
    
    # 2. Buscar un producto
    print("\n2. Buscar producto 'leche':")
    busqueda_resp = buscar_producto_api("leche")
    if busqueda_resp['encontrado']:
        print(f"   ✓ Encontrado: {busqueda_resp['producto_exacto']}")
    else:
        print(f"   ⚠ Sugerencias: {busqueda_resp['sugerencias'][:3]}")
    
    # 3. Generar predicciones
    print("\n3. Generar predicciones:")
    predicciones_resp = generar_predicciones_api(
        productos=["Tortilla de maíz", "Arroz", "Huevo"],
        fecha_inicio="2026-01-01",
        fecha_fin="2026-01-15",
        generar_graficas=True
    )
    
    if predicciones_resp['success']:
        print(f"   ✓ Productos procesados: {predicciones_resp['productos_procesados']}")
        print(f"   ✓ JSON guardado en: {predicciones_resp['ruta_json']}")
        
        # Mostrar mejor día del primer producto
        if predicciones_resp['productos']:
            primer_prod = predicciones_resp['productos'][0]
            mejor = primer_prod['mejor_dia_compra']
            print(f"\n   Mejor día para {primer_prod['alimento']}:")
            if mejor['tipo'] == 'rango':
                print(f"     📅 {mejor['fecha_inicio']} al {mejor['fecha_fin']}")
                print(f"     💰 ${mejor['precio_esperado']}")
            else:
                print(f"     📅 {mejor['fecha']}")
                print(f"     💰 ${mejor['precio_esperado']}")
    else:
        print(f"   ✗ Error: {predicciones_resp['error']}")
    
    print("\n" + "="*60)
