"""
Create SQLite database from merged JSON rental data.
"""

import json
import sqlite3
import re
from pathlib import Path


# Paris arrondissement boundaries (approximate polygons using bounding boxes)
# Based on central point of each arrondissement
ARRONDISSEMENT_CENTERS = {
    "01": (48.8600, 2.3425),
    "02": (48.8680, 2.3410),
    "03": (48.8640, 2.3590),
    "04": (48.8540, 2.3570),
    "05": (48.8460, 2.3500),
    "06": (48.8510, 2.3320),
    "07": (48.8570, 2.3150),
    "08": (48.8760, 2.3100),
    "09": (48.8770, 2.3370),
    "10": (48.8760, 2.3600),
    "11": (48.8590, 2.3800),
    "12": (48.8400, 2.3880),
    "13": (48.8320, 2.3600),
    "14": (48.8300, 2.3270),
    "15": (48.8410, 2.2930),
    "16": (48.8630, 2.2680),
    "17": (48.8880, 2.3050),
    "18": (48.8920, 2.3480),
    "19": (48.8850, 2.3820),
    "20": (48.8640, 2.3980),
}


def get_arrondissement_from_coords(lat: float, lon: float) -> str:
    """
    Determine Paris arrondissement from GPS coordinates.
    Uses nearest neighbor to arrondissement centers.
    Returns None if outside Paris bounds.
    """
    if lat is None or lon is None:
        return None
    
    # Paris bounding box (approximate)
    if not (48.815 <= lat <= 48.905 and 2.22 <= lon <= 2.47):
        return None
    
    # Find nearest arrondissement center
    min_dist = float('inf')
    nearest_arr = None
    
    for arr, (center_lat, center_lon) in ARRONDISSEMENT_CENTERS.items():
        # Simple Euclidean distance (sufficient for small area)
        dist = ((lat - center_lat) ** 2 + (lon - center_lon) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            nearest_arr = arr
    
    return nearest_arr


def extract_arrondissement(address: str) -> str:
    """
    Extract Paris arrondissement from address string.
    Only returns valid Paris arrondissements (01-20).
    """
    if not address:
        return None
    
    address_lower = address.lower()
    
    # Pattern 1: Postal code 750XX (75001-75020)
    match = re.search(r"750(\d{2})", address)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 20:
            return str(num).zfill(2)
    
    # Pattern 2: "Paris 11", "Paris 11e", "Paris 11ème", "Paris 11er"
    match = re.search(r"paris\s*(\d{1,2})(?:e|ème|er|eme)?\b", address_lower)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 20:
            return str(num).zfill(2)
    
    # Pattern 3: "11e arrondissement", "11ème arrondissement"
    match = re.search(r"(\d{1,2})(?:e|ème|er|eme)?\s*arrondissement", address_lower)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 20:
            return str(num).zfill(2)
    
    # Pattern 4: Just "Paris" without number (central/unknown)
    # Don't return anything, keep as NULL
    
    return None


def safe_float(value) -> float:
    """Safely convert value to float."""
    if value is None:
        return None
    try:
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r"[^\d.]", "", str(value))
        return float(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None


def safe_int(value) -> int:
    """Safely convert value to integer."""
    if value is None:
        return None
    try:
        cleaned = re.sub(r"[^\d]", "", str(value))
        return int(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None


def create_tables(conn: sqlite3.Connection):
    """Create the rentals table."""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rentals (
            id TEXT PRIMARY KEY,
            source TEXT,
            url TEXT,
            title TEXT,
            price_eur REAL,
            address TEXT,
            arrondissement TEXT,
            size_m2 REAL,
            price_per_m2 REAL,
            rooms INTEGER,
            floor TEXT,
            rental_type TEXT,
            furnished TEXT,
            latitude REAL,
            longitude REAL
        )
    """)
    
    # Create indexes for common queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_arrondissement ON rentals(arrondissement)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price ON rentals(price_eur)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON rentals(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rental_type ON rentals(rental_type)")
    
    conn.commit()
    print("Tables and indexes created successfully.")


def insert_data(conn: sqlite3.Connection, data: list[dict]):
    """Insert rental data into the database."""
    cursor = conn.cursor()
    
    inserted = 0
    skipped = 0
    geo_resolved = 0
    
    for record in data:
        price = safe_float(record.get("price_eur"))
        size = safe_float(record.get("size_m2"))
        lat = safe_float(record.get("latitude"))
        lon = safe_float(record.get("longitude"))
        
        # Try to extract arrondissement from address first
        arrondissement = extract_arrondissement(record.get("address"))
        
        # If not found in address, try to determine from coordinates
        if arrondissement is None and lat and lon:
            arrondissement = get_arrondissement_from_coords(lat, lon)
            if arrondissement:
                geo_resolved += 1
        
        # Calculate price per m2
        price_per_m2 = None
        if price and size and size > 0:
            price_per_m2 = round(price / size, 2)
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO rentals 
                (id, source, url, title, price_eur, address, arrondissement,
                 size_m2, price_per_m2, rooms, floor, rental_type, furnished,
                 latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.get("id"),
                record.get("source"),
                record.get("url"),
                record.get("title"),
                price,
                record.get("address"),
                arrondissement,
                size,
                price_per_m2,
                safe_int(record.get("rooms")),
                record.get("floor"),
                record.get("rental_type"),
                record.get("furnished"),
                safe_float(record.get("latitude")),
                safe_float(record.get("longitude")),
            ))
            inserted += 1
        except sqlite3.Error as e:
            print(f"Error inserting record: {e}")
            skipped += 1
    
    conn.commit()
    print(f"Inserted: {inserted}, Skipped: {skipped}, Geo-resolved: {geo_resolved}")


def print_summary(conn: sqlite3.Connection):
    """Print database summary statistics."""
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("DATABASE SUMMARY")
    print("="*50)
    
    # Total records
    cursor.execute("SELECT COUNT(*) FROM rentals")
    print(f"Total rentals: {cursor.fetchone()[0]}")
    
    # By source
    cursor.execute("SELECT source, COUNT(*) FROM rentals GROUP BY source")
    print("\nBy source:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    # By arrondissement (top 5)
    cursor.execute("""
        SELECT arrondissement, COUNT(*) as cnt 
        FROM rentals 
        WHERE arrondissement IS NOT NULL 
        GROUP BY arrondissement 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    print("\nTop 5 arrondissements:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}e: {row[1]} listings")
    
    # Price stats
    cursor.execute("""
        SELECT 
            ROUND(AVG(price_eur), 2),
            ROUND(MIN(price_eur), 2),
            ROUND(MAX(price_eur), 2)
        FROM rentals 
        WHERE price_eur IS NOT NULL
    """)
    avg, min_p, max_p = cursor.fetchone()
    print(f"\nPrice stats (EUR): Avg={avg}, Min={min_p}, Max={max_p}")


if __name__ == "__main__":
    json_path = "merged_rentals.json"
    db_path = "paris_rentals.db"
    
    if not Path(json_path).exists():
        print(f"Error: {json_path} not found. Run merge_data.py first.")
        exit(1)
    
    # Load JSON data
    print(f"Loading {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Create database
    print(f"Creating database {db_path}...")
    conn = sqlite3.connect(db_path)
    
    create_tables(conn)
    insert_data(conn, data)
    print_summary(conn)
    
    conn.close()
    print(f"\nDatabase saved to {db_path}")
