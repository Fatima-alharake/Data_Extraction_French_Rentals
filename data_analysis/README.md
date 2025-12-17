# Data Analysis Module

This folder contains scripts for processing, storing, and visualizing the Paris rental data collected by the web scrapers.

## Pipeline Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  JSON Files     │ ──▶ │  merge_data.py  │ ──▶ │ create_database │ ──▶ │ visualizations  │
│  (from spiders) │     │                 │     │     .py         │     │     .py         │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Files

| File | Description |
|------|-------------|
| `merge_data.py` | Merges JSON outputs from multiple spiders into a single dataset |
| `create_database.py` | Creates SQLite database with proper schema and indexes |
| `sql_queries.sql` | Collection of SQL queries for data analysis |
| `visualizations.py` | Python script to generate charts and plots |

## Usage

### Step 1: Merge Data
```bash
python merge_data.py
```
**Input:** `output_studapart.json`, `output_lacartedescolocs.json`  
**Output:** `merged_rentals.json`

### Step 2: Create Database
```bash
python create_database.py
```
**Input:** `merged_rentals.json`  
**Output:** `paris_rentals.db`

### Step 3: Generate Visualizations
```bash
python visualizations.py
```
**Input:** `paris_rentals.db`  
**Output:** `plots/` directory with PNG images

## Visualizations

### 1. Average Price by Arrondissement
- **Type:** Bar Chart
- **Purpose:** Compare rental prices across Paris districts
- **Insights:** Identify expensive vs affordable areas

### 2. Price Distribution by Size Category
- **Type:** Box Plot
- **Purpose:** Analyze price ranges for different apartment sizes
- **Insights:** Understand price variability and outliers

### 3. Rental Type Distribution
- **Type:** Pie Chart
- **Purpose:** Show market composition by property type
- **Insights:** Understand what types of rentals are most common

## Database Schema

```sql
CREATE TABLE rentals (
    id TEXT PRIMARY KEY,
    source TEXT,              -- 'studapart' or 'lacartedescolocs'
    url TEXT,
    title TEXT,
    price_eur REAL,
    address TEXT,
    arrondissement TEXT,      -- Extracted from address (01-20)
    size_m2 REAL,
    price_per_m2 REAL,        -- Calculated field
    rooms INTEGER,
    floor TEXT,
    rental_type TEXT,
    furnished TEXT,
    latitude REAL,
    longitude REAL
);
```

## Requirements

```
pandas
matplotlib
numpy
```

Install with:
```bash
pip install pandas matplotlib numpy
```
