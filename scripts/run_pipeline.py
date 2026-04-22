import sys
from pathlib import Path

# --- ADDED THIS TO FIX THE PATH ERROR ---
# This forces Python to look at the root directory so it can find 'config' and 'pid_extraction'
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
# ----------------------------------------

import typer
from pid_extraction.storage.artifact_store import LocalArtifactStore
from config.settings import settings
from pid_extraction.components.c1_preprocessing import Preprocessor
from pid_extraction.components.c2_extraction import Extractor
from pid_extraction.components.c3_validation import Validator
from pid_extraction.components.c4_routing import QueueManager
from pid_extraction.components.c1_preprocessing.family_template import load_family

app = typer.Typer(help="VLM P&ID Extraction Pipeline CLI")
store = LocalArtifactStore(settings.ARTIFACT_STORE_ROOT)

@app.command()
def process(drawing_id: str, family: str, pdf_path: Path):
    """Run Components C1 -> C2 -> C3 -> C4."""
    typer.echo(f"Starting pipeline for {drawing_id}...")
    
    # Setup
    dest_path = store.artifact_path(drawing_id) / "01_source.pdf"
    if pdf_path.resolve() != dest_path.resolve():
        import shutil
        shutil.copy(pdf_path, dest_path)
    
    family_config = load_family(family)
    
    # C1
    typer.echo("Running C1 (Preprocessing)...")
    c1 = Preprocessor(store, settings)
    c1.run(drawing_id, family)
    
    # C2
    typer.echo("Running C2 (Extraction)...")
    c2 = Extractor(store, settings)
    c2.run(drawing_id, family)
    
    # C3
    typer.echo("Running C3 (Validation)...")
    c3 = Validator(store, settings, family_config)
    c3.run(drawing_id)
    
    # C4 (Routing)
    typer.echo("Running C4 (Queue Routing)...")
    c4 = QueueManager(store)
    c4.route_drawing(drawing_id)
    
    typer.echo(f"Pipeline complete! Artifacts stored in artifacts/{drawing_id}/")
    typer.echo("Run 'streamlit run streamlit_ui/review_app.py' to review.")

if __name__ == "__main__":
    app()