import streamlit as st
from documentos import DocumentUploader
from busqueda import ClaudeAPI

# Configurar la página
st.set_page_config(page_title="Generador de Exámenes con IA", page_icon="📝", layout="wide")

# ========= CSS y estilos personalizados ==========
st.markdown(
    """
    <style>
        /* Fondo global (negro o azul muy oscuro) */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #000000 !important; /* #000000 = negro */
        }
        
        /* LATERALES en gris oscuro */
        .left-guide, .right-config {
            background-color: #2D2D2D !important; /* gris oscuro */
            color: #FFFFFF !important;            /* texto claro */
            padding: 20px;
            border-radius: 10px;
        }

        /* CENTRO en gris claro con texto en negro */
        .main .block-container {
            background-color: #F3F4F6 !important; /* gris claro */
            color: #000000 !important;           /* texto negro */
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Títulos en azul oscuro */
        h1, h2, h3 {
            color: #1E3A8A !important;
        }

        /* Botones personalizados */
        .stButton>button {
            background-color: #2563EB !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-size: 16px !important;
        }
        .stButton>button:hover {
            background-color: #1E40AF !important;
        }

        /* Mensajes personalizados (fondos de mensajes de estado) */
        .success {
            background-color: #D1FAE5 !important;
            color: #065F46 !important;
            padding: 10px;
            border-radius: 8px;
        }
        .error {
            background-color: #FEE2E2 !important;
            color: #991B1B !important;
            padding: 10px;
            border-radius: 8px;
        }
        .warning {
            background-color: #FEF9C3 !important;
            color: #92400E !important;
            padding: 10px;
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ========== Instancias ==========
doc_uploader = DocumentUploader()
claude_api = ClaudeAPI()

# ========== Layout en tres columnas ==========
col1, col2, col3 = st.columns([1.2, 2, 1.2])

# ---------- Columna Izquierda ----------
with col1:
    st.markdown('<div class="left-guide">', unsafe_allow_html=True)
    st.header("📖 Guía de Uso")
    st.write(
        """
        1️⃣ **Sube documentos** en PDF, DOCX o PPTX.  
        2️⃣ **Configura el ámbito y tipo de preguntas** (columna derecha).  
        3️⃣ **Genera Preguntas** con el botón en la columna central.  
        4️⃣ **Visualiza las preguntas y respuestas** sugeridas.  
        5️⃣ **Optimiza tus evaluaciones.**  
        """
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Columna Central ----------
with col2:
    st.title("📘 Generador de Exámenes con IA")

    # Subir documentos
    st.subheader("📂 Subir documentos")
    uploaded_files = st.file_uploader(
        "Selecciona archivos (PDF, DOCX, PPTX, TXT)",
        accept_multiple_files=True,
        type=['pdf', 'txt', 'docx', 'pptx']
    )
    if uploaded_files:
        for file in uploaded_files:
            try:
                doc_uploader.add_document(file)
                st.markdown(
                    f'<div class="success">✅ {file.name} cargado correctamente.</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.markdown(
                    f'<div class="error">❌ Error al procesar {file.name}: {e}</div>',
                    unsafe_allow_html=True
                )

    # Botón para generar preguntas
    if st.button("🚀 Generar Preguntas"):
        if doc_uploader.get_documents():
            full_text = doc_uploader.get_concatenated_text()

            # Recuperamos los valores de la columna derecha
            ambito_preguntas = st.session_state.get("ambito_preguntas", "Todo el temario")
            tema_concreto = st.session_state.get("tema_concreto", "")
            tipo_preguntas = st.session_state.get("tipo_preguntas", "Desarrollo")

            # Determinamos el "prompt_tema"
            if ambito_preguntas == "Todo el temario":
                prompt_tema = "todo el contenido del documento"
            else:
                if tema_concreto:
                    prompt_tema = f"el tema: {tema_concreto}"
                else:
                    st.markdown(
                        '<div class="warning">⚠️ Debes especificar un tema concreto.</div>',
                        unsafe_allow_html=True
                    )
                    st.stop()

            st.info(f"Generando preguntas de tipo '{tipo_preguntas}' sobre '{prompt_tema}'...")

            try:
                # Generar preguntas y respuestas con Claude
                questions, answers = claude_api.generar_preguntas(
                    full_text,
                    prompt_tema,
                    tipo_preguntas.lower()  # "desarrollo", "verdadero/falso" o "preguntas cortas"
                )

                if questions:
                    st.subheader("📋 Preguntas Generadas")

                    for i, question in enumerate(questions):
                        st.write(f"**Pregunta {i + 1}:** {question}")
                        # Dependiendo del tipo de pregunta, mostramos la respuesta de forma distinta
                        if tipo_preguntas == "Desarrollo":
                            # Mostrar respuesta larga
                            st.write(f"**Respuesta (Desarrollo):** {answers[i]}")

                        elif tipo_preguntas == "Verdadero/Falso":
                            # Insertar un radio button para que el usuario elija
                            seleccion = st.radio(
                                "¿Verdadero o Falso?",
                                ["Verdadero", "Falso"],
                                key=f"vf_{i}"
                            )
                            if seleccion:
                                st.success(f"**Respuesta Correcta:** {answers[i]}")

                        elif tipo_preguntas == "Preguntas Cortas":
                            # Mostrar respuesta breve
                            st.write(f"**Respuesta (Corta):** {answers[i]}")

                else:
                    st.markdown(
                        '<div class="warning">⚠️ No se pudieron generar preguntas. Verifica los documentos o el tema.</div>',
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.markdown(
                    f'<div class="error">❌ Error al generar preguntas: {e}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<div class="warning">⚠️ Primero sube documentos.</div>',
                unsafe_allow_html=True
            )

# ---------- Columna Derecha ----------
with col3:
    st.markdown('<div class="right-config">', unsafe_allow_html=True)
    st.header("⚙️ Configuración de Preguntas")

    # Selectbox del ámbito
    st.selectbox(
        "📌 Selecciona el ámbito de las preguntas:",
        ["Todo el temario", "Temas concretos"],
        key="ambito_preguntas"
    )

    # Input para el tema concreto (solo si la selección es "Temas concretos")
    if st.session_state["ambito_preguntas"] == "Temas concretos":
        st.text_input("✍️ Tema específico:", key="tema_concreto")

    # Selectbox del tipo de preguntas
    st.selectbox(
        "🎯 Selecciona el tipo de preguntas:",
        ["Desarrollo", "Verdadero/Falso", "Preguntas Cortas"],
        key="tipo_preguntas"
    )

    st.markdown('</div>', unsafe_allow_html=True)
