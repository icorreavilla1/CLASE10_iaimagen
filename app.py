import os
import streamlit as st
import base64
from openai import OpenAI

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Configuración de Streamlit
st.set_page_config(page_title="Análisis de Imagen", layout="centered", initial_sidebar_state="collapsed")

# Cambiar el color de fondo
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f0f8ff;  /* Color de fondo */
    }
    .sidebar .sidebar-content {
        color: #4B0082;  /* Color del texto en la barra lateral */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título y subtítulo
st.title("Análisis de Imagen: 🤖🏞️")
st.write("<h3 style='color: #FF4500;'>¡Bienvenido! Aquí puedes analizar tus imágenes.</h3>", unsafe_allow_html=True)

# Barra lateral para instrucciones
with st.sidebar:
    st.header("Instrucciones")
    st.write("<h4 style='color: #008000;'>1. Ingresa tu clave de API.</h4>", unsafe_allow_html=True)
    st.write("<h4 style='color: #008000;'>2. Sube la imagen que deseas analizar.</h4>", unsafe_allow_html=True)
    st.write("<h4 style='color: #008000;'>3. Agrega detalles opcionales sobre la imagen.</h4>", unsafe_allow_html=True)
    st.write("<h4 style='color: #008000;'>4. Haz clic en 'Analiza la imagen'.</h4>", unsafe_allow_html=True)

ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke

# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

# Toggle for showing additional details input
show_details = st.toggle("Adiciona detalles sobre la imagen", value=False)

if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Adiciona contexto de la imagen aquí:",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("🔍 Analiza la imagen", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)

        prompt_text = ("Describe lo que ves en la imagen en español")
    
        if show_details and additional_details:
            prompt_text += (
                f"\n\nDetalles adicionales proporcionados por el usuario:\n{additional_details}"
            )
    
        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4-vision-preview", messages=messages,   
                max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Ha ocurrido un error: {e}")
else:
    # Warnings for user action required
    if not uploaded_file and analyze_button:
        st.warning("Por favor, sube una imagen.")
    if not api_key:
        st.warning("Por favor, ingresa tu clave de API.")
