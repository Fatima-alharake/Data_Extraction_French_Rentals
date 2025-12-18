# French Rental Market Dataset 

This project is designed to scrape, store, and analyze rental data from various French housing platforms. It includes a Scrapy-based web crawler, SQL integration for data management, and some data analysis to visualize the data.

## Project Structure

The project is organized into three primary modules:

* **`French_Rentals/`**: The core Scrapy project containing the web crawlers and scraping logic.
* **`Data_Analysis/`**: Contains scripts for processing the scraped data and generating visualizations .
* **`SQL_Files/`**: Contains database schemas and SQL scripts for data persistence.

### File Inventory

```text
├── Data_Analysis/          # Data processing and visualization logic
├── French_Rentals/         # Scrapy project root
│   └── spiders/            # Directory for all spider definitions
├── SQL_Files/              # SQL scripts and database configurations
├── data_paris.json         # Raw scraped data (Paris specific)
├── output_all.json         # Aggregated scraped data
├── heatmap_paris.html      # Generated geographic visualization
├── scrapy.cfg              # Scrapy configuration file
└── .gitignore              # Files excluded from version control

```

---

## Getting Started

Ensure you have Python installed along with the Scrapy framework:

```bash
pip install scrapy

```

### Running the Scrapers

All scraping commands should be executed from within the `French_Rentals` directory.

To crawl listings from La Carte des Colocs and save them to a JSON file:

```bash
scrapy crawl lacartedescolocs_spider -O data_paris.json

```
To crawl listings from Studapart and save them to a JSON file:

```bash
scrapy crawl studapart_spider -O data_paris.json

```


If you wish to add a new platform to the scraping list, create a new spider file in the following directory:
`French_Rentals/spiders/`

Once the file is created, you can run it using the standard `scrapy crawl [spider_name]` command.

---

## Data Analysis Module

This folder contains scripts for processing, storing, and visualizing the Paris rental data collected by the web scrapers.

### Files

| File | Description |
|------|-------------|
| `merge_data.py` | Merges JSON outputs from multiple spiders into a single dataset |
| `create_database.py` | Creates SQLite database with proper schema and indexes |
| `sql_queries.sql` | Collection of SQL queries for data analysis |
| `visualizations.py` | Python script to generate charts and plots |

### Usage

#### Merge Data
```bash
python merge_data.py
```
**Input:** `output_studapart.json`, `output_lacartedescolocs.json`  
**Output:** `merged_rentals.json`

#### Create Database
```bash
python create_database.py
```
**Input:** `merged_rentals.json`  
**Output:** `paris_rentals.db`

#### Generate Visualizations
```bash
python visualizations.py
```
**Input:** `paris_rentals.db`  
**Output:** `plots/` directory with PNG images

### Database Schema

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