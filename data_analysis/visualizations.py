"""
Visualizations for Paris Rental Data Analysis.
"""

import sqlite3
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend - prevents blocking
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Set style for better looking plots
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

COLORS = {
    'primary': '#1a365d',    
    'secondary': '#c53030',    
    'accent': '#2c5282',       
    'light': '#bee3f8',       
    'gradient': plt.cm.Blues, 
}


def get_connection(db_path: str = "paris_rentals.db") -> sqlite3.Connection:
    """Get database connection."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database {db_path} not found. Run create_database.py first.")
    return sqlite3.connect(db_path)



# Average Price by Arrondissement
def plot_price_by_arrondissement(conn: sqlite3.Connection, save_path: str = None):
    """
    Bar chart showing average rental prices by Paris arrondissement.
    """
    query = """
        SELECT 
            arrondissement,
            COUNT(*) as listing_count,
            ROUND(AVG(price_eur), 2) as avg_price,
            ROUND(AVG(price_per_m2), 2) as avg_price_per_m2
        FROM rentals
        WHERE arrondissement IS NOT NULL 
          AND price_eur IS NOT NULL
          AND price_eur > 0
        GROUP BY arrondissement
        ORDER BY CAST(arrondissement AS INTEGER)
    """
    
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No data available for arrondissement visualization.")
        return
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Create bar positions
    x = np.arange(len(df))
    width = 0.6
    
    # Color bars by price (gradient)
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(df)))
    
    bars = ax.bar(x, df['avg_price'], width, color=colors, edgecolor='white', linewidth=0.7)
    
    # Add value labels on bars
    for bar, count in zip(bars, df['listing_count']):
        height = bar.get_height()
        ax.annotate(f'€{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        # Add listing count at bottom
        ax.annotate(f'n={count}',
                    xy=(bar.get_x() + bar.get_width() / 2, 0),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, color='gray')
    
    # Customize axes
    ax.set_xlabel('Arrondissement', fontweight='bold')
    ax.set_ylabel('Average Monthly Rent (€)', fontweight='bold')
    ax.set_title('Average Rental Prices by Paris Arrondissement', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{arr}e" for arr in df['arrondissement']], rotation=45, ha='right')
    
    # Add average line
    avg_all = df['avg_price'].mean()
    ax.axhline(y=avg_all, color=COLORS['secondary'], linestyle='--', linewidth=2, label=f'Paris Average: €{avg_all:.0f}')
    ax.legend(loc='upper right')
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")
    
    plt.close()  # Close figure to free memory


# Average Price by Arrondissement (SHARED ONLY)
def plot_price_by_arrondissement_shared(conn: sqlite3.Connection, save_path: str = None):
    """
    Bar chart showing average rental prices by Paris arrondissement.
    SHARED ACCOMMODATIONS ONLY (La Carte des Colocs).
    """
    query = """
        SELECT 
            arrondissement,
            COUNT(*) as listing_count,
            ROUND(AVG(price_eur), 2) as avg_price,
            ROUND(AVG(price_per_m2), 2) as avg_price_per_m2
        FROM rentals
        WHERE arrondissement IS NOT NULL 
          AND price_eur IS NOT NULL
          AND price_eur > 0
          AND source = 'lacartedescolocs'  -- SHARED ONLY
        GROUP BY arrondissement
        ORDER BY CAST(arrondissement AS INTEGER)
    """
    
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No data available for shared arrondissement visualization.")
        return
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Create bar positions
    x = np.arange(len(df))
    width = 0.6
    
    # Color bars with orange gradient (shared = orange theme)
    colors = plt.cm.Oranges(np.linspace(0.3, 0.8, len(df)))
    
    bars = ax.bar(x, df['avg_price'], width, color=colors, edgecolor='white', linewidth=0.7)
    
    # Add value labels on bars
    for bar, count in zip(bars, df['listing_count']):
        height = bar.get_height()
        ax.annotate(f'€{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        # Add listing count at bottom
        ax.annotate(f'n={count}',
                    xy=(bar.get_x() + bar.get_width() / 2, 0),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, color='gray')
    
    # Customize axes
    ax.set_xlabel('Arrondissement', fontweight='bold')
    ax.set_ylabel('Average Monthly Rent (€)', fontweight='bold')
    ax.set_title('Shared Accommodation Prices by Paris Arrondissement\n(La Carte des Colocs - Room in shared housing)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{arr}e" for arr in df['arrondissement']], rotation=45, ha='right')
    
    # Add average line
    avg_all = df['avg_price'].mean()
    ax.axhline(y=avg_all, color=COLORS['secondary'], linestyle='--', linewidth=2, label=f'Shared Average: €{avg_all:.0f}')
    ax.legend(loc='upper right')
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")
    
    plt.close()  # Close figure to free memory


# Price Distribution by Size - SHARED ONLY (PARIS ONLY)
def plot_price_by_size_comparison(conn: sqlite3.Connection, save_path_shared: str = None):
    """
    Box plot showing price distribution by size for shared accommodations (PARIS ONLY).
    """
    query = """
        SELECT 
            CASE 
                WHEN size_m2 < 20 THEN '< 20 m²'
                WHEN size_m2 BETWEEN 20 AND 30 THEN '20-30 m²'
                WHEN size_m2 BETWEEN 31 AND 50 THEN '31-50 m²'
                WHEN size_m2 BETWEEN 51 AND 80 THEN '51-80 m²'
                WHEN size_m2 > 80 THEN '> 80 m²'
            END as size_category,
            price_eur
        FROM rentals
        WHERE size_m2 IS NOT NULL 
          AND price_eur IS NOT NULL
          AND size_m2 > 0
          AND price_eur > 0
          AND price_eur < 5000  -- Filter extreme outliers
          AND arrondissement IS NOT NULL  -- PARIS ONLY
          AND source = 'lacartedescolocs'  -- SHARED ONLY
    """
    
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No data available for size category visualization.")
        return
    
    # Define category order
    size_order = ['< 20 m²', '20-30 m²', '31-50 m²', '51-80 m²', '> 80 m²']
    df['size_category'] = pd.Categorical(df['size_category'], categories=size_order, ordered=True)
    df = df.dropna(subset=['size_category'])
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    categories = [cat for cat in size_order if cat in df['size_category'].values]
    data = [df[df['size_category'] == cat]['price_eur'].values for cat in categories]
    
    # Filter out empty categories
    non_empty = [(cat, d) for cat, d in zip(categories, data) if len(d) > 0]
    if not non_empty:
        print("No data points for shared size visualization")
        plt.close()
        return
    categories, data = zip(*non_empty)
    
    bp = ax.boxplot(data, patch_artist=True, labels=categories)
    
    colors = plt.cm.Oranges(np.linspace(0.3, 0.8, len(categories)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)
    
    for whisker in bp['whiskers']:
        whisker.set(color=COLORS['primary'], linewidth=1.5)
    for cap in bp['caps']:
        cap.set(color=COLORS['primary'], linewidth=1.5)
    for median in bp['medians']:
        median.set(color=COLORS['secondary'], linewidth=2)
    
    # Add count and median annotations
    for i, cat in enumerate(categories):
        count = len(df[df['size_category'] == cat])
        median_val = df[df['size_category'] == cat]['price_eur'].median()
        ax.annotate(f'n={count}', xy=(i + 1, ax.get_ylim()[0]), 
                    xytext=(0, 10), textcoords='offset points',
                    ha='center', fontsize=9, color='gray')
        ax.annotate(f'€{median_val:.0f}', xy=(i + 1, median_val), 
                    xytext=(0, 5), textcoords='offset points',
                    ha='center', fontsize=8, color=COLORS['secondary'], fontweight='bold')
    
    ax.set_xlabel('Apartment Size (Total)', fontweight='bold')
    ax.set_ylabel('Monthly Rent (€)', fontweight='bold')
    ax.set_title('Shared Accommodation Prices by Size\n(La Carte des Colocs - Price per room in shared housing)', 
                 fontsize=14, fontweight='bold', pad=15)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path_shared:
        plt.savefig(save_path_shared, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path_shared}")
    
    plt.close()


# main to generate all
def generate_all_visualizations():
    """Generate and save all visualizations."""
    print("="*60)
    print("GENERATING PARIS RENTAL VISUALIZATIONS")
    print("="*60)
    
    try:
        conn = get_connection()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Create output directory
    output_dir = Path("plots")
    output_dir.mkdir(exist_ok=True)
    
    print("\n1. Generating Price by Arrondissement chart (ALL)...")
    plot_price_by_arrondissement(conn, str(output_dir / "price_by_arrondissement.png"))
    
    print("\n2. Generating Price by Arrondissement chart (SHARED ONLY)...")
    plot_price_by_arrondissement_shared(conn, str(output_dir / "price_by_arrondissement_shared.png"))
    
    print("\n3. Generating Price by Size chart (SHARED ONLY)...")
    plot_price_by_size_comparison(
        conn, 
        save_path_shared=str(output_dir / "price_by_size_shared.png")
    )
    
    conn.close()
    
    print("\n" + "="*60)
    print("All visualizations saved to 'plots/' directory")
    print("="*60)


if __name__ == "__main__":
    generate_all_visualizations()
