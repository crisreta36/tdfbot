import pandas as pd
import os
from langchain_experimental.agents import create_pandas_dataframe_agent
#from langchain.llms import OpenAI
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Paso 1: Cargar todos los CSV desde la carpeta "csv"
base_path = "csv"

archivos = [
    "AVENTURA LAGOS 4X4 - NOCTURNA.csv",
    "AVENTURA LAGOS 4X4 - TRADICIONAL.csv",
    "AVISTAJE DE CASTORES.csv",
    "BUCEOBAUTISMO.csv",
    "BUCEOEXPERIMENTADO.csv",
    "CABALGATA 2HS.csv",
    "CABALGATA 4HS.csv",
    "CABALGATA 7HS.csv",
    "CITY TOUR.csv",
    "ENTRADA PARQUE NACIONAL.csv",
    "LAGOSCONVENCIONAL.csv",
    "LAGOSEXPRESS.csv",
    "NAVEGACIONCANALBEAGLE.csv",
    "NAVEGACIONPINGUINERA.csv",
    "PAQUETE2DIAS.csv",
    "PAQUETE3DIAS.csv",
    "PAQUETE4DIAS.csv",
    "PARQUE + TREN.csv",
    "PARQUE NACIONAL.csv",
    "PARQUE, TREKKING Y CANOAS.csv",
    "RUTACENTOLLAPREMIUM.csv",
    "RUTACENTOLLATRADICIONAL.csv",
    "SOBREVUELO7MINUTOS.csv",
    "SOBREVUELO15MINUTOS.csv",
    "SOBREVUELO30MINUTOS.csv",
    "TASA PORTUARIA.csv",
    "TRANSFER.csv",
    "TRASLADO GLACIAR MARTIAL.csv",
    "TRASLADO PARQUE NACIONAL.csv",
    "TREKKINGLAGUNAESMERALDA.csv",
    "TREKKINGOJODELALBINO.csv",
    "TREKKINGVINCIGUERRA.csv",
    "TREN FIN DEL MUNDO.csv",
]

df_total = pd.DataFrame()

for archivo in archivos:
    ruta = os.path.join(base_path, archivo)
    try:
        temp_df = pd.read_csv(ruta, encoding="utf-8")
    except:
        temp_df = pd.read_csv(ruta, encoding="latin1")
    temp_df["FUENTE"] = archivo.replace(".csv", "")
    df_total = pd.concat([df_total, temp_df], ignore_index=True)

# Paso 2: Crear el agente de LangChain
#llm = OpenAI(temperature=0)
#llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

agente = create_pandas_dataframe_agent(llm, df_total, verbose=True)

# Paso 3: Interfaz simple por consola
print("\n--- CHATBOT TURISMO USHUAIA ---")
print("Escribí tu consulta sobre actividades, precios o fechas. Escribí 'salir' para terminar.\n")

while True:
    consulta = input("Tú: ")
    if consulta.lower() in ["salir", "exit", "quit"]:
        print("Bot: ¡Gracias por usar el asistente turístico! Hasta luego.")
        break
    try:
        respuesta = agente.run(consulta)
        print(f"Bot: {respuesta}\n")
    except Exception as e:
        print(f"Bot: Lo siento, no pude procesar esa consulta. Error: {str(e)}\n")