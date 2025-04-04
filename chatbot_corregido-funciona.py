# chatbot_web.py

import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Cargar la API Key
load_dotenv()

# Leer todos los CSV desde la carpeta
base_path = "csv"
archivos = [f for f in os.listdir(base_path) if f.endswith(".csv")]
dataframes = []

for archivo in archivos:
    ruta = os.path.join(base_path, archivo)
    try:
        df = pd.read_csv(ruta, encoding="utf-8")
    except:
        df = pd.read_csv(ruta, encoding="latin1")
    df["actividad"] = archivo.replace(".csv", "").strip()
    df["columna_categoria"] = df.columns[0]  # Guardamos el nombre real de la columna
    dataframes.append(df)

df_total = pd.concat(dataframes, ignore_index=True)

# Streamlit
st.set_page_config(page_title="ChatBot Turismo Ushuaia", layout="centered")
st.title("🧭 Chatbot Turismo Ushuaia")
st.markdown("Seleccioná una actividad turística y consultá sus categorías, fechas y precios disponibles.")

# Paso 1: Selección de Actividad
actividades = sorted(df_total["actividad"].unique())
actividad_seleccionada = st.selectbox("1️⃣ Elegí una actividad:", [""] + actividades)

if actividad_seleccionada:
    df_actividad = df_total[df_total["actividad"] == actividad_seleccionada]
    col_cat = df_actividad["columna_categoria"].iloc[0]

    categorias = df_actividad[col_cat].dropna().unique().tolist()
    categorias = sorted(categorias)

    if categorias:
        categoria_seleccionada = st.selectbox("2️⃣ Seleccioná una categoría:", [""] + categorias)

        if categoria_seleccionada:
            st.markdown("### 3️⃣ Fechas y precios disponibles:")
            coincidencias = df_actividad[df_actividad[col_cat] == categoria_seleccionada]

            for _, row in coincidencias.iterrows():
                precio = row.get("PRECIO", "No disponible")
                fecha_ini = row.get("FECHA INICIO", "?")
                fecha_fin = row.get("FECHA FIN", "?")
                st.write(f"📅 Del {fecha_ini} al {fecha_fin} — 💵 {precio}")

            st.markdown("---")
            st.subheader("4️⃣ Confirmación")
            if st.button("✅ Quiero reservar esta actividad"):
                st.success(
                    f"Has seleccionado:\n\n👉 Actividad: {actividad_seleccionada}\n👉 Categoría: {categoria_seleccionada}\n👉 Precio: {precio}\n👉 Fechas: {fecha_ini} a {fecha_fin}"
                )
                st.markdown("[Ir al área de ventas](https://wa.me/542901469748)")

    else:
        st.warning("No se encontraron categorías para esta actividad.")

else:
    st.info("Por favor seleccioná una actividad para comenzar.")
