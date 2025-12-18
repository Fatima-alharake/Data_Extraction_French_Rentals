# Data Storage in SQL Server

Note: This database was designed in a way that would be helpful if we were scraping a large amount of ads, and all the information that is on the sites, hence there would be information scraped that is available in one site and not in the other. For our project, we didn't use this database schema instead we used the one in the data analysis folder.

In the 'french_rentals_sql.sql' file, the scraped data is loaded into two separate tables, one for each rental website. This design choice simplifies classification and future usage if the data is later displayed on a website since it avoids the need to parse URLs to determine the source platform. 
In addition, this approach keeps the tables well organized as more attributes are scraped from each site. Since not all attributes are shared between sources, separating the data helps avoid excessive NULL values and maintains a cleaner, more efficient table structure.
The URL itself is not used as a primary key. Using a long string as a primary key would result in a large index size and potentially slower indexing performance. Instead, each URL is stored as a regular column and paired with a hash-based identifier to guarantee uniqueness while keeping the primary key compact and efficient.
Geographic coordinates (latitude and longitude) are stored as FLOAT values. The DECIMAL data type was avoided because it caused precision issues in SQL Server and did not reliably preserve decimal points.
Each scraped JSON file is loaded into its corresponding table. Before insertion, NULL values are handled as follows:
For string-based fields, NULL values are replaced with '-' to ensure consistency when displaying data.
For numeric fields, NULL values are preserved to accurately represent missing data.
These tables are structured to support efficient querying and can be directly used to display rental listings from both platforms in a unified and consistent format.
