import streamlit as st
from io import BytesIO
from fpdf import FPDF
from openrouter_client import correct_exercises, format_correction_output

# Page configuration - centered layout works better on mobile
st.set_page_config(
    page_title="Exercise Correction AI",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"  # Collapsed by default on mobile
)

# Custom CSS for better mobile experience
st.markdown("""
<style>
    /* Mobile-friendly adjustments */
    .stApp {
        max-width: 100%;
    }
    
    /* Better button styling on mobile */
    .stButton > button {
        width: 100%;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    
    /* Better file uploader on mobile */
    .stFileUploader {
        width: 100%;
    }
    
    /* Reduce padding on mobile */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 1rem !important;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
    }
    
    /* Hide hamburger menu text on mobile */
    .css-1rs6os {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


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


# Title
st.title("📝 Exercise Correction")
st.caption("Upload exercise images → Get AI corrections")

# Sidebar for settings (collapsed by default on mobile)
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Language selection
    output_language = st.text_input(
        "Output Language",
        placeholder="e.g., English, French, Arabic...",
        help="Leave empty to auto-detect from exercise"
    )
    
    # User preferences
    user_preferences = st.text_area(
        "Preferences",
        placeholder="e.g., Step-by-step solutions...",
        help="Custom instructions for corrections",
        height=100
    )
    
    st.markdown("---")
    st.markdown("**📋 How to use:**")
    st.markdown("1. Upload images\n2. Tap 'Correct'\n3. Download results")

# Main content - single column for mobile
st.markdown("### 📤 Upload")

# File uploader
uploaded_files = st.file_uploader(
    "Select exercise images",
    type=["png", "jpg", "jpeg", "webp", "gif"],
    accept_multiple_files=True,
    help="You can upload multiple images"
)

# Show uploaded images in expanders
if uploaded_files:
    st.success(f"✓ {len(uploaded_files)} image(s) ready")
    with st.expander("👁️ Preview images", expanded=False):
        for i, file in enumerate(uploaded_files):
            st.image(file, caption=f"{i+1}. {file.name}", use_container_width=True)
            if i < len(uploaded_files) - 1:
                st.divider()

# Correction button - full width
st.markdown("")  # Spacing
if st.button("🔍 Correct Exercises", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("Please upload at least one image first.")
    else:
        with st.spinner("🤖 Analyzing..."):
            try:
                # Prepare images for API
                images = []
                for file in uploaded_files:
                    mime_type = file.type if file.type else "image/jpeg"
                    images.append((file.getvalue(), mime_type))
                
                # Call the API
                result = correct_exercises(
                    images=images,
                    output_language=output_language.strip() if output_language and output_language.strip() else None,
                    user_preferences=user_preferences.strip() if user_preferences and user_preferences.strip() else None
                )
                
                # Store result in session state
                st.session_state.correction_result = result
                st.session_state.formatted_result = format_correction_output(result)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Display results
if "correction_result" in st.session_state:
    st.markdown("---")
    st.markdown("### ✅ Results")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["📄 Corrections", "🔧 JSON"])
    
    with tab1:
        st.markdown(st.session_state.formatted_result)
    
    with tab2:
        st.json(st.session_state.correction_result)
    
    # Download buttons - stacked vertically on mobile
    st.markdown("### 📥 Download")
    
    st.download_button(
        label="📄 Download as Markdown",
        data=st.session_state.formatted_result,
        file_name="corrections.md",
        mime="text/markdown",
        use_container_width=True
    )
    
    try:
        pdf_bytes = generate_pdf(st.session_state.correction_result)
        st.download_button(
            label="📑 Download as PDF",
            data=pdf_bytes,
            file_name="corrections.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.warning(f"PDF unavailable: {str(e)}")
    
    # Clear button
    if st.button("🗑️ Clear Results", use_container_width=True):
        del st.session_state.correction_result
        del st.session_state.formatted_result
        st.rerun()

# Footer
st.markdown("---")
st.caption("Powered by OpenRouter AI • Gemini 3 Flash")
