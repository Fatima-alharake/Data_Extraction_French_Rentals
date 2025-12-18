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

