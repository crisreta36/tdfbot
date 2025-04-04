from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración del cliente Binance
client = Client(api_key=os.getenv("APIKEY"), api_secret=os.getenv("SECRET"))

def market_buy(symbol, quantity):
    try:
        order = client.order_market_buy(symbol=symbol, quantity=quantity)
        return order
    except Exception as e:
        print(f"Error en market_buy: {e}")
        return None

def market_sell(symbol, quantity):
    try:
        order = client.order_market_sell(symbol=symbol, quantity=quantity)
        return order
    except Exception as e:
        print(f"Error en market_sell: {e}")
        return None
