import streamlit as st
import threading
import time
from pathlib import Path
import sys

# Force Streamlit to find the backend root folder
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from pid_extraction.storage.artifact_store import LocalArtifactStore
from config.settings import settings
from pid_extraction.components.c1_preprocessing import Preprocessor
from pid_extraction.components.c2_extraction import Extractor
from pid_extraction.components.c3_validation import Validator
from pid_extraction.components.c4_routing import QueueManager
from pid_extraction.components.c1_preprocessing.family_template import load_family

st.set_page_config(page_title="Upload & Process", layout="centered")
st.title("🚀 Upload & Process P&ID")

# --- 1. Background Thread Runner ---
# This runs invisibly in the background so the UI doesn't freeze
def run_pipeline_thread(drawing_id: str, family: str, pdf_bytes: bytes, tracker: dict):
    try:
        store = LocalArtifactStore(settings.ARTIFACT_STORE_ROOT)
        
        # Step 0: Save PDF
        tracker["status"] = "Saving PDF to artifacts..."
        tracker["progress"] = 5
        dest_path = store.artifact_path(drawing_id) / "01_source.pdf"
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(pdf_bytes)
        
        family_config = load_family(family)
        
        # Step 1: Preprocessing
        tracker["status"] = "Component 1: Rasterizing & Slicing Image..."
        tracker["progress"] = 15
        c1 = Preprocessor(store, settings)
        c1.run(drawing_id, family)
        
        # Step 2: Extraction
        tracker["status"] = "Component 2: AI Vision Extraction (This takes a few minutes)..."
        tracker["progress"] = 40
        c2 = Extractor(store, settings)
        c2.run(drawing_id, family)
        
        # Step 3: Validation
        tracker["status"] = "Component 3: Applying Deterministic Business Rules..."
        tracker["progress"] = 80
        c3 = Validator(store, settings, family_config)
        c3.run(drawing_id)
        
        # Step 4: Routing
        tracker["status"] = "Component 4: Routing Data to Review Queue..."
        tracker["progress"] = 95
        c4 = QueueManager(store)
        c4.route_drawing(drawing_id)
        
        # Finish
        tracker["progress"] = 100
        tracker["status"] = "Pipeline Complete! Ready for Human Review."
        tracker["is_running"] = False
        tracker["is_complete"] = True

    except Exception as e:
        tracker["status"] = f"Pipeline Error: {str(e)}"
        tracker["is_running"] = False
        tracker["error"] = True

# --- 2. Initialize Session State ---
# This dictionary acts as a bridge between the Streamlit UI and the background thread
if "tracker" not in st.session_state:
    st.session_state.tracker = {
        "is_running": False,
        "is_complete": False,
        "progress": 0,
        "status": "",
        "error": False
    }

# --- 3. The UI Elements ---
with st.form("upload_form"):
    drawing_id = st.text_input("Drawing ID (e.g., demo_2):", placeholder="Enter a unique ID for this drawing")
    family = st.selectbox("Drawing Family Template:", ["gas_flotation_tank"])
    uploaded_file = st.file_uploader("Upload P&ID PDF", type=["pdf"])
    
    submit_button = st.form_submit_button("Start Extraction Pipeline", type="primary")

# --- 4. The Trigger Logic ---
if submit_button:
    if not drawing_id or not uploaded_file:
        st.error("Please provide both a Drawing ID and a PDF file.")
    else:
        # Reset the tracker
        st.session_state.tracker = {"is_running": True, "is_complete": False, "progress": 0, "status": "Initializing...", "error": False}
        
        # Spawn the background thread
        pdf_bytes = uploaded_file.read()
        thread = threading.Thread(
            target=run_pipeline_thread, 
            args=(drawing_id, family, pdf_bytes, st.session_state.tracker)
        )
        thread.start()
        st.rerun() # Refresh the page to show the progress bar

# --- 5. The Live Progress Polling ---
if st.session_state.tracker["is_running"]:
    st.divider()
    status_text = st.empty()
    prog_bar = st.progress(0)
    
    # This loop keeps the UI updating every second without breaking the thread
    while st.session_state.tracker["is_running"]:
        status_text.info(f"⏳ **{st.session_state.tracker['status']}**")
        prog_bar.progress(st.session_state.tracker["progress"])
        time.sleep(1)
        
    # When the loop breaks, the thread is finished!
    st.rerun()

# --- 6. Completion Message ---
if st.session_state.tracker.get("is_complete") and not st.session_state.tracker.get("is_running"):
    st.success(f"✅ {st.session_state.tracker['status']}")
    st.balloons()
    st.info("👈 Please proceed to the **1 Queue** page on the sidebar to review the results.")

if st.session_state.tracker.get("error"):
    st.error(f"❌ {st.session_state.tracker['status']}")