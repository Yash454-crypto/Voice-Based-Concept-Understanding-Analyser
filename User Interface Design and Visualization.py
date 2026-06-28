"""
User Interface Design & Visualization Demo
--------------------------------------------
Run with:  streamlit run visualization_app.py

Demonstrates:
- Custom theming via CSS injection
- Layout design (columns, containers, cards)
- Multiple visualization libraries: Matplotlib, Plotly, Altair
- KPI cards / metric dashboards
- Color palettes & style consistency
- Responsive-style grid layout
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import altair as alt

# ----------------------------------------------------------------------
# 1. Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Visualization Dashboard",
    page_icon="🎨",
    layout="wide",
)

# ----------------------------------------------------------------------
# 2. Custom theming via CSS injection (UI design)
# ----------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Overall page padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* KPI card styling */
.kpi-card {
    background: linear-gradient(135deg, #1f2937, #111827);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    color: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.kpi-card h3 {
    font-size: 0.85rem;
    font-weight: 500;
    color: #9ca3af;
    margin-bottom: 0.3rem;
}
.kpi-card p {
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0;
}

/* Section headers */
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid #6366f1;
    padding-left: 0.6rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Consistent color palette across all charts
PALETTE = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4", "#a855f7"]

# ----------------------------------------------------------------------
# 3. Sample data
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    rng = np.random.default_rng(7)
    dates = pd.date_range("2024-01-01", periods=180, freq="D")
    regions = ["North", "South", "East", "West"]
    df = pd.DataFrame(
        {
            "date": np.tile(dates, len(regions)),
            "region": np.repeat(regions, len(dates)),
        }
    )
    df["sales"] = (
        500
        + 50 * np.sin(np.linspace(0, 12, len(df)))
        + rng.normal(0, 40, len(df))
        + df["region"].map({"North": 100, "South": 50, "East": 0, "West": -30})
    ).round(2)
    df["units"] = (df["sales"] / rng.uniform(8, 12, len(df))).round(0)
    return df


df = load_data()

# ----------------------------------------------------------------------
# 4. Header
# ----------------------------------------------------------------------
st.title("🎨 UI Design & Visualization Dashboard")
st.caption("Custom-themed dashboard combining Matplotlib, Plotly, and Altair.")

# ----------------------------------------------------------------------
# 5. Sidebar filters
# ----------------------------------------------------------------------
st.sidebar.header("Filters")
selected_regions = st.sidebar.multiselect(
    "Region", options=df["region"].unique(), default=list(df["region"].unique())
)
date_range = st.sidebar.date_input(
    "Date range",
    value=(df["date"].min().date(), df["date"].max().date()),
)

mask = df["region"].isin(selected_regions)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    mask &= (df["date"] >= pd.Timestamp(start)) & (df["date"] <= pd.Timestamp(end))

fdf = df[mask]

# ----------------------------------------------------------------------
# 6. KPI cards (custom HTML components)
# ----------------------------------------------------------------------
total_sales = fdf["sales"].sum()
total_units = fdf["units"].sum()
avg_sales = fdf["sales"].mean()
top_region = fdf.groupby("region")["sales"].sum().idxmax() if len(fdf) else "—"

kpi_cols = st.columns(4)
kpi_data = [
    ("Total Sales", f"${total_sales:,.0f}"),
    ("Total Units", f"{total_units:,.0f}"),
    ("Avg Daily Sales", f"${avg_sales:,.2f}"),
    ("Top Region", top_region),
]
for col, (label, value) in zip(kpi_cols, kpi_data):
    col.markdown(
        f"""<div class="kpi-card"><h3>{label}</h3><p>{value}</p></div>""",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# 7. Plotly: interactive time series
# ----------------------------------------------------------------------
st.markdown('<div class="section-title">Sales Over Time (Plotly)</div>', unsafe_allow_html=True)

fig_line = px.line(
    fdf,
    x="date",
    y="sales",
    color="region",
    color_discrete_sequence=PALETTE,
    template="plotly_dark",
)
fig_line.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_line, use_container_width=True)

# ----------------------------------------------------------------------
# 8. Two-column layout: Plotly donut + Altair bar
# ----------------------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-title">Sales Share by Region</div>', unsafe_allow_html=True)
    region_totals = fdf.groupby("region", as_index=False)["sales"].sum()
    fig_donut = go.Figure(
        data=[
            go.Pie(
                labels=region_totals["region"],
                values=region_totals["sales"],
                hole=0.55,
                marker=dict(colors=PALETTE),
            )
        ]
    )
    fig_donut.update_layout(margin=dict(l=10, r=10, t=10, b=10), template="plotly_dark")
    st.plotly_chart(fig_donut, use_container_width=True)

with col_right:
    st.markdown('<div class="section-title">Monthly Units (Altair)</div>', unsafe_allow_html=True)
    monthly = fdf.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    monthly_agg = monthly.groupby(["month", "region"], as_index=False)["units"].sum()

    chart = (
        alt.Chart(monthly_agg)
        .mark_bar()
        .encode(
            x=alt.X("month:N", title="Month"),
            y=alt.Y("units:Q", title="Units"),
            color=alt.Color("region:N", scale=alt.Scale(range=PALETTE)),
            tooltip=["month", "region", "units"],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

# ----------------------------------------------------------------------
# 9. Matplotlib: styled static chart
# ----------------------------------------------------------------------
st.markdown('<div class="section-title">Sales Distribution (Matplotlib)</div>', unsafe_allow_html=True)

plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(10, 4))
for i, region in enumerate(selected_regions):
    region_data = fdf[fdf["region"] == region]["sales"]
    ax.hist(region_data, bins=25, alpha=0.6, label=region, color=PALETTE[i % len(PALETTE)])

ax.set_xlabel("Sales")
ax.set_ylabel("Frequency")
ax.legend(loc="upper right", frameon=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
st.pyplot(fig)

# ----------------------------------------------------------------------
# 10. Data table with conditional styling
# ----------------------------------------------------------------------
st.markdown('<div class="section-title">Detailed Data</div>', unsafe_allow_html=True)
st.dataframe(
    fdf.sort_values("date", ascending=False).style.background_gradient(
        subset=["sales"], cmap="viridis"
    ),
    use_container_width=True,
    height=300,
)

st.caption("Dashboard demo — custom CSS theming + Matplotlib / Plotly / Altair visualizations.")