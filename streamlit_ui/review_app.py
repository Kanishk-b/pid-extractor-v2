import streamlit as st

st.set_page_config(page_title="P&ID Review Queue", layout="wide")

st.title("⚙️ P&ID Human Review Interface")
st.markdown("""
Welcome to the C4 Confidence-Gated Review UI. 
Please select a page from the sidebar:
- **1 Queue**: View pending items across all drawings.
- **2 Review**: Process your claimed extractions.
- **3 Drawing Summary**: Finalize and emit the validated database.
""")