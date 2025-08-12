import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINTS = {
    "USD": os.getenv("API_URL"),
    "BTC": os.getenv("API_URL_BTC"),
    "USDT": os.getenv("API_URL_USDT"),
    "ETH": os.getenv("API_URL_ETH"),
}

CONFIG_MONEDAS = {
    "USD": ("ask", "bid"),
    "BTC": ("totalAsk", "totalBid"),
    "USDT": ("totalAsk", "totalBid"),
    "ETH": ("totalAsk", "totalBid"),
}

def formatear_mensaje(moneda, mejor_compra, mejor_venta, tipo_precio, tipo_precio_venta):
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    return (
        f"💱 *{moneda}*\n"
        f"🕒 _Última actualización: {timestamp}_\n\n"
        f"🟢 *Mejor lugar para comprar:* [{mejor_compra['prettyName']}]({mejor_compra['url']})\n"
        f"💸 Precio: `${mejor_compra[tipo_precio]:,.2f}`\n\n"
        f"🔴 *Mejor lugar para vender:* [{mejor_venta['prettyName']}]({mejor_venta['url']})\n"
        f"💰 Precio: `${mejor_venta[tipo_precio_venta]:,.2f}`\n"
    )

def obtener_mejor_compra_venta(moneda):
    if moneda not in API_ENDPOINTS or not API_ENDPOINTS[moneda]:
        return f"⚠️ URL para {moneda} no configurada."
    
    if moneda not in CONFIG_MONEDAS:
        return f"⚠️ Configuración de precios para {moneda} no encontrada."

    tipo_precio, tipo_precio_venta = CONFIG_MONEDAS[moneda]
    url = API_ENDPOINTS[moneda]

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        casas_activas = [
            casa for casa in data
            if casa.get(tipo_precio) is not None and casa.get(tipo_precio_venta) is not None
        ]

        if not casas_activas:
            return f"⚠️ No se encontraron casas activas con precios válidos para *{moneda}*."

        mejor_compra = min(casas_activas, key=lambda c: c[tipo_precio])
        mejor_venta = max(casas_activas, key=lambda c: c[tipo_precio_venta])

        return formatear_mensaje(moneda, mejor_compra, mejor_venta, tipo_precio, tipo_precio_venta)

    except requests.RequestException as e:
        return f"❌ *Error de conexión* al obtener cotización de {moneda}: `{e}`"
    except Exception as e:
        return f"❌ *Error inesperado* en {moneda}: `{e}`"

def obtener_mejor_compra_venta_usd():
    return obtener_mejor_compra_venta("USD")

def obtener_mejor_compra_venta_btc():
    return obtener_mejor_compra_venta("BTC")

def obtener_mejor_compra_venta_usdt():
    return obtener_mejor_compra_venta("USDT")

def obtener_mejor_compra_venta_eth():
    return obtener_mejor_compra_venta("ETH")

if __name__ == "__main__":
    for moneda in CONFIG_MONEDAS:
        print(obtener_mejor_compra_venta(moneda))
        print()
