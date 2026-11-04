from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ------------------------------------------------------------
# 1. PAGE CONFIGURATION & VISUAL STYLING
# ------------------------------------------------------------

st.set_page_config(
    page_title="Afficionado Coffee | Revenue Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #F7F5F0;
            color: #29231F;
        }
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            max-width: 1500px;
        }
        h1, h2, h3 {
            color: #34251F;
        }
        .dashboard-eyebrow {
            color: #8A654A;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }
        .dashboard-subtitle {
            color: #746A63;
            font-size: 1rem;
            margin-top: -0.4rem;
            margin-bottom: 1.2rem;
        }
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E8E0D8;
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 2px 8px rgba(52, 37, 31, 0.04);
        }
        div[data-testid="stMetricLabel"] {
            color: #746A63;
            font-size: 0.9rem;
        }
        div[data-testid="stMetricValue"] {
            color: #34251F;
            font-weight: 700;
        }
        div[data-testid="stRadio"] > label {
            color: #746A63;
            font-weight: 600;
        }
        .section-caption {
            color: #746A63;
            font-size: 0.9rem;
            margin-top: -0.4rem;
            margin-bottom: 0.8rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 2. DATA LOADING & PREPARATION
# ------------------------------------------------------------

DATA_PATH = Path(__file__).parent / "Data" / "Afficionado_Coffee_Roasters.csv"


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """Load transaction data and calculate revenue for each record."""
    data = pd.read_csv(file_path)
    data["revenue"] = data["transaction_qty"] * data["unit_price"]
    return data


try:
    df = load_data(str(DATA_PATH))
except FileNotFoundError:
    st.error(
        "Dataset not found. Keep the existing Data folder and CSV file beside app1.py."
    )
    st.stop()

required_columns = {
    "transaction_qty", "unit_price", "product_category", "product_type",
    "product_detail", "store_location", "transaction_time"
}
missing_columns = required_columns.difference(df.columns)
if missing_columns:
    st.error(f"The dataset is missing required columns: {', '.join(sorted(missing_columns))}")
    st.stop()


# ------------------------------------------------------------
# 3. DASHBOARD HEADER
# ------------------------------------------------------------

st.markdown('<div class="dashboard-eyebrow">Retail performance dashboard</div>', unsafe_allow_html=True)
st.title("☕ Afficionado Coffee Roasters")
st.markdown(
    '<div class="dashboard-subtitle">Product optimization & revenue analytics · 2025 transaction data</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 4. SIDEBAR FILTERS
# ------------------------------------------------------------

def clear_all_filters():
    st.session_state["store_filter"] = "All Stores"
    st.session_state["category_filter"] = "All Categories"
    st.session_state["type_filter"] = "All Product Types"


def reset_product_type():
    st.session_state["type_filter"] = "All Product Types"


st.sidebar.header("Dashboard Filters")


store_options = [
    "All Stores",
    "Hell's Kitchen",
    "Astoria",
    "Lower Manhattan"
]

selected_store = st.sidebar.selectbox(
    "Store Location",
    options=store_options,
    key="store_filter",
    index=0
)


category_options = ["All Categories"] + sorted(
    df["product_category"].dropna().unique().tolist()
)

selected_category = st.sidebar.selectbox(
    "Product Category",
    options=category_options,
    key="category_filter",
    index=0,
    on_change=reset_product_type
)


if selected_category == "All Categories":

    available_types = sorted(
        df["product_type"].dropna().unique().tolist()
    )

else:

    available_types = sorted(
        df.loc[
            df["product_category"] == selected_category,
            "product_type"
        ].dropna().unique().tolist()
    )

type_options = ["All Product Types"] + available_types


if st.session_state.get("type_filter") not in type_options:
    st.session_state["type_filter"] = "All Product Types"

selected_type = st.sidebar.selectbox(
    "Product Type",
    options=type_options,
    key="type_filter",
    index=0
)


st.sidebar.divider()

st.sidebar.button(
    "↺ Clear All Filters",
    use_container_width=True,
    on_click=clear_all_filters
)


filtered_df = df.copy()

if selected_store != "All Stores":

    filtered_df = filtered_df[
        filtered_df["store_location"] == selected_store
    ]

if selected_category != "All Categories":

    filtered_df = filtered_df[
        filtered_df["product_category"] == selected_category
    ]

if selected_type != "All Product Types":

    filtered_df = filtered_df[
        filtered_df["product_type"] == selected_type
    ]


# ------------------------------------------------------------
# 5. BUSINESS OVERVIEW & KPI CARDS
# ------------------------------------------------------------

st.subheader("Business Overview")

st.caption(
    "A snapshot of business performance for the selected store "
    "and product filters."
)


def format_kpi(value):

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    elif abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"

    else:
        return f"{value:,.2f}"


if filtered_df.empty:

    st.warning(
        "No records match these filters. "
        "Try selecting a different category or product type."
    )

else:


    total_revenue = filtered_df["revenue"].sum()

    total_units = filtered_df["transaction_qty"].sum()

    transaction_records = len(filtered_df)

    unique_products = filtered_df["product_detail"].nunique()


    avg_revenue_per_record = (
        total_revenue / transaction_records
        if transaction_records > 0 else 0
    )

    avg_revenue_per_unit = (
        total_revenue / total_units
        if total_units > 0 else 0
    )


    category_kpi = (
        filtered_df.groupby("product_category")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    top_category_share = (
        category_kpi.iloc[0] / total_revenue * 100
        if len(category_kpi) > 0 and total_revenue > 0
        else 0
    )

    top_category_name = (
        category_kpi.index[0]
        if len(category_kpi) > 0
        else "N/A"
    )


    product_kpi = (
        filtered_df.groupby("product_detail")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    top_product_share = (
        product_kpi.iloc[0] / total_revenue * 100
        if len(product_kpi) > 0 and total_revenue > 0
        else 0
    )

    top_product_name = (
        product_kpi.index[0]
        if len(product_kpi) > 0
        else "N/A"
    )


    st.markdown("##### Core Performance")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric(
        "Total Revenue",
        format_kpi(total_revenue)
    )

    kpi2.metric(
        "Units Sold",
        format_kpi(total_units)
    )

    kpi3.metric(
        "Transaction Records",
        format_kpi(transaction_records)
    )

    kpi4.metric(
        "Products Represented",
        f"{unique_products:,.0f}"
    )


    st.divider()
    st.markdown("##### Revenue Contribution & Efficiency")

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

    kpi5.metric(
        "Avg. Revenue / Record",
        format_kpi(avg_revenue_per_record)
    )

    kpi6.metric(
        "Avg. Revenue / Unit",
        format_kpi(avg_revenue_per_unit)
    )

    kpi7.metric(
        "Top Category Share",
        f"{top_category_share:.1f}%",
        help=f"Highest contributing category: {top_category_name}"
    )

    kpi8.metric(
        "Top Product Share",
        f"{top_product_share:.1f}%",
        help=f"Highest contributing product: {top_product_name}"
    )


    st.caption(
        f"Showing {transaction_records:,} transaction records · "
        f"{selected_store} · {selected_category} · {selected_type}"
    )

    st.divider()


with st.expander("Dataset preview (optional)"):
    st.caption("Raw transaction records for the currently selected filters.")
    st.dataframe(filtered_df.head(100), use_container_width=True, hide_index=True)
    st.caption("Showing at most the first 100 matching records.")


# ------------------------------------------------------------
# 6. CATEGORY REVENUE CONTRIBUTION
# ------------------------------------------------------------

st.divider()
st.subheader("Category Revenue Contribution")

st.caption(
    "Explore how each product category contributes to total revenue "
    "within the selected filters."
)

category_revenue = (
    filtered_df.groupby("product_category", as_index=False)
    .agg(
        total_revenue=("revenue", "sum"),
        units_sold=("transaction_qty", "sum"),
        transaction_records=("transaction_id", "count")
    )
)

if not category_revenue.empty:
    total_filtered_revenue = category_revenue["total_revenue"].sum()

    category_revenue["revenue_share"] = (
        category_revenue["total_revenue"] / total_filtered_revenue * 100
        if total_filtered_revenue > 0
        else 0
    )

    category_revenue = category_revenue.sort_values(
        "total_revenue",
        ascending=True
    )

    fig_category = px.bar(
        category_revenue,
        x="total_revenue",
        y="product_category",
        orientation="h",
        color_discrete_sequence=["#9B6A45"],
        custom_data=[
            "revenue_share",
            "units_sold",
            "transaction_records"
        ],
        labels={
            "total_revenue": "Revenue",
            "product_category": ""
        }
    )

    fig_category.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Revenue: %{x:,.2f}<br>"
            "Revenue Contribution: %{customdata[0]:.2f}%<br>"
            "Units Sold: %{customdata[1]:,.0f}<br>"
            "Transaction Records: %{customdata[2]:,.0f}"
            "<extra></extra>"
        )
    )

    fig_category.update_layout(
        height=430,
        margin=dict(l=10, r=30, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#34251F",
            family="Arial, sans-serif"
        ),
        xaxis=dict(
            title="Revenue",
            showgrid=True,
            gridcolor="#E8E0D8",
            zeroline=False
        ),
        yaxis=dict(
            title="",
            showgrid=False
        ),
        showlegend=False
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

    with st.expander("View Category Revenue Details"):
        display_category = (
            category_revenue
            .sort_values("total_revenue", ascending=False)
            .copy()
        )

        display_category["total_revenue"] = (
            display_category["total_revenue"]
            .map(lambda x: f"{x:,.2f}")
        )

        display_category["revenue_share"] = (
            display_category["revenue_share"]
            .map(lambda x: f"{x:.2f}%")
        )

        display_category = display_category.rename(
            columns={
                "product_category": "Category",
                "total_revenue": "Revenue",
                "revenue_share": "Revenue Contribution",
                "units_sold": "Units Sold",
                "transaction_records": "Transaction Records"
            }
        )

        st.dataframe(
            display_category,
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("No category revenue data available for the selected filters.")


st.divider()

# ------------------------------------------------------------
# 7. PRODUCT PERFORMANCE RANKING
# ------------------------------------------------------------

st.subheader("Product Performance Ranking")

st.caption(
    "Compare products by revenue contribution and sales volume. "
    "Use the slider to control how many products are displayed."
)


top_n = st.slider(
    "Number of products to display",
    min_value=5,
    max_value=30,
    value=10,
    step=5
)


product_ranking = (
    filtered_df.groupby("product_detail", as_index=False)
    .agg(
        total_revenue=("revenue", "sum"),
        units_sold=("transaction_qty", "sum"),
        transaction_records=("transaction_id", "count")
    )
)

if not product_ranking.empty:


    total_revenue = product_ranking["total_revenue"].sum()
    total_units = product_ranking["units_sold"].sum()

    product_ranking["revenue_share"] = (
        product_ranking["total_revenue"] / total_revenue * 100
        if total_revenue > 0 else 0
    )

    product_ranking["volume_share"] = (
        product_ranking["units_sold"] / total_units * 100
        if total_units > 0 else 0
    )


    top_revenue_products = (
        product_ranking
        .nlargest(top_n, "total_revenue")
        .sort_values("total_revenue", ascending=True)
    )

    top_volume_products = (
        product_ranking
        .nlargest(top_n, "units_sold")
        .sort_values("units_sold", ascending=True)
    )


    col1, col2 = st.columns(2, gap="large")


    with col1:

        st.markdown("#### Revenue Ranking")

        fig_revenue = px.bar(
            top_revenue_products,
            x="total_revenue",
            y="product_detail",
            orientation="h",
            color_discrete_sequence=["#9B6A45"],
            custom_data=[
                "units_sold",
                "revenue_share",
                "transaction_records"
            ],
            labels={
                "total_revenue": "Revenue",
                "product_detail": ""
            }
        )

        fig_revenue.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Revenue: %{x:,.2f}<br>"
                "Units Sold: %{customdata[0]:,.0f}<br>"
                "Revenue Contribution: %{customdata[1]:.2f}%<br>"
                "Transaction Records: %{customdata[2]:,.0f}"
                "<extra></extra>"
            )
        )

        fig_revenue.update_layout(
            height=max(420, top_n * 35),
            margin=dict(l=5, r=15, t=15, b=35),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#34251F", size=11),
            xaxis=dict(
                title="Revenue",
                showgrid=True,
                gridcolor="#E8E0D8",
                zeroline=False
            ),
            yaxis=dict(title="", showgrid=False),
            showlegend=False
        )

        st.plotly_chart(
            fig_revenue,
            use_container_width=True
        )


    with col2:

        st.markdown("#### Sales Volume Ranking")

        fig_volume = px.bar(
            top_volume_products,
            x="units_sold",
            y="product_detail",
            orientation="h",
            color_discrete_sequence=["#C08B58"],
            custom_data=[
                "total_revenue",
                "volume_share",
                "transaction_records"
            ],
            labels={
                "units_sold": "Units Sold",
                "product_detail": ""
            }
        )

        fig_volume.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Units Sold: %{x:,.0f}<br>"
                "Revenue: %{customdata[0]:,.2f}<br>"
                "Volume Contribution: %{customdata[1]:.2f}%<br>"
                "Transaction Records: %{customdata[2]:,.0f}"
                "<extra></extra>"
            )
        )

        fig_volume.update_layout(
            height=max(420, top_n * 35),
            margin=dict(l=5, r=15, t=15, b=35),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#34251F", size=11),
            xaxis=dict(
                title="Units Sold",
                showgrid=True,
                gridcolor="#E8E0D8",
                zeroline=False
            ),
            yaxis=dict(title="", showgrid=False),
            showlegend=False
        )

        st.plotly_chart(
            fig_volume,
            use_container_width=True
        )


    detail_col1, detail_col2 = st.columns(2, gap="large")


    with detail_col1:

        with st.expander("Revenue Ranking Details"):

            revenue_details = top_revenue_products.copy()

            revenue_details = revenue_details.sort_values(
                "total_revenue",
                ascending=False
            )

            revenue_details["total_revenue"] = (
                revenue_details["total_revenue"]
                .map(lambda x: f"{x:,.2f}")
            )

            revenue_details["revenue_share"] = (
                revenue_details["revenue_share"]
                .map(lambda x: f"{x:.2f}%")
            )

            revenue_details["volume_share"] = (
                revenue_details["volume_share"]
                .map(lambda x: f"{x:.2f}%")
            )

            revenue_details = revenue_details.rename(
                columns={
                    "product_detail": "Product",
                    "total_revenue": "Revenue",
                    "units_sold": "Units Sold",
                    "transaction_records": "Transaction Records",
                    "revenue_share": "Revenue Contribution",
                    "volume_share": "Volume Contribution"
                }
            )

            st.dataframe(
                revenue_details,
                use_container_width=True,
                hide_index=True
            )


    with detail_col2:

        with st.expander("Sales Volume Ranking Details"):

            volume_details = top_volume_products.copy()

            volume_details = volume_details.sort_values(
                "units_sold",
                ascending=False
            )

            volume_details["total_revenue"] = (
                volume_details["total_revenue"]
                .map(lambda x: f"{x:,.2f}")
            )

            volume_details["revenue_share"] = (
                volume_details["revenue_share"]
                .map(lambda x: f"{x:.2f}%"
                )
            )

            volume_details["volume_share"] = (
                volume_details["volume_share"]
                .map(lambda x: f"{x:.2f}%")
            )

            volume_details = volume_details.rename(
                columns={
                    "product_detail": "Product",
                    "total_revenue": "Revenue",
                    "units_sold": "Units Sold",
                    "transaction_records": "Transaction Records",
                    "revenue_share": "Revenue Contribution",
                    "volume_share": "Volume Contribution"
                }
            )

            st.dataframe(
                volume_details,
                use_container_width=True,
                hide_index=True
            )


else:
    st.info("No product data available for the selected filters.")


st.divider()

# ------------------------------------------------------------
# 8. STORE PERFORMANCE
# ------------------------------------------------------------

st.subheader("Store Performance")

st.caption(
    "Compare revenue contribution across store locations "
    "within the selected filters."
)


store_performance = (
    filtered_df.groupby("store_location", as_index=False)
    .agg(
        total_revenue=("revenue", "sum"),
        units_sold=("transaction_qty", "sum"),
        transaction_records=("transaction_id", "count")
    )
    .sort_values("total_revenue", ascending=True)
)


total_filtered_revenue = filtered_df["revenue"].sum()

store_performance["revenue_share"] = (
    store_performance["total_revenue"] / total_filtered_revenue * 100
    if total_filtered_revenue > 0
    else 0
)


fig_store = px.bar(
    store_performance,
    x="total_revenue",
    y="store_location",
    orientation="h",
    color_discrete_sequence=["#9B6A45"],
    custom_data=[
        "units_sold",
        "revenue_share",
        "transaction_records"
    ],
    labels={
        "total_revenue": "Revenue",
        "store_location": ""
    }
)

fig_store.update_traces(
    hovertemplate=(
        "<b>%{y}</b><br>"
        "Revenue: %{x:,.2f}<br>"
        "Units Sold: %{customdata[0]:,.0f}<br>"
        "Revenue Contribution: %{customdata[1]:.2f}%<br>"
        "Transaction Records: %{customdata[2]:,.0f}"
        "<extra></extra>"
    )
)

fig_store.update_layout(
    height=300,
    margin=dict(l=10, r=30, t=20, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="#34251F",
        family="Arial, sans-serif"
    ),
    xaxis=dict(
        title="Revenue",
        showgrid=True,
        gridcolor="#E8E0D8",
        zeroline=False
    ),
    yaxis=dict(
        title="",
        showgrid=False
    ),
    showlegend=False
)

st.plotly_chart(
    fig_store,
    use_container_width=True
)


with st.expander("View Store Performance Details"):

    display_store = store_performance.copy()

    display_store["total_revenue"] = (
        display_store["total_revenue"]
        .map(lambda x: f"{x:,.2f}")
    )

    display_store["revenue_share"] = (
        display_store["revenue_share"]
        .map(lambda x: f"{x:.2f}%")
    )

    display_store = display_store.rename(
        columns={
            "store_location": "Store",
            "total_revenue": "Revenue",
            "units_sold": "Units Sold",
            "transaction_records": "Transaction Records",
            "revenue_share": "Revenue Contribution"
        }
    )

    st.dataframe(
        display_store,
        use_container_width=True,
        hide_index=True
    )


st.divider()

# ------------------------------------------------------------
# 9. PRODUCT POPULARITY VS REVENUE
# ------------------------------------------------------------

st.subheader("Product Popularity vs. Revenue")

st.caption(
    "Explore the relationship between product sales volume "
    "and revenue contribution. Median lines divide products "
    "into four performance groups."
)


product_scatter = (
    filtered_df.groupby(
        ["product_detail", "product_category"],
        as_index=False
    )
    .agg(
        total_revenue=("revenue", "sum"),
        units_sold=("transaction_qty", "sum")
    )
)

if not product_scatter.empty:


    median_units = product_scatter["units_sold"].median()
    median_revenue = product_scatter["total_revenue"].median()


    fig_scatter = px.scatter(
        product_scatter,
        x="units_sold",
        y="total_revenue",
        hover_name="product_detail",
        color="product_category",
        custom_data=["product_category"],
        labels={
            "units_sold": "Units Sold",
            "total_revenue": "Revenue",
            "product_category": "Category"
        }
    )


    fig_scatter.add_vline(
        x=median_units,
        line_dash="dash",
        line_color="#9B6A45",
        annotation_text="Median Units"
    )

    fig_scatter.add_hline(
        y=median_revenue,
        line_dash="dash",
        line_color="#9B6A45",
        annotation_text="Median Revenue"
    )

    fig_scatter.update_traces(
        marker=dict(
            size=10,
            opacity=0.75,
            line=dict(width=0.5, color="#FFFFFF")
        ),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Category: %{customdata[0]}<br>"
            "Units Sold: %{x:,.0f}<br>"
            "Revenue: %{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig_scatter.update_layout(
        height=550,
        margin=dict(l=10, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#34251F",
            family="Arial, sans-serif"
        ),
        xaxis=dict(
            title="Units Sold",
            showgrid=True,
            gridcolor="#E8E0D8",
            zeroline=False
        ),
        yaxis=dict(
            title="Revenue",
            showgrid=True,
            gridcolor="#E8E0D8",
            zeroline=False
        ),
        legend_title_text="Product Category"
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

    st.caption(
        "Upper-right: high volume and high revenue | "
        "Upper-left: lower volume but high revenue | "
        "Lower-right: high volume but lower revenue | "
        "Lower-left: lower volume and lower revenue."
    )

else:
    st.info("No product data available for the selected filters.")


st.divider()

# ------------------------------------------------------------
# 10. PRODUCT DRILL-DOWN ANALYSIS
# ------------------------------------------------------------

st.subheader("Product Drill-Down Analysis")

st.caption(
    "Select an individual product to explore its sales "
    "performance across store locations."
)


available_products = sorted(
    filtered_df["product_detail"].dropna().unique().tolist()
)

if available_products:

    selected_product = st.selectbox(
        "Select a Product",
        options=available_products
    )


    product_detail_df = filtered_df[
        filtered_df["product_detail"] == selected_product
    ].copy()


    product_revenue = product_detail_df["revenue"].sum()
    product_units = product_detail_df["transaction_qty"].sum()
    product_records = product_detail_df["transaction_id"].nunique()

    product_category = product_detail_df["product_category"].iloc[0]
    product_type = product_detail_df["product_type"].iloc[0]

    total_filtered_revenue = filtered_df["revenue"].sum()

    product_revenue_share = (
        product_revenue / total_filtered_revenue * 100
        if total_filtered_revenue > 0 else 0
    )


    st.markdown(f"**Category:** {product_category}  |  **Product Type:** {product_type}")


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Revenue",
        format_kpi(product_revenue)
    )

    col2.metric(
        "Units Sold",
        format_kpi(product_units)
    )

    col3.metric(
        "Transaction Records",
        format_kpi(product_records)
    )

    col4.metric(
        "Revenue Contribution",
        f"{product_revenue_share:.2f}%"
    )


    st.markdown("#### Store-Level Performance")

    product_store_performance = (
        product_detail_df.groupby(
            "store_location",
            as_index=False
        )
        .agg(
            total_revenue=("revenue", "sum"),
            units_sold=("transaction_qty", "sum"),
            transaction_records=("transaction_id", "count")
        )
        .sort_values("total_revenue", ascending=False)
    )

    fig_product_store = px.bar(
        product_store_performance,
        x="store_location",
        y="total_revenue",
        color_discrete_sequence=["#9B6A45"],
        custom_data=[
            "units_sold",
            "transaction_records"
        ],
        labels={
            "store_location": "Store Location",
            "total_revenue": "Revenue"
        }
    )

    fig_product_store.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Revenue: %{y:,.2f}<br>"
            "Units Sold: %{customdata[0]:,.0f}<br>"
            "Transaction Records: %{customdata[1]:,.0f}"
            "<extra></extra>"
        )
    )

    fig_product_store.update_layout(
        height=350,
        margin=dict(l=10, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#34251F"),
        xaxis=dict(
            title="Store Location",
            showgrid=False
        ),
        yaxis=dict(
            title="Revenue",
            showgrid=True,
            gridcolor="#E8E0D8"
        ),
        showlegend=False
    )

    st.plotly_chart(
        fig_product_store,
        use_container_width=True
    )


    with st.expander("View Product Performance Details"):

        display_product_detail = (
            product_store_performance.copy()
        )

        display_product_detail["total_revenue"] = (
            display_product_detail["total_revenue"]
            .map(lambda x: f"{x:,.2f}")
        )

        display_product_detail = (
            display_product_detail.rename(
                columns={
                    "store_location": "Store",
                    "total_revenue": "Revenue",
                    "units_sold": "Units Sold",
                    "transaction_records": "Transaction Records"
                }
            )
        )

        st.dataframe(
            display_product_detail,
            use_container_width=True,
            hide_index=True
        )

else:
    st.info("No products available for the selected filters.")
