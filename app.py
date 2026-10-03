import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types


# Load the server-side API key from the project's .env file.
load_dotenv()

MODEL_NAME = "gemini-3.8-flash"

st.title("Multimodal AI Image Q&A")
st.write(
    "Upload an image and ask a question about it. The app combines your image "
    "and question to generate an answer."
)

uploaded_image = st.file_uploader(
    "Choose an image",
    type=["png", "jpg", "jpeg"],
)
question = st.text_area("Ask a question about the image")

if uploaded_image is not None:
    st.image(uploaded_image, caption=uploaded_image.name, use_container_width=True)

if st.button("Analyze Image", type="primary"):
    if uploaded_image is None:
        st.warning("Please upload an image before analyzing.")
    elif not question.strip():
        st.warning("Please enter a question about the image.")
    else:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY is missing. Add it to your .env file.")
        else:
            # Keep the model grounded in visible details and explicit about uncertainty.
            prompt = (
                "Answer the user's question directly using only information visible "
                "in the image. If the requested information cannot be determined "
                "from the image, say so clearly. Never invent missing visual "
                f"information.\n\nUser's question: {question.strip()}"
            )

            client = None
            try:
                with st.spinner("Analyzing the image..."):
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=[
                            prompt,
                            # Send the uploaded image bytes and their MIME type to Gemini.
                            types.Part.from_bytes(
                                data=uploaded_image.getvalue(),
                                mime_type=uploaded_image.type,
                            ),
                        ],
                    )

                if response.text:
                    st.subheader("Answer")
                    st.write(response.text)
                else:
                    st.warning("Gemini returned an empty response. Please try again.")
            except errors.APIError as error:
                st.error(f"Gemini API request failed: {error}")
            finally:
                if client is not None:
                    client.close()
