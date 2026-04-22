import streamlit as st
from pid_extraction.storage.artifact_store import LocalArtifactStore
import json

st.title("🔍 Active Review")

store = LocalArtifactStore()
drawing_id = st.text_input("Enter Drawing ID (e.g., demo_t7572):")

if drawing_id:
    try:
        state = store.get_json(drawing_id, "05_review_state.json")
        val_data = store.get_json(drawing_id, "04_extraction_validated.json")
        manifest = store.get_json(drawing_id, "02_regions/manifest.json")
        
        pending_items = [i for i in state.get("items", []) if i["status"] == "pending"]
        
        if not pending_items:
            st.success("Queue empty! Move to Drawing Summary.")
        else:
            # Grab the highest priority item
            pending_items.sort(key=lambda x: x["priority"], reverse=True)
            active_item = pending_items[0]
            
            # Find the corresponding extraction details
            extraction = next((r["extraction"] for r in val_data["validated_extractions"] if r["extraction"]["id"] == active_item["extraction_id"]), None)
            
            if extraction:
                st.subheader(f"Reviewing Tag: {extraction.get('tag')}")
                
                # --- THE FIX: Handle merged region IDs ---
                raw_region_id = extraction.get('region_id', 'R01')
                # If it's merged like "R03, R04", just grab the first one to show the user
                primary_region = raw_region_id.split(",")[0].strip()
                
                region_info = next((r for r in manifest.get("regions", []) if r["region_id"] == primary_region), None)
                
                # Ensure Linux-safe paths so the image doesn't break on Streamlit Cloud
                image_path = region_info["file_path"].replace("\\", "/") if region_info else f"02_regions/{primary_region}.png"
                # -----------------------------------------
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    try:
                        st.image(store.get_bytes(drawing_id, image_path), caption=f"Found in: {raw_region_id}", format="PNG")
                    except Exception as img_error:
                        st.error("Image missing on server. Try re-running the extraction!")
                    
                with col2:
                    with st.form("review_form"):
                        st.text_input("Extracted Tag", value=extraction.get("tag"), disabled=True)
                        decision = st.radio("Decision", ["accept", "correct", "reject"])
                        corrected_tag = st.text_input("Corrected Tag (if 'correct' selected)")
                        notes = st.text_area("Reviewer Notes")
                        
                        if st.form_submit_button("Submit Decision"):
                            # Update State
                            active_item["status"] = "decided"
                            active_item["reviewer_decision"] = decision
                            active_item["corrected_tag"] = corrected_tag
                            active_item["notes"] = notes
                            
                            store.put_json(drawing_id, "05_review_state.json", state)
                            st.success("Decision saved!")
                            st.rerun()
                            
                with col3:
                    st.info(f"**Type:** {extraction.get('type')}")
                    st.info(f"**Confidence:** {extraction.get('confidence')}")
                    st.info(f"**Priority Score:** {active_item.get('priority')}")
                    
    except Exception as e:
        st.error(f"Error loading data: {e}")
