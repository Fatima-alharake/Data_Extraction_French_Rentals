-- =============================================================================
-- SQL Queries for Paris Rental Data Analysis
-- =============================================================================

-- -----------------------------------------------------------------------------
-- QUERY 1: Average Price by Arrondissement
-- Used for: Bar chart visualization of rental prices across Paris districts
-- -----------------------------------------------------------------------------
SELECT 
    arrondissement,
    COUNT(*) as listing_count,
    ROUND(AVG(price_eur), 2) as avg_price,
    ROUND(MIN(price_eur), 2) as min_price,
    ROUND(MAX(price_eur), 2) as max_price,
    ROUND(AVG(price_per_m2), 2) as avg_price_per_m2
FROM rentals
WHERE arrondissement IS NOT NULL 
  AND price_eur IS NOT NULL
  AND price_eur > 0
GROUP BY arrondissement
ORDER BY CAST(arrondissement AS INTEGER);


-- -----------------------------------------------------------------------------
-- QUERY 2: Price Distribution by Size Category
-- Used for: Box plot or histogram of price ranges by apartment size
-- -----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN size_m2 < 20 THEN '< 20 m²'
        WHEN size_m2 BETWEEN 20 AND 30 THEN '20-30 m²'
        WHEN size_m2 BETWEEN 31 AND 50 THEN '31-50 m²'
        WHEN size_m2 BETWEEN 51 AND 80 THEN '51-80 m²'
        WHEN size_m2 > 80 THEN '> 80 m²'
        ELSE 'Unknown'
    END as size_category,
    COUNT(*) as listing_count,
    ROUND(AVG(price_eur), 2) as avg_price,
    ROUND(AVG(price_per_m2), 2) as avg_price_per_m2
FROM rentals
WHERE size_m2 IS NOT NULL 
  AND price_eur IS NOT NULL
  AND size_m2 > 0
GROUP BY size_category
ORDER BY 
    CASE size_category
        WHEN '< 20 m²' THEN 1
        WHEN '20-30 m²' THEN 2
        WHEN '31-50 m²' THEN 3
        WHEN '51-80 m²' THEN 4
        WHEN '> 80 m²' THEN 5
        ELSE 6
    END;


-- -----------------------------------------------------------------------------
-- QUERY 3: Rental Type Distribution
-- Used for: Pie chart showing distribution of rental types
-- -----------------------------------------------------------------------------
SELECT 
    COALESCE(rental_type, 'Non spécifié') as rental_type,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM rentals), 2) as percentage
FROM rentals
GROUP BY rental_type
ORDER BY count DESC;


-- -----------------------------------------------------------------------------
-- QUERY 4: Data Source Comparison
-- Used for: Comparing data between Studapart and La Carte des Colocs
-- -----------------------------------------------------------------------------
SELECT 
    source,
    COUNT(*) as total_listings,
    ROUND(AVG(price_eur), 2) as avg_price,
    ROUND(AVG(size_m2), 2) as avg_size,
    ROUND(AVG(price_per_m2), 2) as avg_price_per_m2,
    SUM(CASE WHEN furnished IS NOT NULL THEN 1 ELSE 0 END) as furnished_count
FROM rentals
WHERE price_eur IS NOT NULL
GROUP BY source;


-- -----------------------------------------------------------------------------
-- QUERY 5: Price per m² by Arrondissement (for scatter plot)
-- Used for: Scatter plot showing price/m² vs arrondissement
-- -----------------------------------------------------------------------------
SELECT 
    arrondissement,
    price_per_m2,
    size_m2,
    price_eur
FROM rentals
WHERE arrondissement IS NOT NULL 
  AND price_per_m2 IS NOT NULL
  AND price_per_m2 > 0
  AND price_per_m2 < 100  -- Filter outliers
ORDER BY CAST(arrondissement AS INTEGER);


-- -----------------------------------------------------------------------------
-- QUERY 6: Top 10 Most Expensive Listings
-- Used for: Table or highlight visualization
-- -----------------------------------------------------------------------------
SELECT 
    title,
    arrondissement,
    price_eur,
    size_m2,
    price_per_m2,
    rooms,
    source
FROM rentals
WHERE price_eur IS NOT NULL
ORDER BY price_eur DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- QUERY 7: Furnished vs Unfurnished Price Comparison
-- Used for: Grouped bar chart
-- -----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN furnished IS NOT NULL THEN 'Meublé'
        ELSE 'Non meublé / Non spécifié'
    END as furnished_status,
    COUNT(*) as count,
    ROUND(AVG(price_eur), 2) as avg_price,
    ROUND(AVG(price_per_m2), 2) as avg_price_per_m2
FROM rentals
WHERE price_eur IS NOT NULL
GROUP BY furnished_status;
