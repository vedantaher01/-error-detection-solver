import streamlit as st
from PIL import Image
from ocr_utils import extract_text_from_image
from solver import solve_problem

st.set_page_config(page_title="Error Detection Solver", layout="wide")

st.title("Error Detection Techniques Solver")
st.subheader("Scan a problem statement from camera or upload an image")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

with col2:
    camera_image = st.camera_input("Take a photo")

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
elif camera_image is not None:
    image = Image.open(camera_image)

if image is not None:
    st.image(image, caption="Uploaded / Captured Image", use_container_width=True)

    with st.spinner("Extracting text from image..."):
        extracted_text = extract_text_from_image(image)

    st.markdown("### Extracted Problem Statement")
    if not extracted_text:
        st.warning("No text was detected. Try a clearer, well-lit photo.")

    st.caption(
        "OCR can misread digits (for example 0 as O, or 1 as l). "
        "Check the text below and correct it if needed. The solution updates when you click outside the box or press Ctrl+Enter."
    )
    problem_text = st.text_area(
        "Problem text (editable)",
        value=extracted_text or "",
        height=150,
        key=f"problem_text_{hash(extracted_text or '')}",
    )

    if problem_text.strip():
        with st.spinner("Solving the error detection problem..."):
            result = solve_problem(problem_text)

        st.markdown("### Detected Method")
        st.write(str(result.get("method", "Unknown")).upper())

        if result.get("status") == "success":
            st.markdown("### Step-by-Step Explanation")
            st.markdown(result.get("explanation", ""))

            with st.expander("Solution details (summary)", expanded=True):
                for key, value in result.items():
                    if key not in ["method", "status", "explanation"]:
                        label = key.replace("_", " ").title()
                        st.write(f"**{label}:** {value}")
        else:
            st.markdown("### Error")
            st.write(result.get("message", "Something went wrong."))
