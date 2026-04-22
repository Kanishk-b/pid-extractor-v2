import streamlit as st
from pid_extraction.storage.artifact_store import LocalArtifactStore
import json

st.title("📋 Pending Review Queue")

store = LocalArtifactStore()
# In a real app with DB, we'd query across all drawings. For MVP, we'll ask for a drawing ID.
drawing_id = st.text_input("Enter Drawing ID to view queue (e.g., demo_1):")

if drawing_id:
    try:
        state = store.get_json(drawing_id, "05_review_state.json")
        st.write("### Queue Summary")
        
        # Make the summary look nice using Streamlit metrics
        summary = state.get("summary", {})
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Items", summary.get("total_items", 0))
        col2.metric("Pending Review", summary.get("pending_items", 0))
        col3.metric("Auto-Accepted", summary.get("auto_accepted", 0))
        
        pending_items = [i for i in state.get("items", []) if i["status"] == "pending"]
        
        if not pending_items:
            st.success("🎉 No pending items! This drawing is fully processed.")
        else:
            st.warning(f"Found {len(pending_items)} items requiring human review.")
            
            st.write("---")
            st.subheader("🔍 Human Review Panel")
            
            # Select the first pending item to review
            item = pending_items[0]
            
            # Show the data on the left, and the image on the right
            data_col, img_col = st.columns([1, 1])
            
            with data_col:
                st.write("**Tag Data:**")
                st.json(item)
                
                # Mock action buttons for the MVP
                st.button("✅ Accept Tag", key="accept_btn", use_container_width=True)
                st.button("✏️ Edit Tag", key="edit_btn", use_container_width=True)
            
            with img_col:
                region_id = item.get("region_id")
                if region_id:
                    try:
                        # THE FIX: Safely fetching the image as bytes
                        # Force lowercase .png to avoid Linux case-sensitivity crashes
                        img_path = f"02_regions/{region_id}.png"
                        img_bytes = store.get_bytes(drawing_id, img_path)
                        st.image(img_bytes, caption=f"Source Region: {region_id}", use_container_width=True)
                    except Exception as img_e:
                        st.error(f"Could not load image for {region_id}. Ensure the C1 Preprocessor generated it.")
                else:
                    st.info("No region ID associated with this tag.")
            
            st.write("---")
            st.write("**All Pending Items:**")
            st.dataframe(pending_items, width="stretch")
            
    except Exception as e:
        st.error(f"Could not load review state. Have you run the pipeline for '{drawing_id}' yet? Error: {e}")