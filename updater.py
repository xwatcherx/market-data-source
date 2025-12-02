import requests
from bs4 import BeautifulSoup
import json
import statistics
import time
import random

# --- MAPA DE LA VERDAD (Atributo Usuario -> Búsqueda Real en Mercado) ---
TARGETS = {
    # 1. INTENCIONES (Lo que buscan)
    "seguros": "car insurance cpa",
    "hipoteca": "refinance mortgage cpa",
    "crypto": "crypto trading cpa",
    "software": "b2b software cpa",
    "betting": "sports betting cpa",
    "remesas": "money transfer app cpa",
    "wedding": "wedding registry cpa",
    "travel": "luxury travel booking cpa",
    "electronics": "win gadget sweepstakes",
    "gaming": "online game registration cpa",
    "fashion": "fashion subscription cpa",
    
    # 2. PERFIL FINANCIERO (Lo que son)
    # Si alguien tiene deudas, su valor es lo que pagan las reparadoras de crédito
    "deuda_relief": "debt relief cpa", 
    "credit_repair": "credit repair cpa",
    # Si alguien es inversor, su valor es lo que pagan los brokers
    "investor": "forex trading cpa",
    
    # 3. ACTIVOS / HOGAR
    # Solo un dueño de casa instala paneles solares o ventanas nuevas
    "homeowner": "solar panel installation cpa", 
    "home_security": "home security system cpa",
    
    # 4. SALUD / CONDICIONES (High Ticket)
    "salud_oido": "hearing aid trial cpa",
    "salud_diabetes": "diabetes monitor cpa",
    "salud_piel": "skincare trial cpa",
    "salud_senior": "medical alert system cpa",
    
    # 5. DEMOGRAFÍA
    "padres": "baby formula sample cpa", # Proxy para valor de padres
    "seniors": "medicare supplement cpa" # Proxy para jubilados
}

def obtener_promedio_mercado(busqueda):
    """
    Busca en Affplus precios reales de afiliados.
    """
    print(f"   🔎 Auditando mercado para: '{busqueda}'...")
    # Usamos un user-agent rotativo simple para evitar bloqueos básicos
    uas = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)']
    headers = {'User-Agent': random.choice(uas)}
    
    url = f"https://www.affplus.com/search?q={busqueda.replace(' ', '%20')}&sort=payout_desc"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        precios = []
        # Buscamos patrones de precio en el HTML
        elementos = soup.find_all(string=lambda text: text and "$" in text)
        
        for texto in elementos:
            # Limpieza agresiva de texto
            txt = texto.strip().replace('$', '').replace(',', '')
            try:
                # Extraemos el primer número flotante que encontremos
                monto = float(txt.split()[0]) 
                # Filtro de cordura: Eliminamos ofertas de $0.10 y errores de $5000
                if 1.50 < monto < 450.0: 
                    precios.append(monto)
            except:
                continue
        
        if precios:
            # Usamos la mediana para mayor fiabilidad (evita picos falsos)
            resultado = statistics.median(precios)
            print(f"      💰 Precio Mercado: ${resultado:.2f}")
            return round(resultado, 2)
        else:
            print(f"      ⚠️ Sin datos recientes. Usando histórico.")
            return None
            
    except Exception as e:
        print(f"      ❌ Error conexión: {e}")
        return None

def actualizar_base_datos():
    print("--- INICIANDO ESCANEO DE MERCADO RTB (REAL TIME BIDDING) ---")
    
    nuevo_json = {
        "meta_info": {
            "fecha_actualizacion": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "fuente_datos": "Affiliate Networks Aggregated Data"
        },
        "cotizaciones": {}
    }
    
    for key, query in TARGETS.items():
        precio = obtener_promedio_mercado(query)
        if precio:
            nuevo_json["cotizaciones"][key] = precio
        else:
            # Fallbacks conservadores si falla el scraping hoy
            defaults = {
                "seguros": 42.0, "hipoteca": 38.0, "deuda_relief": 25.0,
                "salud_oido": 55.0, "homeowner": 30.0, "padres": 12.0
            }
            nuevo_json["cotizaciones"][key] = defaults.get(key, 8.0) # 8.0 es el valor base genérico
            
    # Guardamos
    with open('market_prices.json', 'w') as f:
        json.dump(nuevo_json, f, indent=4)
    
    print("--- BASE DE DATOS ACTUALIZADA CON PRECIOS REALES ---")

if __name__ == "__main__":
    actualizar_base_datos()
