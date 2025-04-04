import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
from datetime import datetime

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

# Configuración de Streamlit
st.set_page_config(page_title="ChatBot Turismo Ushuaia", layout="centered")
st.title("🧭 Chatbot Turismo Ushuaia")
st.markdown("Seleccioná una actividad turística y consultá sus categorías, fechas y precios disponibles.")

# Paso 1: Selección de actividad
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
            st.markdown("### 3️⃣ Seleccioná la fecha y precio disponibles:")
            coincidencias = df_actividad[df_actividad[col_cat] == categoria_seleccionada]

            opciones_fechas = []
            for _, row in coincidencias.iterrows():
                precio = row.get("PRECIO", "No disponible")
                fecha_ini = row.get("FECHA INICIO", "?")
                fecha_fin = row.get("FECHA FIN", "?")
                label = f"📅 Del {fecha_ini} al {fecha_fin} — 💵 {precio}"
                opciones_fechas.append((label, fecha_ini, fecha_fin, precio))

            if opciones_fechas:
                opciones_labels = [opt[0] for opt in opciones_fechas]
                seleccion_label = st.selectbox("Elegí una opción:", [""] + opciones_labels)

                if seleccion_label and seleccion_label != "":
                    seleccion = next(opt for opt in opciones_fechas if opt[0] == seleccion_label)
                    fecha_ini, fecha_fin, precio = seleccion[1], seleccion[2], seleccion[3]

                    st.markdown("---")
                    st.subheader("4️⃣ Confirmación")
                    if st.button("✅ Quiero reservar esta actividad"):
                        resumen = (
                            f"👉 Actividad: {actividad_seleccionada}\n"
                            f"👉 Categoría: {categoria_seleccionada}\n"
                            f"👉 Precio: {precio}\n"
                            f"👉 Fechas: {fecha_ini} a {fecha_fin}"
                        )
                        st.success("Reserva confirmada 🎉")
                        st.code(resumen)
                        st.markdown("[Ir al área de ventas (WhatsApp)](https://wa.me/542901469748)")

                        # Guardar historial en log_reservas.txt
                        with open("log_reservas.txt", "a", encoding="utf-8") as f:
                            f.write(f"{datetime.now()} - {resumen}\n")

                        # Descargar como TXT
                        st.download_button("⬇️ Descargar resumen en TXT", resumen, file_name="reserva.txt")

                        # Descargar como PDF
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        for line in resumen.split("\n"):
                            pdf.cell(200, 10, txt=line, ln=True)
                        pdf_output_path = "reserva.pdf"
                        pdf.output(pdf_output_path)
                        with open(pdf_output_path, "rb") as f:
                            st.download_button("⬇️ Descargar en PDF", f, file_name="reserva.pdf")

                    # Botón para reiniciar
                    if st.button("🔁 Volver a empezar"):
                        st.experimental_rerun()

    else:
        st.warning("No se encontraron categorías para esta actividad.")

else:
    st.info("Por favor seleccioná una actividad para comenzar.")
