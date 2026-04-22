import streamlit as st
from pid_extraction.storage.artifact_store import LocalArtifactStore
import json

st.title("📋 Pending Review Queue")

store = LocalArtifactStore()
# In a real app with DB, we'd query across all drawings. For MVP, we'll ask for a drawing ID.
drawing_id = st.text_input("Enter Drawing ID to view queue (e.g., demo_t7572):")

if drawing_id:
    try:
        state = store.get_json(drawing_id, "05_review_state.json")
        st.write("### Queue Summary")
        st.json(state.get("summary", {}))
        
        pending_items = [i for i in state.get("items", []) if i["status"] == "pending"]
        
        if not pending_items:
            st.success("No pending items for this drawing!")
        else:
            st.warning(f"Found {len(pending_items)} items requiring human review.")
            st.dataframe(pending_items, width="stretch")
            
    except Exception as e:
        st.error(f"Could not load review state: {e}")
