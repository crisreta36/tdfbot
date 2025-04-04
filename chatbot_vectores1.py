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

# Paso 1: Leer CSV y procesar datos
base_path = "csv"
archivos = [f for f in os.listdir(base_path) if f.endswith(".csv")]
dataframes = []

for archivo in archivos:
    ruta = os.path.join(base_path, archivo)
    try:
        df = pd.read_csv(ruta, encoding="utf-8")
    except:
        df = pd.read_csv(ruta, encoding="latin1")
    df.columns = [col.strip().upper() for col in df.columns]  # limpiar nombres de columnas
    df["ACTIVIDAD"] = archivo.replace(".csv", "")
    dataframes.append(df)

data_total = pd.concat(dataframes, ignore_index=True)

# Paso 2: Crear embeddings (opcional, para búsqueda futura)
texto = ""
for df in dataframes:
    texto += df.fillna("").to_string(index=False) + "\n"
splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=100)
fragmentos = splitter.split_text(texto)
documentos = [Document(page_content=f) for f in fragmentos]
embedding = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documentos, embedding)

# Paso 3: Interfaz gráfica Streamlit
st.set_page_config(page_title="ChatBot Turismo Ushuaia", layout="centered")
st.title("🧭 Chatbot Turismo Ushuaia")
st.markdown("Seleccioná una actividad turística y consultá sus categorías, fechas y precios disponibles.")

# Menú 1: Selección de Actividad
actividades = sorted(data_total["ACTIVIDAD"].unique())
actividad_seleccionada = st.selectbox("1️⃣ Elegí una actividad:", actividades)

# Filtrar por actividad
df_actividad = data_total[data_total["ACTIVIDAD"] == actividad_seleccionada]

# Detectar la primera columna útil automáticamente
columnas_validas = [col for col in df_actividad.columns if col not in ["ACTIVIDAD", "PRECIO", "FECHA INICIO", "FECHA FIN"]]
columna_texto = columnas_validas[0] if columnas_validas else None

# Extraer y limpiar categorías con búsqueda flexible
palabras_clave = ["adulto", "jubilado", "menor", "cud", "infoa"]
categorias = []

if columna_texto:
    for valor in df_actividad[columna_texto].dropna().astype(str).unique():
        valor_limpio = valor.strip().lower()
        if any(p in valor_limpio for p in palabras_clave):
            categorias.append(valor.strip())
    categorias = sorted(list(set(categorias)))

# Menú 2: Selección de Categoría
if categorias:
    categoria_seleccionada = st.selectbox("2️⃣ Seleccioná una categoría:", categorias)
    st.markdown("### 3️⃣ Fechas y precios disponibles:")

    # Mostrar coincidencias de esa categoría
    coincidencias = df_actividad[df_actividad[columna_texto] == categoria_seleccionada]
    if "FECHA INICIO" in df_actividad.columns and "FECHA FIN" in df_actividad.columns:
        for _, row in coincidencias.iterrows():
            precio = row.get("PRECIO", "No disponible")
            fecha_ini = row.get("FECHA INICIO", "?")
            fecha_fin = row.get("FECHA FIN", "?")
            st.write(f"📅 Del {fecha_ini} al {fecha_fin} — 💵 {precio}")

        st.markdown("---")
        st.subheader("4️⃣ Confirmación")
        if st.button("✅ Quiero reservar esta actividad"):
            st.success(f"Has seleccionado: \n\n👉 Actividad: {actividad_seleccionada}\n👉 Categoría: {categoria_seleccionada}\n👉 Precio: {precio}\n👉 Fechas: {fecha_ini} a {fecha_fin}")
            st.markdown("[Ir al área de ventas](https://wa.me/542901469748)")
    else:
        st.warning("No se encontraron columnas de fechas válidas.")
else:
    st.warning("No se encontraron categorías específicas en esta actividad. Probá otra.")
