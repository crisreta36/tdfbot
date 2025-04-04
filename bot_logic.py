import math
import time
from binance.client import Client


class TradingBot:
    def __init__(self, market, buy_amount, max_drop_percent, target_increment, alcista_increment, api_key, api_secret, sleep_time, martingale_limit, log_callback=None):
        self.market = market.upper()
        self.buy_amount = buy_amount
        self.max_drop_percent = max_drop_percent
        self.target_increment = target_increment
        self.alcista_increment = alcista_increment  # Incremento para compras en tendencia alcista
        self.api_key = api_key
        self.api_secret = api_secret
        self.sleep_time = sleep_time
        self.martingale_limit = martingale_limit
        self.last_buy_price = None
        self.martingale_multiplier = 1
        self.log_callback = log_callback
        self.client = Client(api_key, api_secret)
        self.running = False  # Controla si el bot está en ejecución

    def log(self, message):
        """Muestra o guarda logs dependiendo de la configuración"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def get_price(self):
        """Obtiene el precio actual del mercado"""
        try:
            return float(self.client.get_symbol_ticker(symbol=self.market)['price'])
        except Exception as e:
            self.log(f"Error al obtener precio: {e}")
            return None

    def adjust_quantity(self, quantity):
        """Ajusta la cantidad para cumplir con las reglas de Binance"""
        try:
            exchange_info = self.client.get_exchange_info()
            symbol_info = next(filter(lambda x: x['symbol'] == self.market, exchange_info['symbols']), None)

            if not symbol_info:
                raise Exception(f"Información del mercado no encontrada para {self.market}")

            step_size = float(next(filter(lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters']))['stepSize'])
            precision = int(math.log10(1 / step_size))
            adjusted_quantity = round(quantity, precision)
            return adjusted_quantity - (adjusted_quantity % step_size)
        except Exception as e:
            self.log(f"Error ajustando cantidad: {e}")
            return quantity

    def market_buy(self, quantity):
        """Realiza una compra de mercado"""
        try:
            adjusted_quantity = self.adjust_quantity(quantity)
            order = self.client.order_market_buy(symbol=self.market, quantity=adjusted_quantity)
            self.log(f"Compra realizada: {order}")
            return order
        except Exception as e:
            self.log(f"Error en market_buy: {e}")
            return None

    def market_sell(self, quantity):
        """Realiza una venta de mercado"""
        try:
            adjusted_quantity = self.adjust_quantity(quantity)
            order = self.client.order_market_sell(symbol=self.market, quantity=adjusted_quantity)
            self.log(f"Venta realizada: {order}")
            return order
        except Exception as e:
            self.log(f"Error en market_sell: {e}")
            return None

    def execute_trade(self):
        """Ejecuta operaciones de compra o venta según las condiciones"""
        current_price = self.get_price()
        if not current_price:
            return

        # Primera compra si no existe un precio previo
        if not self.last_buy_price:
            self.log(f"Comprando {self.market} a {current_price}")
            quantity = self.buy_amount / current_price
            order = self.market_buy(quantity)
            if order:
                self.last_buy_price = current_price
            return  # Salir para evitar cálculos de incremento o caída

        # Calcular incremento o caída solo si hay un precio de compra anterior
        increment = (current_price - self.last_buy_price) / self.last_buy_price
        drop = (self.last_buy_price - current_price) / self.last_buy_price

        # Verificar incremento para venta
        if increment >= self.target_increment:
            self.log(f"Vendiendo {self.market} a {current_price}")
            quantity = self.buy_amount / self.last_buy_price
            self.market_sell(quantity)
            self.last_buy_price = None  # Reiniciar después de vender
            self.martingale_multiplier = 1  # Reiniciar multiplicador
            return

        # Verificar caída para compra adicional
        if drop >= self.max_drop_percent:
            self.log(f"Comprando más {self.market} a {current_price} debido a caída")
            if self.martingale_multiplier <= self.martingale_limit:
                quantity = (self.buy_amount * self.martingale_multiplier) / current_price
                order = self.market_buy(quantity)
                if order:
                    self.martingale_multiplier *= 2
                    self.last_buy_price = current_price  # Actualizar precio
            else:
                self.log("Límite de Martingala alcanzado. Reiniciando multiplicador.")
                self.martingale_multiplier = 1
            return

        # Verificar incremento alcista para compra adicional
        if increment >= self.alcista_increment:
            self.log(f"Comprando más {self.market} a {current_price} debido a tendencia alcista")
            if self.martingale_multiplier <= self.martingale_limit:
                quantity = (self.buy_amount * self.martingale_multiplier) / current_price
                order = self.market_buy(quantity)
                if order:
                    self.martingale_multiplier *= 2
                    self.last_buy_price = current_price  # Actualizar precio
            else:
                self.log("Límite de Martingala alcanzado. Reiniciando multiplicador.")
                self.martingale_multiplier = 1

    def start(self):
        """Inicia el ciclo principal del bot"""
        self.running = True
        try:
            self.log("Iniciando bot de trading...")
            while self.running:
                self.execute_trade()
                time.sleep(self.sleep_time / 1000)
        except KeyboardInterrupt:
            self.log("Bot detenido manualmente.")

    def stop(self):
        """Detiene el bot"""
        self.running = False
        self.log("Bot detenido.")
