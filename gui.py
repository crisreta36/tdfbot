import tkinter as tk
from tkinter import messagebox
from threading import Thread
from bot_logic import TradingBot


class TradingBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Bot")
        self.bot_thread = None
        self.bot = None  # Instancia del bot
        self.bot_running = False

        # Inputs
        tk.Label(root, text="Pares de Mercado (e.g., SHIBUSDT):").grid(row=0, column=0)
        self.market_entry = tk.Entry(root)
        self.market_entry.grid(row=0, column=1)

        tk.Label(root, text="Monto de Compra (USDT):").grid(row=1, column=0)
        self.buy_amount_entry = tk.Entry(root)
        self.buy_amount_entry.grid(row=1, column=1)

        tk.Label(root, text="Porcentaje Máximo de Caída:").grid(row=2, column=0)
        self.max_drop_entry = tk.Entry(root)
        self.max_drop_entry.grid(row=2, column=1)

        tk.Label(root, text="Incremento Objetivo:").grid(row=3, column=0)
        self.target_increment_entry = tk.Entry(root)
        self.target_increment_entry.grid(row=3, column=1)

        tk.Label(root, text="Incremento Alcista:").grid(row=4, column=0)  # Nuevo campo
        self.alcista_increment_entry = tk.Entry(root)
        self.alcista_increment_entry.grid(row=4, column=1)

        tk.Label(root, text="API Key:").grid(row=5, column=0)
        self.api_key_entry = tk.Entry(root, show="*")
        self.api_key_entry.grid(row=5, column=1)

        tk.Label(root, text="API Secret:").grid(row=6, column=0)
        self.api_secret_entry = tk.Entry(root, show="*")
        self.api_secret_entry.grid(row=6, column=1)

        tk.Label(root, text="Tiempo entre ciclos (ms):").grid(row=7, column=0)
        self.sleep_time_entry = tk.Entry(root)
        self.sleep_time_entry.grid(row=7, column=1)

        tk.Label(root, text="Límite Martingala:").grid(row=8, column=0)
        self.martingale_limit_entry = tk.Entry(root)
        self.martingale_limit_entry.grid(row=8, column=1)

        # Botones
        self.start_button = tk.Button(root, text="Iniciar Bot", command=self.start_bot)
        self.start_button.grid(row=9, columnspan=2)

        self.stop_button = tk.Button(root, text="Detener Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.grid(row=10, columnspan=2)

        self.save_button = tk.Button(root, text="Guardar Configuración", command=self.save_config)
        self.save_button.grid(row=11, columnspan=2)

        # Logs
        tk.Label(root, text="Logs:").grid(row=12, column=0)
        self.logs_text = tk.Text(root, height=10, width=50, state=tk.DISABLED)
        self.logs_text.grid(row=13, columnspan=2)

    def log_message(self, message):
        """Muestra un mensaje en el área de logs."""
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.insert(tk.END, message + "\n")
        self.logs_text.see(tk.END)
        self.logs_text.config(state=tk.DISABLED)

    def start_bot(self):
        if self.bot_running:
            messagebox.showwarning("Advertencia", "El bot ya está en ejecución.")
            return

        market = self.market_entry.get()
        try:
            buy_amount = float(self.buy_amount_entry.get())
            max_drop = float(self.max_drop_entry.get())
            target_increment = float(self.target_increment_entry.get())
            alcista_increment = float(self.alcista_increment_entry.get())  # Nuevo valor
            api_key = self.api_key_entry.get()
            api_secret = self.api_secret_entry.get()
            sleep_time = int(self.sleep_time_entry.get())
            martingale_limit = int(self.martingale_limit_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos.")
            return

        # Configurar el bot
        self.bot = TradingBot(
            market=market,
            buy_amount=buy_amount,
            max_drop_percent=max_drop,
            target_increment=target_increment,
            alcista_increment=alcista_increment,  # Nuevo parámetro
            api_key=api_key,
            api_secret=api_secret,
            sleep_time=sleep_time,
            martingale_limit=martingale_limit,
            log_callback=self.log_message
        )

        # Habilitar/deshabilitar botones
        self.bot_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Iniciar el bot en un hilo separado
        self.bot_thread = Thread(target=self.bot.start, daemon=True)
        self.bot_thread.start()
        self.log_message("Bot iniciado correctamente.")

    def stop_bot(self):
        if hasattr(self, "bot") and self.bot_running:
            self.bot_running = False
            self.bot.stop()  # Detenemos el bot correctamente
            if self.bot_thread:
                self.bot_thread.join()  # Esperamos a que el hilo termine
            self.log_message("Bot detenido manualmente.")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            messagebox.showinfo("Bot Detenido", "El bot se ha detenido correctamente.")

    def save_config(self):
        config = {
            "market": self.market_entry.get(),
            "buy_amount": self.buy_amount_entry.get(),
            "max_drop": self.max_drop_entry.get(),
            "target_increment": self.target_increment_entry.get(),
            "alcista_increment": self.alcista_increment_entry.get(),  # Guardar el nuevo valor
            "api_key": self.api_key_entry.get(),
            "api_secret": self.api_secret_entry.get(),
            "sleep_time": self.sleep_time_entry.get(),
            "martingale_limit": self.martingale_limit_entry.get(),
        }
        with open(".env", "w") as f:
            for key, value in config.items():
                f.write(f"{key.upper()}={value}\n")
        self.log_message("Configuración guardada correctamente.")
        messagebox.showinfo("Configuración Guardada", "La configuración ha sido guardada correctamente.")


# Inicializar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotApp(root)
    root.mainloop()
