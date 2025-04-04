# chatbot_web.py

import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

# Cargar API Key
load_dotenv()

# Leer CSVs
base_path = "csv"
archivos = [f for f in os.listdir(base_path) if f.endswith(".csv")]
dataframes = []

for archivo in archivos:
    ruta = os.path.join(base_path, archivo)
    try:
        df = pd.read_csv(ruta, encoding="utf-8")
    except:
        df = pd.read_csv(ruta, encoding="latin1")
    df.columns = [col.strip().upper() for col in df.columns]
    df["ACTIVIDAD"] = archivo.replace(".csv", "").strip()
    dataframes.append(df)

data_total = pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame(columns=["ACTIVIDAD"])

# Interfaz Streamlit
st.set_page_config(page_title="ChatBot Turismo Ushuaia", layout="centered")
st.title("🧭 Chatbot Turismo Ushuaia")
st.markdown("Seleccioná una actividad turística y consultá sus categorías, fechas y precios disponibles.")

# Mostrar selectbox sin selección por defecto
actividades = sorted(data_total["ACTIVIDAD"].dropna().unique())
actividad_seleccionada = st.selectbox("1️⃣ Elegí una actividad:", ["Seleccionar..."] + list(actividades))

if actividad_seleccionada != "Seleccionar...":
    df_actividad = data_total[data_total["ACTIVIDAD"] == actividad_seleccionada]

    columnas_utiles = [col for col in df_actividad.columns if col not in ["ACTIVIDAD", "PRECIO", "FECHA INICIO", "FECHA FIN"]]
    columna_categoria = columnas_utiles[0] if columnas_utiles else None

    palabras_clave = ["adulto", "jubilado", "menor", "cud", "infoa", "baustimo adulto", "baustimo jubilado", "baustimo menor", "baustimo cud" ]
    categorias = []

    if columna_categoria:
        for val in df_actividad[columna_categoria].dropna().astype(str).unique():
            if any(pal in val.lower() for pal in palabras_clave):
                categorias.append(val.strip())

        categorias = sorted(list(set(categorias)))

        if categorias:
            categoria_seleccionada = st.selectbox("2️⃣ Seleccioná una categoría:", ["Seleccionar..."] + categorias)

            if categoria_seleccionada != "Seleccionar...":
                st.markdown("### 3️⃣ Fechas y precios disponibles:")

                coincidencias = df_actividad[df_actividad[columna_categoria] == categoria_seleccionada]
                if "FECHA INICIO" in df_actividad.columns and "FECHA FIN" in df_actividad.columns:
                    for _, row in coincidencias.iterrows():
                        precio = row.get("PRECIO", "No disponible")
                        fecha_ini = row.get("FECHA INICIO", "?")
                        fecha_fin = row.get("FECHA FIN", "?")
                        st.write(f"📅 Del {fecha_ini} al {fecha_fin} — 💵 {precio}")

                    st.markdown("---")
                    st.subheader("4️⃣ Confirmación")
                    if st.button("✅ Quiero reservar esta actividad"):
                        st.success(
                            f"Has seleccionado: \n👉 Actividad: {actividad_seleccionada}\n👉 Categoría: {categoria_seleccionada}\n👉 Precio: {precio}\n👉 Fechas: {fecha_ini} a {fecha_fin}"
                        )
                        st.markdown("[Ir al área de ventas](https://wa.me/542901469748)")
                else:
                    st.warning("No se encontraron columnas de fechas válidas.")
        else:
            st.warning("No se encontraron categorías específicas en esta actividad. Probá otra.")
    else:
        st.warning("No se encontró una columna válida con categorías.")
else:
    st.info("⬅️ Por favor seleccioná una actividad para comenzar.")
