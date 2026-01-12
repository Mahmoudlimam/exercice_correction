import streamlit as st
from io import BytesIO
from fpdf import FPDF
from openrouter_client import correct_exercises, format_correction_output

# Page configuration
st.set_page_config(
    page_title="Exercise Correction AI",
    page_icon="📝",
    layout="wide"
)


def generate_pdf(correction_data: dict) -> bytes:
    """Generate a PDF from correction data."""
    pdf = FPDF()
    pdf.add_page()
    
    # Use a Unicode font for multi-language support
    pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    pdf.add_font('DejaVu', 'I', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf')
    
    pdf.set_font('DejaVu', '', 12)
    
    for exercise in correction_data.get("exercises", []):
        # Exercise header
        pdf.set_font('DejaVu', 'B', 14)
        exercise_name = exercise.get('exercise_name', '')
        pdf.multi_cell(0, 10, exercise_name)
        pdf.ln(3)
        
        # Given data (if present)
        given_data = exercise.get('given_data', '').strip()
        if given_data and given_data.lower() not in ['none', 'n/a', '-', '']:
            pdf.set_font('DejaVu', 'I', 11)
            pdf.multi_cell(0, 8, given_data)
            pdf.ln(3)
        
        # Questions and answers
        for i, q in enumerate(exercise.get("questions", []), 1):
            # Question
            pdf.set_font('DejaVu', 'B', 12)
            question_text = f"{i}. {q.get('question', '')}"
            pdf.multi_cell(0, 8, question_text)
            pdf.ln(2)
            
            # Answer
            pdf.set_font('DejaVu', '', 11)
            answer_text = q.get('answer', '')
            pdf.multi_cell(0, 7, answer_text)
            pdf.ln(5)
        
        # Separator
        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(8)
    
    # Return PDF as bytes
    return bytes(pdf.output())


# Title and description
st.title("📝 AI Exercise Correction")
st.markdown("Upload images of exercises and get AI-generated corrections with detailed answers.")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Language selection
    output_language = st.text_input(
        "Output Language (optional)",
        placeholder="e.g., English, French, Arabic...",
        help="Leave empty to use the same language as the exercise"
    )
    
    # User preferences
    user_preferences = st.text_area(
        "User Preferences (optional)",
        placeholder="e.g., Provide step-by-step solutions, Include formulas used...",
        help="Add any specific instructions for how you want the corrections"
    )
    
    st.markdown("---")
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. Upload one or more exercise images
    2. Optionally set output language
    3. Add any preferences for correction style
    4. Click 'Correct Exercises'
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Exercises")
    
    # File uploader for multiple images
    uploaded_files = st.file_uploader(
        "Upload exercise images",
        type=["png", "jpg", "jpeg", "webp", "gif"],
        accept_multiple_files=True,
        help="You can upload multiple images for multi-page exercises"
    )
    
    # Display uploaded images
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} image(s) uploaded:**")
        for i, file in enumerate(uploaded_files):
            with st.expander(f"Image {i+1}: {file.name}"):
                st.image(file, use_container_width=True)

with col2:
    st.header("✅ Corrections")
    
    # Correction button
    if st.button("🔍 Correct Exercises", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("Please upload at least one exercise image.")
        else:
            with st.spinner("Analyzing exercises and generating corrections..."):
                try:
                    # Prepare images for API
                    images = []
                    for file in uploaded_files:
                        # Get mime type from file extension
                        mime_type = f"image/{file.type.split('/')[-1]}" if file.type else "image/jpeg"
                        images.append((file.getvalue(), mime_type))
                    
                    # Call the API
                    result = correct_exercises(
                        images=images,
                        output_language=output_language if output_language.strip() else None,
                        user_preferences=user_preferences if user_preferences.strip() else None
                    )
                    
                    # Store result in session state
                    st.session_state.correction_result = result
                    st.session_state.formatted_result = format_correction_output(result)
                    
                except Exception as e:
                    st.error(f"Error generating corrections: {str(e)}")
    
    # Display results
    if "correction_result" in st.session_state:
        # Tabs for different views
        tab1, tab2 = st.tabs(["📄 Formatted", "🔧 Raw JSON"])
        
        with tab1:
            st.markdown(st.session_state.formatted_result)
        
        with tab2:
            st.json(st.session_state.correction_result)
        
        # Download buttons
        col_md, col_pdf = st.columns(2)
        
        with col_md:
            st.download_button(
                label="📥 Download MD",
                data=st.session_state.formatted_result,
                file_name="corrections.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col_pdf:
            try:
                pdf_bytes = generate_pdf(st.session_state.correction_result)
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name="corrections.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF generation error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Powered by OpenRouter AI | Model: google/gemini-3-flash-preview"
    "</div>",
    unsafe_allow_html=True
)
