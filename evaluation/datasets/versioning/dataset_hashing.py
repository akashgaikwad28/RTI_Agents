"""
Cryptographic hashing for dataset integrity and reproducibility.
"""
import hashlib
import json
from evaluation.datasets.versioning.dataset_manifest import DatasetManifest

def calculate_dataset_hash(manifest: DatasetManifest) -> str:
    """Calculates a SHA256 hash of the dataset queries and core metadata to ensure integrity."""
    # We strip out ephemeral fields like created_at and hash itself
    core_data = {
        "dataset_name": manifest.dataset_name,
        "version": manifest.version,
        "language": manifest.language,
        "queries": [q.model_dump(exclude_none=True) for q in manifest.queries]
    }
    
    # Sort keys to ensure deterministic hashing
    serialized = json.dumps(core_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

def sign_manifest(manifest: DatasetManifest) -> DatasetManifest:
    """Calculates and attaches the hash to the manifest."""
    manifest.hash = calculate_dataset_hash(manifest)
    return manifest
