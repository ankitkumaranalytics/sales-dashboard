import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pathlib import Path
from PIL import Image
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ======================================================
# PAGE CONFIGURATION
# ======================================================

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

pio.templates.default = "plotly_white"

# ======================================================
# CUSTOM CSS
# ======================================================

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
    padding-bottom:1rem;
}

div[data-testid="metric-container"]{
    background:white;
    border-radius:12px;
    padding:18px;
    box-shadow:0px 3px 10px rgba(0,0,0,0.10);
}

h1{
    color:#1F4E79;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# PROJECT PATH
# ======================================================

BASE_DIR = Path(__file__).resolve().parent

# ======================================================
# HEADER
# ======================================================

logo_path = BASE_DIR / "assets" / "logo.png"

logo_col, title_col = st.columns([1.2,5])

with logo_col:

    if logo_path.exists():

        try:

            logo = Image.open(logo_path)

            st.image(
                logo,
                width=170
            )

        except Exception:

            st.markdown("# 📊")

    else:

        st.markdown("# 📊")


with title_col:

    st.title("📊 Sales Analytics Dashboard")

    st.markdown(
        """
### Professional Business Intelligence Dashboard

Analyze sales, customers, products and profit using Python, Pandas, Plotly and Streamlit.
"""
    )

    today = datetime.now().strftime("%d %B %Y")

    st.caption(f"📅 Today : {today}")

st.divider()

# ======================================================
# FIND DATASET
# ======================================================

possible_files = [

    BASE_DIR / "data" / "sales_data.csv",

    BASE_DIR / "data" / "processed" / "cleaned_sales.csv"

]

DATA_PATH = None

for file in possible_files:

    if file.exists():

        DATA_PATH = file

        break

if DATA_PATH is None:

    st.error("❌ Dataset not found.")

    st.stop()

# ======================================================
# LOAD DATASET
# ======================================================

encodings = [

    "utf-8",

    "utf-8-sig",

    "cp1252",

    "latin1",

    "ISO-8859-1"

]

df = None

for enc in encodings:

    try:

        df = pd.read_csv(
            DATA_PATH,
            encoding=enc
        )

        break

    except Exception:

        pass

if df is None:

    st.error("Unable to read dataset.")

    st.stop()

# ======================================================
# CLEAN COLUMN NAMES
# ======================================================

df.columns = (

    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ","_")
)

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.title("🔍 Dashboard Filters")

# Category Filter

if "category" in df.columns:

    category = st.sidebar.selectbox(

        "Category",

        ["All"] + sorted(df["category"].unique().tolist())

    )

    if category != "All":

        df = df[df["category"] == category]

# Region Filter

if "region" in df.columns:

    region = st.sidebar.selectbox(

        "Region",

        ["All"] + sorted(df["region"].unique().tolist())

    )

    if region != "All":

        df = df[df["region"] == region]

# Date Filter

if "order_date" in df.columns:

    df["order_date"] = pd.to_datetime(df["order_date"])

    min_date = df["order_date"].min().date()

    max_date = df["order_date"].max().date()

    start_date, end_date = st.sidebar.date_input(

        "Date Range",

        value=(min_date, max_date)

    )

    df = df[
        (df["order_date"] >= pd.to_datetime(start_date))
        &
        (df["order_date"] <= pd.to_datetime(end_date))
    ]

st.sidebar.markdown("---")

st.sidebar.success(f"Showing {len(df):,} Records")

# ======================================================
# DATA LOADED
# ======================================================

st.success(f"✅ Dataset Loaded Successfully ({len(df):,} rows)")

# ======================================================
# KPI SECTION
# ======================================================

st.divider()

st.subheader("📊 Business Overview")

total_sales = df["sales"].sum()

total_profit = df["profit"].sum()

total_orders = df["order_id"].nunique()

total_customers = df["customer_id"].nunique()

average_order = total_sales / total_orders if total_orders else 0

profit_margin = (
    total_profit / total_sales * 100
    if total_sales else 0
)

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

kpi1.metric(
    "💰 Sales",
    f"${total_sales:,.0f}"
)

kpi2.metric(
    "📈 Profit",
    f"${total_profit:,.0f}"
)

kpi3.metric(
    "📦 Orders",
    f"{total_orders:,}"
)

kpi4.metric(
    "👥 Customers",
    f"{total_customers:,}"
)

kpi5.metric(
    "💵 Avg Order",
    f"${average_order:,.2f}"
)

kpi6.metric(
    "📊 Margin",
    f"{profit_margin:.2f}%"
)

# ======================================================
# SALES DASHBOARD
# ======================================================

st.divider()

st.subheader("📈 Sales Performance Dashboard")

left, right = st.columns(2)

# ======================================================
# SALES BY CATEGORY
# ======================================================

category_sales = (
    df.groupby("category", as_index=False)["sales"]
      .sum()
      .sort_values("sales", ascending=False)
)

fig1 = px.bar(
    category_sales,
    x="category",
    y="sales",
    color="sales",
    text_auto=".2s",
    color_continuous_scale="Blues",
    title="Sales by Category"
)

fig1.update_layout(

    height=470,

    title_x=0.5,

    xaxis_title="Category",

    yaxis_title="Sales",

    coloraxis_showscale=False,

    margin=dict(
        l=20,
        r=20,
        t=60,
        b=20
    )
)

fig1.update_traces(

    textposition="outside",

    hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
)

left.plotly_chart(
    fig1,
    width="stretch",
    key="category_chart"
)

# ======================================================
# SALES BY REGION
# ======================================================

region_sales = (
    df.groupby("region", as_index=False)["sales"]
      .sum()
)

fig2 = px.pie(

    region_sales,

    names="region",

    values="sales",

    hole=0.55,

    title="Sales by Region",

    color_discrete_sequence=px.colors.qualitative.Set2
)

fig2.update_layout(

    height=470,

    title_x=0.5
)

fig2.update_traces(

    textinfo="percent+label",

    hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<extra></extra>"
)

right.plotly_chart(
    fig2,
    width="stretch",
    key="region_chart"
)

# ======================================================
# MONTHLY SALES TREND
# ======================================================

st.divider()

st.subheader("📅 Monthly Sales Trend")

monthly_sales = (
    df.groupby(
        df["order_date"].dt.to_period("M")
    )["sales"]
    .sum()
    .reset_index()
)

monthly_sales["order_date"] = (
    monthly_sales["order_date"]
    .astype(str)
)

fig3 = px.line(

    monthly_sales,

    x="order_date",

    y="sales",

    markers=True,

    title="Monthly Sales Trend"
)

fig3.update_layout(

    height=500,

    title_x=0.5,

    xaxis_title="Month",

    yaxis_title="Sales",

    hovermode="x unified"
)

st.plotly_chart(
    fig3,
    width="stretch",
    key="monthly_sales_chart"
)
# ======================================================
# AI BUSINESS INSIGHTS
# ======================================================

st.divider()

st.subheader("🤖 AI Business Insights")

insight1, insight2 = st.columns(2)

# -----------------------------
# Best Selling Category
# -----------------------------

category_sales = (
    df.groupby("category")["sales"]
    .sum()
)

best_category = category_sales.idxmax()
best_category_sales = category_sales.max()

with insight1:

    st.success(
        f"""
🏆 **Best Selling Category**

**{best_category}**

Sales: **${best_category_sales:,.0f}**
"""
    )

# -----------------------------
# Best Region
# -----------------------------

region_sales = (
    df.groupby("region")["sales"]
    .sum()
)

best_region = region_sales.idxmax()
best_region_sales = region_sales.max()

with insight2:

    st.info(
        f"""
🌍 **Top Performing Region**

**{best_region}**

Sales: **${best_region_sales:,.0f}**
"""
    )

# -----------------------------
# Profit Analysis
# -----------------------------

if total_profit > 0:

    st.success(
        "📈 Business is generating an overall profit."
    )

else:

    st.error(
        "📉 Business is currently running at a loss."
    )

# -----------------------------
# Recommendation
# -----------------------------

if average_order >= 400:

    st.success(
        "💡 Customers have a high average order value."
    )

else:

    st.warning(
        "💡 Consider bundles or discounts to increase average order value."
    )
    # ======================================================
# DOWNLOAD REPORT
# ======================================================

st.divider()

st.subheader("📥 Download Report")

download_col1, download_col2 = st.columns(2)

with download_col1:

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download CSV",
        csv,
        file_name="sales_report.csv",
        mime="text/csv"
    )

with download_col2:

    excel_file = "sales_report.xlsx"

    with pd.ExcelWriter(excel_file) as writer:
        df.to_excel(writer, index=False)

    with open(excel_file, "rb") as file:

        st.download_button(
            "📊 Download Excel",
            file,
            file_name="sales_report.xlsx"
        )
        
        pdf_file = "sales_report.pdf"

doc = SimpleDocTemplate(pdf_file)

styles = getSampleStyleSheet()

story = []

story.append(Paragraph("<b>Sales Analytics Report</b>", styles["Title"]))

story.append(
    Paragraph(f"Total Sales: ${total_sales:,.2f}", styles["BodyText"])
)

story.append(
    Paragraph(f"Total Profit: ${total_profit:,.2f}", styles["BodyText"])
)

story.append(
    Paragraph(f"Total Orders: {total_orders}", styles["BodyText"])
)

story.append(
    Paragraph(f"Total Customers: {total_customers}", styles["BodyText"])
)

story.append(
    Paragraph(f"Average Order: ${average_order:,.2f}", styles["BodyText"])
)

story.append(
    Paragraph(f"Profit Margin: {profit_margin:.2f}%", styles["BodyText"])
)

doc.build(story)

with open(pdf_file, "rb") as pdf:

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf,
        file_name="sales_report.pdf",
        mime="application/pdf"
    )
# ======================================================
# FOOTER
# ======================================================

st.divider()

st.markdown(
    """
<div style='text-align:center;color:gray;'>

Developed by Ankit Kumar

Python • Streamlit • Plotly • Pandas

</div>
""",
    unsafe_allow_html=True
)