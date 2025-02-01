import random
import streamlit as st
from documentos import DocumentUploader
from busqueda import ClaudeAPI

# Configurar la página con título e icono
st.set_page_config(page_title="Generador de Exámenes con IA", page_icon="📝", layout="wide")

# Estilos personalizados en CSS
st.markdown("""
    <style>
        /* Ajuste del ancho de la app */
        .main .block-container {
            max-width: 1200px;
        }

        /* Ajustes de colores */
        body {
            background-color: white;
        }

        /* Estilos para la guía (columna izquierda) y configuración (columna derecha) */
        .left-guide, .right-config {
            background-color: #F3F4F6; /* Gris claro */
            padding: 20px;
            border-radius: 10px;
        }

        /* Color de títulos */
        h1, h2, h3 {
            color: #1E3A8A; /* Azul oscuro */
            text-align: center;
        }

        /* Botones personalizados */
        .stButton>button {
            background-color: #2563EB; /* Azul */
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
        }

        .stButton>button:hover {
            background-color: #1E40AF; /* Azul más oscuro */
        }

        /* Mensajes personalizados */
        .success {
            background-color: #D1FAE5; /* Verde claro */
            color: #065F46; /* Verde oscuro */
            padding: 10px;
            border-radius: 8px;
        }

        .error {
            background-color: #FEE2E2; /* Rojo claro */
            color: #991B1B; /* Rojo oscuro */
            padding: 10px;
            border-radius: 8px;
        }

        .warning {
            background-color: #FEF9C3; /* Amarillo claro */
            color: #92400E; /* Marrón oscuro */
            padding: 10px;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Instancias
doc_uploader = DocumentUploader()
claude_api = ClaudeAPI()

# Layout: Se divide la pantalla en tres columnas (izquierda, centro, derecha)
col1, col2, col3 = st.columns([1.2, 2, 1.2])  # Ajuste de tamaño de columnas

# 📖 **Barra lateral izquierda (Guía de uso)**
with col1:
    st.markdown('<div class="left-guide">', unsafe_allow_html=True)
    st.header("📖 Guía de Uso")
    st.write("""
    1️⃣ **Sube documentos** en formato PDF, DOCX o PPTX.  
    2️⃣ **Configura el ámbito y tipo de preguntas** en la sección de la derecha.  
    3️⃣ **Presiona "Generar Preguntas"** para obtener exámenes con IA.  
    4️⃣ **Visualiza las preguntas y respuestas sugeridas.**  
    5️⃣ **Optimiza el proceso de evaluación académica.**  
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# 📘 **Sección principal en el centro**
with col2:
    # Título de la aplicación
    st.title("📘 Generador de Exámenes con IA")

    # Sección de subida de documentos
    st.subheader("📂 Subir documentos")
    uploaded_files = st.file_uploader(
        "Selecciona archivos en PDF, DOCX o PPTX",
        accept_multiple_files=True,
        type=['pdf', 'txt', 'docx', 'pptx']
    )

    if uploaded_files:
        for file in uploaded_files:
            try:
                doc_uploader.add_document(file)
                st.markdown(f'<div class="success">✅ {file.name} cargado correctamente.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error">❌ Error al procesar {file.name}: {e}</div>', unsafe_allow_html=True)

    # Botón para generar preguntas
    if st.button("🚀 Generar Preguntas"):
        if doc_uploader.get_documents():
            # Obtener texto concatenado de los documentos
            full_text = doc_uploader.get_concatenated_text()

            # Generar preguntas y respuestas con Claude
            st.info(f"⏳ Generando preguntas con IA...")

            try:
                questions, answers = claude_api.generar_preguntas(full_text, "todo el contenido", "desarrollo")

                # Mostrar preguntas y respuestas generadas
                if questions:
                    st.subheader("📋 Preguntas Generadas")
                    for i, question in enumerate(questions):
                        st.markdown(f"**{i + 1}. {question}**")
                        st.markdown(f"✍️ **Respuesta sugerida:** {answers[i]}")

                else:
                    st.markdown('<div class="warning">⚠️ No se pudieron generar preguntas. Verifica los documentos.</div>', unsafe_allow_html=True)

            except Exception as e:
                st.markdown(f'<div class="error">❌ Error al generar preguntas: {e}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning">⚠️ Primero sube documentos.</div>', unsafe_allow_html=True)

# 🎯 **Barra lateral derecha (Configuración de preguntas)**
with col3:
    st.markdown('<div class="right-config">', unsafe_allow_html=True)
    st.header("⚙️ Configuración de Preguntas")
    
    ambito_preguntas = st.selectbox(
        "📌 Selecciona el ámbito de las preguntas:",
        ["Todo el temario", "Temas concretos"]
    )

    tema_concreto = None
    if ambito_preguntas == "Temas concretos":
        tema_concreto = st.text_input("✍️ Escribe el tema específico:")

    tipo_preguntas = st.selectbox(
        "🎯 Selecciona el tipo de preguntas:",
        ["Desarrollo", "Verdadero/Falso", "Preguntas Cortas"]
    )
    st.markdown('</div>', unsafe_allow_html=True)
