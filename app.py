# app.py

import random
import streamlit as st
from documentos import DocumentUploader
from busqueda import ClaudeAPI

# Instancias
doc_uploader = DocumentUploader()
claude_api = ClaudeAPI()

# Título de la aplicación
st.title("Generador de Exámenes")

# Subir documentos
uploaded_files = st.file_uploader("Sube tus documentos", accept_multiple_files=True, type=['pdf', 'txt', 'docx', 'pptx'])

if uploaded_files:
    for file in uploaded_files:
        try:
            doc_uploader.add_document(file)
        except Exception as e:
            st.error(f"Error al procesar el archivo {file.name}: {e}")
    st.success("Documentos cargados exitosamente.")

# Opciones de ámbito
st.sidebar.header("Opciones de Ámbito y Tipo de Preguntas")

ambito_preguntas = st.sidebar.selectbox(
    "Selecciona el ámbito de las preguntas:",
    ["Todo el temario", "Temas concretos"]
)

tema_concreto = None
if ambito_preguntas == "Temas concretos":
    tema_concreto = st.text_input("Escribe el tema sobre el que quieres generar preguntas:")

# Opciones de tipo de preguntas
tipo_preguntas = st.sidebar.selectbox(
    "Selecciona el tipo de preguntas:",
    ["Desarrollo", "Verdadero/Falso", "Preguntas Cortas"]
)

# Botón para generar preguntas
if st.button("Generar Preguntas"):
    if doc_uploader.get_documents():
        # Obtener texto concatenado de los documentos
        full_text = doc_uploader.get_concatenated_text()

        # Definir el prompt según las opciones seleccionadas
        if ambito_preguntas == "Todo el temario":
            prompt_tema = "todo el contenido del documento"
        elif tema_concreto:
            prompt_tema = f"el tema: {tema_concreto}"
        else:
            st.warning("Debes especificar un tema concreto.")
            st.stop()

        # Generar preguntas y respuestas con Claude
        st.info(f"Generando preguntas de tipo '{tipo_preguntas}' sobre '{prompt_tema}'...")
        try:
            questions, answers = claude_api.generar_preguntas(
                full_text,
                prompt_tema,
                tipo_preguntas.lower()  # "desarrollo", "verdadero/falso" o "preguntas cortas"
            )

            # Mostrar preguntas y respuestas
            if questions:
                st.header("Preguntas Generadas")
                for i, question in enumerate(questions):
                    st.write(f"**Pregunta {i + 1}:** {question}")

                    if tipo_preguntas == "Desarrollo":
                        # Mostrar la respuesta correcta como texto más largo
                        st.write(f"**Respuesta (desarrollo):** {answers[i]}")

                    elif tipo_preguntas == "Verdadero/Falso":
                        # Opciones verdadero/falso
                        seleccion = st.radio(
                            f"¿Es verdadero o falso?", 
                            ["Verdadero", "Falso"],
                            key=f"vf_{i}"
                        )
                        if seleccion:
                            st.success(f"**Respuesta Correcta:** {answers[i]}")

                    elif tipo_preguntas == "Preguntas Cortas":
                        # Mostrar respuesta corta
                        st.write(f"**Respuesta (corta):** {answers[i]}")

            else:
                st.warning("No se pudieron generar preguntas. Verifica los documentos o el tema.")
        except Exception as e:
            st.error(f"Error al generar preguntas: {e}")
    else:
        st.warning("Primero sube documentos.")
