
# --------------------------------------------------
# Afficionado Coffee Roasters
# Product Optimization & Revenue Analytics Dashboard
# --------------------------------------------------

# Import the required libraries
import streamlit as st
import pandas as pd
import numpy as np

# --------------------------------------------------
# 1. Configure the Streamlit page
# --------------------------------------------------

# Set the browser tab title, layout, and sidebar state
st.set_page_config(
    page_title="Afficionado Coffee Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. Display the dashboard heading
# --------------------------------------------------

st.title("☕ Afficionado Coffee Roasters")
st.subheader("Product Optimization & Revenue Analytics")

st.markdown("""
Explore product sales, revenue contribution, category performance,
and store-level business insights through this interactive dashboard.
""")

# Add a visual divider below the introduction
st.divider()

# --------------------------------------------------
# 3. Load the dataset
# --------------------------------------------------

# Define the relative path to the CSV file
DATA_PATH = "Data/Afficionado_Coffee_Roasters.csv"

# Use a cached function to avoid repeatedly reading the CSV
@st.cache_data
def load_data(file_path):
    """Load the coffee roasters transaction dataset."""
    data = pd.read_csv(file_path)
    return data

# Attempt to load the dataset
try:
    df = load_data(DATA_PATH)

except FileNotFoundError:
    st.error(
        "Dataset not found. Please check that the CSV file "
        "is inside the Data folder and the filename is correct."
    )
    st.stop()

# --------------------------------------------------
# 4. Prepare the data
# --------------------------------------------------

# Calculate revenue for each transaction record
df["revenue"] = df["transaction_qty"] * df["unit_price"]

# Display a success message after loading the dataset
st.success("Dataset loaded successfully!")

# --------------------------------------------------
# 5. Create interactive sidebar filters
# --------------------------------------------------

st.sidebar.title("Dashboard Filters")

st.sidebar.markdown(
    "Use the filters below to explore product performance."
)

# --------------------------------------------------
# 5.1 Product Category Filter
# --------------------------------------------------

# Get all unique product categories
categories = sorted(df["product_category"].dropna().unique())

# Add an All option to show every category
category_options = ["All"] + categories

selected_category = st.sidebar.selectbox(
    "Select Product Category",
    options=category_options
)

# --------------------------------------------------
# 5.2 Product Type Filter
# --------------------------------------------------

# Start with the complete dataset
category_filtered_df = df.copy()

# Apply the selected category before generating product types
if selected_category != "All":
    category_filtered_df = category_filtered_df[
        category_filtered_df["product_category"] == selected_category
    ]

# Get product types available under the selected category
product_types = sorted(
    category_filtered_df["product_type"].dropna().unique()
)

# Add an All option
product_type_options = ["All"] + product_types

selected_product_type = st.sidebar.selectbox(
    "Select Product Type",
    options=product_type_options
)

# --------------------------------------------------
# 5.3 Store Location Filter
# --------------------------------------------------

# Get all unique store locations
store_locations = sorted(
    df["store_location"].dropna().unique()
)

# Add an All option
store_options = ["All"] + store_locations

selected_store = st.sidebar.selectbox(
    "Select Store Location",
    options=store_options
)

# --------------------------------------------------
# 5.4 Apply all selected filters
# --------------------------------------------------

# Create a filtered copy of the original dataset
filtered_df = df.copy()

# Apply category filter
if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["product_category"] == selected_category
    ]

# Apply product type filter
if selected_product_type != "All":
    filtered_df = filtered_df[
        filtered_df["product_type"] == selected_product_type
    ]

# Apply store location filter
if selected_store != "All":
    filtered_df = filtered_df[
        filtered_df["store_location"] == selected_store
    ]

# Display the number of records remaining after filtering
st.sidebar.divider()

st.sidebar.metric(
    "Filtered Transaction Records",
    f"{len(filtered_df):,}"
)

# --------------------------------------------------
# 5. Display basic dataset information
# --------------------------------------------------

# Show the dataset dimensions and key business metrics
st.divider()
st.header("Business Overview")

# Calculate summary metrics using filtered data
total_revenue = filtered_df["revenue"].sum()
total_units_sold = filtered_df["transaction_qty"].sum()
total_records = len(filtered_df)
total_products = filtered_df["product_id"].nunique()

# Display the metrics in four columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Revenue",
        value=f"{total_revenue:,.2f}"
    )

with col2:
    st.metric(
        label="Units Sold",
        value=f"{total_units_sold:,}"
    )

with col3:
    st.metric(
        label="Transaction Records",
        value=f"{total_records:,}"
    )

with col4:
    st.metric(
        label="Unique Products",
        value=f"{total_products:,}"
    )

# --------------------------------------------------
# 6. Display a data preview
# --------------------------------------------------

st.divider()
st.header("Dataset Preview")

# Allow users to choose how many rows to preview
preview_rows = st.selectbox(
    "Number of rows to display",
    options=[5, 10, 20, 50],
    index=1
)

# Display the selected number of rows
st.dataframe(
    filtered_df.head(preview_rows),
    use_container_width=True
)

# --------------------------------------------------
# 6. Product Ranking Analysis
# --------------------------------------------------

st.divider()
st.header("Product Performance Rankings")

# Aggregate sales data at product level
product_summary = (
    filtered_df.groupby(
        ["product_id", "product_detail"]
    )
    .agg(
        total_units_sold=("transaction_qty", "sum"),
        total_transactions=("transaction_id", "count"),
        total_revenue=("revenue", "sum")
    )
    .reset_index()
)

# Calculate each product's percentage contribution
# to the revenue of the currently filtered dataset
filtered_total_revenue = filtered_df["revenue"].sum()

product_summary["revenue_contribution_pct"] = (
    product_summary["total_revenue"]
    / filtered_total_revenue * 100
    if filtered_total_revenue > 0
    else 0
)

# --------------------------------------------------
# 6.1 Top-N Product Selection
# --------------------------------------------------

top_n = st.slider(
    "Select Number of Top Products",
    min_value=5,
    max_value=30,
    value=10,
    step=5
)

# --------------------------------------------------
# 6.2 Rank Products by Sales Volume
# --------------------------------------------------

top_volume_products = (
    product_summary
    .sort_values(
        by="total_units_sold",
        ascending=False
    )
    .head(top_n)
)

# --------------------------------------------------
# 6.3 Rank Products by Revenue
# --------------------------------------------------

top_revenue_products = (
    product_summary
    .sort_values(
        by="total_revenue",
        ascending=False
    )
    .head(top_n)
)

# --------------------------------------------------
# 6.4 Display Product Rankings
# --------------------------------------------------

col1, col2 = st.columns(2)

# Display ranking by sales volume
with col1:

    st.subheader("Top Products by Sales Volume")

    st.dataframe(
        top_volume_products[
            [
                "product_detail",
                "total_units_sold",
                "total_revenue"
            ]
        ].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

# Display ranking by revenue
with col2:

    st.subheader("Top Products by Revenue")

    st.dataframe(
        top_revenue_products[
            [
                "product_detail",
                "total_revenue",
                "total_units_sold",
                "revenue_contribution_pct"
            ]
        ].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 7. Category Revenue Distribution
# --------------------------------------------------

st.divider()
st.header("Category Revenue Distribution")

# Calculate revenue and unit sales for each category
category_summary = (
    filtered_df.groupby("product_category")
    .agg(
        total_revenue=("revenue", "sum"),
        total_units_sold=("transaction_qty", "sum")
    )
    .reset_index()
)

# Calculate each category's contribution to filtered revenue
category_total_revenue = filtered_df["revenue"].sum()

if category_total_revenue > 0:
    category_summary["revenue_contribution_pct"] = (
        category_summary["total_revenue"]
        / category_total_revenue * 100
    )
else:
    category_summary["revenue_contribution_pct"] = 0

# Sort categories by revenue contribution
category_summary = category_summary.sort_values(
    by="total_revenue",
    ascending=False
)

# Display the category performance table
st.dataframe(
    category_summary,
    use_container_width=True,
    hide_index=True
)


# Visualize revenue contribution by category
st.subheader("Revenue by Product Category")

import matplotlib.pyplot as plt

# Sort categories by revenue in descending order
chart_data = category_summary.sort_values(
    by="total_revenue",
    ascending=False
)

# Create the horizontal bar chart
fig, ax = plt.subplots(figsize=(10, 5))

ax.barh(
    chart_data["product_category"],
    chart_data["total_revenue"]
)

# Place the highest-revenue category at the top
ax.invert_yaxis()

# Set axis labels correctly
ax.set_xlabel("Total Revenue")
ax.set_ylabel("Product Category")

ax.set_title("Revenue Contribution by Product Category")

# Improve chart readability
ax.grid(axis="x", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()

# Display chart in Streamlit
st.pyplot(fig)

plt.close(fig)


# --------------------------------------------------
# 8. Popularity vs Revenue Analysis
# --------------------------------------------------

st.divider()
st.header("Popularity vs Revenue Analysis")

st.markdown("""
This analysis compares product sales volume with revenue generation.
Each point represents an individual product.
""")

# Calculate median values for reference lines
median_units = product_summary["total_units_sold"].median()
median_revenue = product_summary["total_revenue"].median()

# Create scatter plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(
    product_summary["total_units_sold"],
    product_summary["total_revenue"],
    alpha=0.7
)

# Add median reference lines
ax.axvline(
    median_units,
    linestyle="--",
    linewidth=1.5,
    label=f"Median Units: {median_units:,.0f}"
)

ax.axhline(
    median_revenue,
    linestyle="--",
    linewidth=1.5,
    label=f"Median Revenue: {median_revenue:,.2f}"
)

# Axis labels and title
ax.set_xlabel("Total Units Sold")
ax.set_ylabel("Total Revenue")
ax.set_title("Product Popularity vs Revenue")

# Grid and legend
ax.grid(linestyle="--", alpha=0.3)
ax.legend()

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# --------------------------------------------------
# 9. Product Performance Classification
# --------------------------------------------------

st.divider()
st.header("Product Performance Classification")

# Classify products based on median sales volume and revenue
product_summary["performance_group"] = np.select(
    [
        (product_summary["total_units_sold"] >= median_units) &
        (product_summary["total_revenue"] >= median_revenue),

        (product_summary["total_units_sold"] < median_units) &
        (product_summary["total_revenue"] >= median_revenue),

        (product_summary["total_units_sold"] >= median_units) &
        (product_summary["total_revenue"] < median_revenue)
    ],
    [
        "High Volume - High Revenue",
        "Low Volume - High Revenue",
        "High Volume - Low Revenue"
    ],
    default="Low Volume - Low Revenue"
)

# Count products in each performance group
performance_summary = (
    product_summary["performance_group"]
    .value_counts()
    .reset_index()
)

performance_summary.columns = [
    "Performance Group",
    "Number of Products"
]

# Calculate percentage of products in each group
performance_summary["Product Share (%)"] = (
    performance_summary["Number of Products"]
    / len(product_summary) * 100
    if len(product_summary) > 0
    else 0
)

st.subheader("Product Distribution by Performance Group")

st.dataframe(
    performance_summary,
    use_container_width=True,
    hide_index=True
)

# Visualize the number of products in each performance group
st.subheader("Product Distribution Across Performance Groups")

fig, ax = plt.subplots(figsize=(10, 5))

ax.barh(
    performance_summary["Performance Group"],
    performance_summary["Number of Products"]
)

ax.set_xlabel("Number of Products")
ax.set_ylabel("Performance Group")
ax.set_title("Product Performance Classification")

# Display the highest-count group at the top
ax.invert_yaxis()

# Add product counts beside the bars
for index, value in enumerate(performance_summary["Number of Products"]):
    ax.text(value + 0.3, index, str(value), va="center")

ax.grid(axis="x", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)


# --------------------------------------------------
# 10. Product-Level Drill-Down
# --------------------------------------------------

st.divider()
st.header("Product-Level Performance Drill-Down")

st.markdown("""
Select an individual product to explore its sales volume,
revenue contribution, and average revenue per unit.
""")

# Get available products from the filtered dataset
available_products = sorted(
    product_summary["product_detail"].dropna().unique()
)

selected_product = st.selectbox(
    "Select a Product",
    options=available_products
)

# Retrieve the selected product's performance details
selected_product_data = product_summary[
    product_summary["product_detail"] == selected_product
].iloc[0]



# Extract selected product metrics
product_units = selected_product_data["total_units_sold"]
product_revenue = selected_product_data["total_revenue"]
product_transactions = selected_product_data["total_transactions"]
product_contribution = selected_product_data["revenue_contribution_pct"]

# Calculate average revenue per unit
average_revenue_per_unit = (
    product_revenue / product_units
    if product_units > 0
    else 0
)

# Display product performance metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Units Sold",
        f"{product_units:,.0f}"
    )

with col2:
    st.metric(
        "Total Revenue",
        f"{product_revenue:,.2f}"
    )

with col3:
    st.metric(
        "Revenue Contribution",
        f"{product_contribution:.2f}%"
    )

with col4:
    st.metric(
        "Average Revenue per Unit",
        f"{average_revenue_per_unit:,.2f}"
    )




st.subheader("Selected Product Details")

st.write(f"**Product Name:** {selected_product}")

st.write(
    f"**Transaction Records:** {product_transactions:,.0f}"
)

st.write(
    f"**Performance Group:** "
    f"{selected_product_data['performance_group']}"
)




# --------------------------------------------------
# 11. Store Performance Analysis
# --------------------------------------------------

st.divider()
st.header("Store Performance Analysis")

st.markdown("""
Compare revenue generation and sales volume across different
store locations.
""")

# Aggregate sales performance by store
store_summary = (
    filtered_df.groupby("store_location")
    .agg(
        total_revenue=("revenue", "sum"),
        total_units_sold=("transaction_qty", "sum"),
        total_transactions=("transaction_id", "count")
    )
    .reset_index()
)

# Calculate each store's revenue contribution
store_total_revenue = filtered_df["revenue"].sum()

if store_total_revenue > 0:
    store_summary["revenue_contribution_pct"] = (
        store_summary["total_revenue"]
        / store_total_revenue * 100
    )
else:
    store_summary["revenue_contribution_pct"] = 0

# Sort stores by revenue
store_summary = store_summary.sort_values(
    by="total_revenue",
    ascending=False
)

st.subheader("Store Performance Summary")

st.dataframe(
    store_summary,
    use_container_width=True,
    hide_index=True
)



st.subheader("Revenue by Store Location")

fig, ax = plt.subplots(figsize=(9, 5))

chart_data = store_summary.sort_values(
    by="total_revenue",
    ascending=False
)

ax.barh(
    chart_data["store_location"],
    chart_data["total_revenue"]
)

ax.invert_yaxis()

ax.set_xlabel("Total Revenue")
ax.set_ylabel("Store Location")
ax.set_title("Revenue Comparison Across Store Locations")

ax.grid(axis="x", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)



# --------------------------------------------------
# 12. Time-of-Day Sales Analysis
# --------------------------------------------------

st.divider()
st.header("Time-of-Day Sales Analysis")

st.markdown("""
Explore sales activity throughout the day to identify
peak business hours and periods of lower activity.
""")

# Extract the hour from transaction_time
time_filtered_df = filtered_df.copy()

time_filtered_df["transaction_hour"] = pd.to_datetime(
    time_filtered_df["transaction_time"],
    format="%H:%M:%S",
    errors="coerce"
).dt.hour

# Aggregate sales by hour
hourly_summary = (
    time_filtered_df.dropna(subset=["transaction_hour"])
    .groupby("transaction_hour")
    .agg(
        total_revenue=("revenue", "sum"),
        total_units_sold=("transaction_qty", "sum"),
        total_transactions=("transaction_id", "count")
    )
    .reset_index()
)

# Sort chronologically
hourly_summary = hourly_summary.sort_values(
    by="transaction_hour"
)

st.subheader("Hourly Sales Summary")

st.dataframe(
    hourly_summary,
    use_container_width=True,
    hide_index=True
)



st.subheader("Revenue by Hour")

fig, ax = plt.subplots(figsize=(11, 5))

ax.bar(
    hourly_summary["transaction_hour"],
    hourly_summary["total_revenue"],
    width=0.7
)

ax.set_xlabel("Hour of Day")
ax.set_ylabel("Total Revenue")
ax.set_title("Hourly Revenue Distribution")

ax.set_xticks(range(6, 21))
ax.set_xticklabels([
    f"{hour:02d}:00" for hour in range(6, 21)
])

ax.grid(axis="y", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)



# Identify the hour with the highest revenue
if not hourly_summary.empty:

    peak_hour_data = hourly_summary.loc[
        hourly_summary["total_revenue"].idxmax()
    ]

    peak_hour = int(peak_hour_data["transaction_hour"])
    peak_revenue = peak_hour_data["total_revenue"]
    peak_units = peak_hour_data["total_units_sold"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Peak Revenue Hour",
            f"{peak_hour:02d}:00"
        )

    with col2:
        st.metric(
            "Peak Hour Revenue",
            f"{peak_revenue:,.2f}"
        )

    with col3:
        st.metric(
            "Peak Hour Units Sold",
            f"{peak_units:,.0f}"
        )
else:
    st.info("No hourly sales data is available for the selected filters.")



# --------------------------------------------------
# 13. Business Dependency and Pareto Analysis
# --------------------------------------------------

st.divider()
st.header("Business Dependency & Pareto Analysis")

st.markdown("""
Analyze how much revenue is generated by the highest-performing
products and assess overall product revenue concentration.
""")

# Sort products by revenue in descending order
pareto_summary = product_summary.sort_values(
    by="total_revenue",
    ascending=False
).copy()

# Calculate cumulative revenue
pareto_summary["cumulative_revenue"] = (
    pareto_summary["total_revenue"].cumsum()
)

# Calculate cumulative revenue contribution
pareto_total_revenue = pareto_summary["total_revenue"].sum()

if pareto_total_revenue > 0:
    pareto_summary["cumulative_contribution_pct"] = (
        pareto_summary["cumulative_revenue"]
        / pareto_total_revenue * 100
    )
else:
    pareto_summary["cumulative_contribution_pct"] = 0

# Calculate revenue contribution of top product groups
top_10_contribution = (
    pareto_summary.head(10)["total_revenue"].sum()
    / pareto_total_revenue * 100
    if pareto_total_revenue > 0 else 0
)

top_20_contribution = (
    pareto_summary.head(20)["total_revenue"].sum()
    / pareto_total_revenue * 100
    if pareto_total_revenue > 0 else 0
)

products_for_80 = (
    (pareto_summary["cumulative_contribution_pct"] >= 80).idxmax()
    if not pareto_summary.empty and pareto_total_revenue > 0
    else None
)

if products_for_80 is not None:
    products_needed_for_80 = (
        pareto_summary.index.get_loc(products_for_80) + 1
    )
else:
    products_needed_for_80 = 0

# Display concentration metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Top 10 Products Contribution",
        f"{top_10_contribution:.2f}%"
    )

with col2:
    st.metric(
        "Top 20 Products Contribution",
        f"{top_20_contribution:.2f}%"
    )

with col3:
    st.metric(
        "Products Generating 80% Revenue",
        f"{products_needed_for_80}"
    )


st.subheader("Product Revenue Concentration — Pareto Analysis")

fig, ax1 = plt.subplots(figsize=(12, 6))

# Product ranking on the horizontal axis
product_ranks = range(1, len(pareto_summary) + 1)

# Revenue bars
ax1.bar(
    product_ranks,
    pareto_summary["total_revenue"]
)

ax1.set_xlabel("Product Revenue Ranking")
ax1.set_ylabel("Product Revenue")
ax1.set_title("Pareto Analysis of Product Revenue")

# Cumulative revenue contribution line
ax2 = ax1.twinx()

ax2.plot(
    product_ranks,
    pareto_summary["cumulative_contribution_pct"],
    marker=".",
    linewidth=2
)

ax2.set_ylabel("Cumulative Revenue Contribution (%)")
ax2.set_ylim(0, 105)

# Reference line at 80%
ax2.axhline(
    80,
    linestyle="--",
    linewidth=1.5,
    label="80% Revenue Threshold"
)

ax2.legend(loc="lower right")

ax1.grid(axis="y", linestyle="--", alpha=0.3)
ax1.set_axisbelow(True)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)





