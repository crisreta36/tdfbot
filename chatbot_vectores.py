# chatbot_vectores.py

import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter

# Cargar la API Key desde .env
load_dotenv()

# Paso 1: Leer todos los CSV y convertir a texto unificado
base_path = "csv"
archivos = os.listdir(base_path)
texto_total = ""

for archivo in archivos:
    if archivo.endswith(".csv"):
        ruta = os.path.join(base_path, archivo)
        try:
            df = pd.read_csv(ruta, encoding="utf-8")
        except:
            df = pd.read_csv(ruta, encoding="latin1")

        texto = f"\n--- {archivo.replace('.csv','')} ---\n"
        texto += df.fillna("").to_string(index=False)
        texto_total += texto + "\n"

# Paso 2: Dividir el texto en fragmentos (chunks)
splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=100)
fragmentos = splitter.split_text(texto_total)
documentos = [Document(page_content=f) for f in fragmentos]

# Paso 3: Crear los embeddings e índice FAISS
embedding = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documentos, embedding)
retriever = vectorstore.as_retriever()

# Paso 4: Crear el LLM (modelo de lenguaje)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Paso 5: Crear la cadena de respuesta QA con un prompt en español
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQAWithSourcesChain

prompt_template = PromptTemplate.from_template(
    """
    Eres un asistente turístico de Ushuaia. Respondé en español usando la información proporcionada.
    Si no sabés la respuesta con certeza, decí "No tengo información suficiente para responder eso."

    Pregunta: {question}
    Información:
    {context}
    Respuesta:
    """
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False,
    chain_type_kwargs={"prompt": prompt_template}
)

# Paso 6: Interfaz de consola
print("\n--- CHATBOT TURISMO USHUAIA (EMBEDDINGS) ---")
print("Consultá sobre actividades, precios, fechas, paquetes, excursiones... Escribí 'salir' para terminar.\n")

while True:
    consulta = input("Tú: ")
    if consulta.lower() in ["salir", "exit", "quit"]:
        print("Bot: ¡Gracias por usar el asistente turístico! Hasta pronto.")
        break
    try:
        respuesta = qa_chain.run(consulta)
        print(f"Bot: {respuesta}\n")
    except Exception as e:
        print(f"Bot: Hubo un error procesando la consulta: {str(e)}\n")
