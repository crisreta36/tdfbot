import os
import pandas as pd
import streamlit as st
import urllib.parse
from fpdf import FPDF
from dotenv import load_dotenv

# Cargar variables de entorno
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
    df["columna_categoria"] = df.columns[0]
    dataframes.append(df)

df_total = pd.concat(dataframes, ignore_index=True)

# Interfaz Streamlit
st.set_page_config(page_title="ChatBot Turismo Ushuaia", layout="centered")
st.title("🧭 Chatbot Turismo Ushuaia")
st.markdown("Seleccioná una actividad turística y consultá sus categorías, fechas y precios disponibles.")

# Paso 1: Selección de actividad
actividades = sorted(df_total["actividad"].unique())
actividad_seleccionada = st.selectbox("1️⃣ Elegí una actividad:", ["Seleccioná una actividad..."] + actividades)

if actividad_seleccionada != "Seleccioná una actividad...":
    df_actividad = df_total[df_total["actividad"] == actividad_seleccionada]
    col_cat = df_actividad["columna_categoria"].iloc[0]

    categorias = sorted(df_actividad[col_cat].dropna().unique().tolist())
    categoria_seleccionada = st.selectbox("2️⃣ Seleccioná una categoría:", ["Seleccioná una categoría..."] + categorias)

    if categoria_seleccionada != "Seleccioná una categoría...":
        st.markdown("### 3️⃣ Fechas y precios disponibles:")

        coincidencias = df_actividad[df_actividad[col_cat] == categoria_seleccionada]
        fechas_precios = []

        for _, row in coincidencias.iterrows():
            precio = row.get("PRECIO", "No disponible")
            fecha_ini = row.get("FECHA INICIO", "?")
            fecha_fin = row.get("FECHA FIN", "?")
            label = f"{fecha_ini} al {fecha_fin} — {precio}"
            fechas_precios.append((label, fecha_ini, fecha_fin, precio))

        opciones_fechas = [fp[0] for fp in fechas_precios]
        seleccion_fechaprecio = st.selectbox("4️⃣ Elegí una fecha con su precio:", ["Seleccioná una opción..."] + opciones_fechas)

        if seleccion_fechaprecio != "Seleccioná una opción...":
            selected = next(fp for fp in fechas_precios if fp[0] == seleccion_fechaprecio)
            fecha_ini, fecha_fin, precio = selected[1], selected[2], selected[3]

            st.markdown("---")
            st.subheader("5️⃣ Confirmación")
            st.success(f"""
Has seleccionado:

👉 Actividad: {actividad_seleccionada}  
👉 Categoría: {categoria_seleccionada}  
👉 Precio: {precio}  
👉 Fechas: {fecha_ini} a {fecha_fin}
""")

            # WhatsApp
            mensaje = f"""
Hola, quiero reservar:

👉 Actividad: {actividad_seleccionada}
👉 Categoría: {categoria_seleccionada}
👉 Precio: {precio}
👉 Fechas: {fecha_ini} a {fecha_fin}
"""
            url_mensaje = urllib.parse.quote(mensaje)
            wa_link = f"https://wa.me/542901582590?text={url_mensaje}"
            st.markdown(f"[📲 Ir al área de ventas por WhatsApp]({wa_link})")

            # Guardar historial
            with open("log_reservas.txt", "a", encoding="utf-8") as f:
                f.write(mensaje + "\n---\n")

            # Descargar TXT
            st.download_button("⬇️ Descargar resumen TXT", mensaje, file_name="resumen_reserva.txt")

            # Descargar PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in mensaje.strip().splitlines():
                pdf.cell(200, 10, txt=line.strip(), ln=True)
            pdf_output_path = "resumen_reserva.pdf"
            pdf.output(pdf_output_path)
            with open(pdf_output_path, "rb") as f:
                st.download_button("⬇️ Descargar resumen PDF", f, file_name="resumen_reserva.pdf")

            # Reiniciar todo
            if st.button("🔄 Volver a empezar"):
                st.rerun()

else:
    st.info("Por favor seleccioná una actividad para comenzar.")
