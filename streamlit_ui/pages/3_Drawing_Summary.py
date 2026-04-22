import streamlit as st
import io
import csv
from pid_extraction.storage.artifact_store import LocalArtifactStore
from pid_extraction.components.c4_routing.final_emitter import emit_final

st.title("✅ Finalize Drawing")

store = LocalArtifactStore()
drawing_id = st.text_input("Enter Drawing ID to finalize (e.g., demo_t7572):")

if st.button("Generate Final Artifact"):
    try:
        # 1. Generate the final JSON database
        final_records = emit_final(drawing_id, store)
        st.success(f"Successfully generated 06_final.json with {len(final_records)} records!")
        
        # 2. Convert to CSV in memory
        if final_records:
            # Grab the column headers from the keys of the first tag dictionary
            headers = list(final_records[0].keys())
            
            # Create an in-memory text buffer
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=headers)
            
            # Write the data
            writer.writeheader()
            writer.writerows(final_records)
            
            # 3. Create the Download Button
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"{drawing_id}_extraction_database.csv",
                mime="text/csv",
                type="primary" # Makes the button stand out!
            )
            
        # Display the raw JSON below the button for reference
        st.json(final_records)
        
    except Exception as e:
        st.error(f"Error finalizing drawing: {e}")