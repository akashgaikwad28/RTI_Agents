"""
Local registry to store and load versioned benchmark datasets.
"""
import os
import json
from typing import Optional, List
from evaluation.datasets.versioning.dataset_manifest import DatasetManifest
from evaluation.datasets.versioning.dataset_hashing import sign_manifest, calculate_dataset_hash

REGISTRY_DIR = os.path.join("data", "evaluation", "datasets")

class DatasetRegistry:
    def __init__(self, registry_dir: str = REGISTRY_DIR):
        self.registry_dir = registry_dir
        os.makedirs(self.registry_dir, exist_ok=True)
        
    def _get_path(self, dataset_name: str, version: str) -> str:
        return os.path.join(self.registry_dir, f"{dataset_name}_v{version}.json")
        
    def register(self, manifest: DatasetManifest) -> str:
        """Signs and saves the dataset manifest."""
        manifest = sign_manifest(manifest)
        filepath = self._get_path(manifest.dataset_name, manifest.version)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(manifest.model_dump_json(indent=2))
        return manifest.hash
        
    def load(self, dataset_name: str, version: str) -> Optional[DatasetManifest]:
        """Loads a dataset and verifies its integrity hash."""
        filepath = self._get_path(dataset_name, version)
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        manifest = DatasetManifest(**data)
        
        # Verify integrity
        expected_hash = calculate_dataset_hash(manifest)
        if manifest.hash and manifest.hash != expected_hash:
            raise ValueError(f"Dataset integrity compromised! Expected {manifest.hash}, got {expected_hash}")
            
        return manifest

    def list_datasets(self) -> List[dict]:
        """Lists all registered datasets and their versions."""
        datasets = []
        for file in os.listdir(self.registry_dir):
            if file.endswith(".json"):
                with open(os.path.join(self.registry_dir, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    datasets.append({
                        "name": data.get("dataset_name"),
                        "version": data.get("version"),
                        "hash": data.get("hash"),
                        "language": data.get("language")
                    })
        return datasets
