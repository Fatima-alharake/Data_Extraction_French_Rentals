import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

try:
    df = pd.read_json('merged_rentals.json')
except ValueError:
    print("Error: check your json file.")
    exit()

numeric_cols = ['price_eur', 'size_m2', 'rooms']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df_clean = df[
    (df['price_eur'] < 5000) & 
    (df['rooms'] < 10) & 
    (df['size_m2'] < 500)
].dropna(subset=['price_eur', 'size_m2', 'rooms'])

print(f"Plotting {len(df_clean)} records.")

sns.set_theme(style="whitegrid", context="talk")
palette = sns.color_palette("viridis")

fig = plt.figure(figsize=(20, 12))
gs = gridspec.GridSpec(2, 3, figure=fig, height_ratios=[1, 1.2], wspace=0.3, hspace=0.4)

ax1 = fig.add_subplot(gs[0, 0])
sns.histplot(data=df_clean, x='price_eur', kde=True, color=palette[0], ax=ax1, element="step")
ax1.set_title('Price Distribution (€)', fontweight='bold')
ax1.set_xlabel('Price (€)')

ax2 = fig.add_subplot(gs[0, 1])
sns.histplot(data=df_clean, x='size_m2', kde=True, color=palette[2], ax=ax2, element="step")
ax2.set_title('Size Distribution (m²)', fontweight='bold')
ax2.set_xlabel('Size (m²)')

ax3 = fig.add_subplot(gs[0, 2])
sns.countplot(data=df_clean, x='rooms', palette="viridis", ax=ax3)
ax3.set_title('Number of Rooms', fontweight='bold')
ax3.set_xlabel('Rooms')
ax3.set_ylabel('Count')

ax4 = fig.add_subplot(gs[1, 0])
top_rental_types = df_clean['rental_type'].value_counts().nlargest(10).index

sns.countplot(data=df_clean[df_clean['rental_type'].isin(top_rental_types)], 
              y='rental_type', 
              palette="rocket", 
              order=top_rental_types, 
              ax=ax4)

ax4.set_xscale('log') 
ax4.set_title('Top Rental Types (Log Scale)', fontweight='bold')
ax4.set_xlabel('Count (Logarithmic)')
ax4.set_ylabel('')
ax4.grid(True, which="both", axis="x", ls="--", alpha=0.5)

ax5 = fig.add_subplot(gs[1, 1:])
sns.scatterplot(data=df_clean, x='size_m2', y='price_eur', 
                hue='rooms', size='rooms', sizes=(50, 300), 
                palette="viridis", ax=ax5, alpha=0.7)

sns.regplot(data=df_clean, x='size_m2', y='price_eur', scatter=False, 
            ax=ax5, color='grey', line_kws={"linestyle": "--", "alpha": 0.5})

ax5.set_title('Correlation: Size (m²) vs. Price (€)', fontweight='bold')
ax5.set_xlabel('Size (m²)')
ax5.set_ylabel('Price (€)')
ax5.legend(title='Rooms', bbox_to_anchor=(1, 1), loc='upper left')

plt.suptitle('Rental Market Analysis', fontsize=24, fontweight='bold', y=0.95)
sns.despine()

plt.savefig('rental_analysis_log.png', bbox_inches='tight', dpi=150)
print("Graph saved as 'rental_analysis_log.png'")
plt.show()