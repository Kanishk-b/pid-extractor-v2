import json
from pathlib import Path
from typing import Protocol, Any, Optional, Type
from pydantic import BaseModel

class ArtifactStore(Protocol):
    def put_bytes(self, drawing_id: str, key: str, data: bytes) -> Path: ...
    def get_bytes(self, drawing_id: str, key: str) -> bytes: ...
    def put_json(self, drawing_id: str, key: str, data: BaseModel | dict[str, Any]) -> Path: ...
    def get_json(self, drawing_id: str, key: str, model: Optional[Type[BaseModel]] = None) -> Any: ...
    def list_keys(self, drawing_id: str, prefix: str = "") -> list[str]: ...
    def artifact_path(self, drawing_id: str) -> Path: ...

class LocalArtifactStore:
    def __init__(self, root_dir: str = "./artifacts"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def artifact_path(self, drawing_id: str) -> Path:
        path = self.root / drawing_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def put_bytes(self, drawing_id: str, key: str, data: bytes) -> Path:
        file_path = self.artifact_path(drawing_id) / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        return file_path
        
    def get_bytes(self, drawing_id: str, key: str) -> bytes:
        return (self.artifact_path(drawing_id) / key).read_bytes()

    def put_json(self, drawing_id: str, key: str, data: BaseModel | dict[str, Any]) -> Path:
        file_path = self.artifact_path(drawing_id) / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        json_data = data.model_dump() if isinstance(data, BaseModel) else data
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
        return file_path
        
    def get_json(self, drawing_id: str, key: str, model: Optional[Type[BaseModel]] = None) -> Any:
        file_path = self.artifact_path(drawing_id) / key
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if model:
            return model.model_validate(data)
        return data

    def list_keys(self, drawing_id: str, prefix: str = "") -> list[str]:
        path = self.artifact_path(drawing_id)
        if not path.exists():
            return []
        return [str(p.relative_to(path)).replace("\\", "/") for p in path.rglob(f"{prefix}*") if p.is_file()]