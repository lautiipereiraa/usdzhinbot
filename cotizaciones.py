import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

API_URL = os.getenv("API_URL")
API_URL_BTC = os.getenv("API_URL_BTC")
API_URL_USDT = os.getenv("API_URL_USDT")
API_URL_ETH = os.getenv("API_URL_ETH")

def formatear_mensaje(moneda, mejor_compra, mejor_venta, tipo_precio='ask', tipo_precio_venta='bid'):
    return (
        f"--- {moneda} ---\n"
        f"Mejor lugar para comprar: {mejor_compra['prettyName']} ({mejor_compra['url']})\n"
        f"Precio: ${mejor_compra[tipo_precio]:,.2f}\n\n"
        f"Mejor lugar para vender: {mejor_venta['prettyName']} ({mejor_venta['url']})\n"
        f"Precio: ${mejor_venta[tipo_precio_venta]:,.2f}\n"
    )

def obtener_mejor_compra_venta_usd():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        casas_activas = [casa for casa in data if casa.get('is24x7') and casa.get('ask') is not None and casa.get('bid') is not None]

        if not casas_activas:
            return "No se encontraron casas activas con precios válidos para USD."

        mejor_compra = min(casas_activas, key=lambda c: c['ask'])
        mejor_venta = max(casas_activas, key=lambda c: c['bid'])

        return formatear_mensaje("USD", mejor_compra, mejor_venta, tipo_precio='ask', tipo_precio_venta='bid')

    except requests.RequestException as e:
        return f"Error de conexión con la API USD: {e}"
    except Exception as e:
        return f"Error inesperado en USD: {e}"

def obtener_mejor_compra_venta_btc():
    try:
        response = requests.get(API_URL_BTC)
        response.raise_for_status()
        data = response.json()

        casas_activas = [casa for casa in data if casa.get('totalAsk') is not None and casa.get('totalBid') is not None]

        if not casas_activas:
            return "No se encontraron casas activas con precios válidos para BTC."

        mejor_compra = min(casas_activas, key=lambda c: c['totalAsk'])
        mejor_venta = max(casas_activas, key=lambda c: c['totalBid'])

        return formatear_mensaje("BTC", mejor_compra, mejor_venta, tipo_precio='totalAsk', tipo_precio_venta='totalBid')

    except requests.RequestException as e:
        return f"Error de conexión con la API BTC: {e}"
    except Exception as e:
        return f"Error inesperado en BTC: {e}"

def obtener_mejor_compra_venta_usdt():
    try:
        response = requests.get(API_URL_USDT)
        response.raise_for_status()
        data = response.json()

        casas_activas = [casa for casa in data if casa.get('totalAsk') is not None and casa.get('totalBid') is not None]

        if not casas_activas:
            return "No se encontraron casas activas con precios válidos para USDT."

        mejor_compra = min(casas_activas, key=lambda c: c['totalAsk'])
        mejor_venta = max(casas_activas, key=lambda c: c['totalBid'])

        return formatear_mensaje("USDT", mejor_compra, mejor_venta, tipo_precio='totalAsk', tipo_precio_venta='totalBid')

    except requests.RequestException as e:
        return f"Error de conexión con la API USDT: {e}"
    except Exception as e:
        return f"Error inesperado en USDT: {e}"

def obtener_mejor_compra_venta_eth():
    try:
        response = requests.get(API_URL_ETH)
        response.raise_for_status()
        data = response.json()

        casas_activas = [casa for casa in data if casa.get('totalAsk') is not None and casa.get('totalBid') is not None]

        if not casas_activas:
            return "No se encontraron casas activas con precios válidos para ETH."

        mejor_compra = min(casas_activas, key=lambda c: c['totalAsk'])
        mejor_venta = max(casas_activas, key=lambda c: c['totalBid'])

        return formatear_mensaje("ETH", mejor_compra, mejor_venta, tipo_precio='totalAsk', tipo_precio_venta='totalBid')

    except requests.RequestException as e:
        return f"Error de conexión con la API ETH: {e}"
    except Exception as e:
        return f"Error inesperado en ETH: {e}"

if __name__ == "__main__":
    print(obtener_mejor_compra_venta_usd())
    print(obtener_mejor_compra_venta_btc())
    print(obtener_mejor_compra_venta_usdt())
    print(obtener_mejor_compra_venta_eth())
