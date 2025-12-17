"""
Merge JSON data from multiple rental scrapers into a single dataset.
"""

import json
import hashlib
from pathlib import Path


def load_json(path: str) -> list:
    """Load JSON file and return list of records."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_id(record: dict) -> str:
    """Generate a unique ID based on URL hash."""
    url = record.get("AdUrl", "")
    return hashlib.md5(url.encode()).hexdigest()[:12]


def normalize_record(record: dict, source: str) -> dict:
    """Normalize record fields and add metadata."""
    normalized = {
        "id": generate_id(record),
        "source": source,
        "url": record.get("AdUrl"),
        "title": record.get("AdTitle"),
        "price_eur": record.get("RentalPrice_EUR"),
        "address": record.get("RentalAddrese"),
        "size_m2": record.get("RentalSize_m2"),
        "rooms": record.get("RentalRooms"),
        "floor": record.get("RentalFloor"),
        "rental_type": record.get("RentalType"),
        "furnished": record.get("Furnished"),
        "latitude": record.get("Lat"),
        "longitude": record.get("Lon"),
    }
    return normalized


def merge_datasets(files: list[tuple[str, str]]) -> list[dict]:
    """
    Merge multiple JSON files into one dataset.
    
    Args:
        files: List of tuples (file_path, source_name)
    
    Returns:
        List of normalized and merged records
    """
    merged = []
    seen_ids = set()
    
    for file_path, source in files:
        print(f"Loading {file_path}...")
        data = load_json(file_path)
        
        for record in data:
            normalized = normalize_record(record, source)
            
            # Skip duplicates based on ID (URL hash)
            if normalized["id"] not in seen_ids:
                seen_ids.add(normalized["id"])
                merged.append(normalized)
    
    print(f"Total records after merge: {len(merged)}")
    return merged


def save_merged(data: list[dict], output_path: str):
    """Save merged data to JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    # Define input files and their sources
    input_files = [
        ("../output_all.json", "studapart"),
        ("../data_paris.json", "lacartedescolocs"),
    ]
    
    # Filter existing files
    existing_files = [(f, s) for f, s in input_files if Path(f).exists()]
    
    if not existing_files:
        print("No input files found. Please run the spiders first.")
        print("Expected files: output_studapart.json, output_lacartedescolocs.json")
    else:
        merged_data = merge_datasets(existing_files)
        save_merged(merged_data, "merged_rentals.json")
