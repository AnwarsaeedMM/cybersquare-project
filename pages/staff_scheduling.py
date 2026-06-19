#!/usr/bin/env python
# coding: utf-8
# Cyber Square Institute — Staff Schedule Dashboard
# Run: streamlit run stfs_dashboard.py

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Project root
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Staff Schedule Dashboard — Cyber Square",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "staff_schedule_with_weekly.csv")
    time_cols = ["10:00-12:00", "12:00-02:00", "02:30-04:30", "04:30-05:30 (Online)"]
    df["free_periods"] = df[time_cols].apply(lambda row: (row == "Free Period").sum(), axis=1)
    df["utilization_pct"] = (df["daily_hours"] / 7 * 100).round(1)
    df["workload_tier"] = pd.cut(
        df["daily_hours"],
        bins=[0, 4, 5, 6, 7],
        labels=["Low (≤4 h)", "Mid (5 h)", "Mid-High (6 h)", "High (7 h)"],
    )
    return df

DATA_PATH = "staff_schedule_with_weekly.csv"

df = load_data(DATA_PATH)

TIME_COLS = ["10:00-12:00", "12:00-02:00", "02:30-04:30", "04:30-05:30 (Online)"]

# ─────────────────────────────────────────────
# Sidebar filters
# ─────────────────────────────────────────────
st.sidebar.title("🔍 Filters")
all_courses = sorted(df["course"].unique().tolist())
sel_courses = st.sidebar.multiselect("Course", all_courses, default=all_courses)

min_h, max_h = int(df["daily_hours"].min()), int(df["daily_hours"].max())
sel_hours = st.sidebar.slider("Daily Hours Range", min_h, max_h, (min_h, max_h))

filt = df[
    df["course"].isin(sel_courses) &
    df["daily_hours"].between(sel_hours[0], sel_hours[1])
].copy()

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(filt)}** of **{len(df)}** trainers")

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("📊 Staff Schedule Dashboard")
st.caption("Trainer scheduling efficiency · workload distribution · resource utilisation")
st.divider()

# ─────────────────────────────────────────────
# KPI Row
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

total_staff   = filt["staff_id"].nunique()
total_courses = filt["course"].nunique()
avg_daily     = round(filt["daily_hours"].mean(), 1)
avg_weekly    = round(filt["weekly_hours"].mean(), 1)
free_slots    = int((filt[TIME_COLS] == "Free Period").sum().sum())

k1.metric("👥 Total Trainers",    total_staff)
k2.metric("📚 Courses Covered",   total_courses)
k3.metric("⏱ Avg Daily Hours",   f"{avg_daily} h")
k4.metric("📅 Avg Weekly Hours",  f"{avg_weekly} h")
k5.metric("🕒 Free Period Slots", free_slots)

st.divider()

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Workload Analysis",
    "🗓 Schedule Grid",
    "📚 Course Allocation",
    "⚡ Utilisation",
    "📋 Raw Data",
])

# ══════════════════════════════════════════════
# TAB 1 — Workload Analysis
# ══════════════════════════════════════════════
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Daily Hours per Trainer")
        color_map = {
            "Low (≤4 h)":     "#1D9E75",
            "Mid (5 h)":      "#378ADD",
            "Mid-High (6 h)": "#7F77DD",
            "High (7 h)":     "#D85A30",
        }
        fig_daily = px.bar(
            filt.sort_values("daily_hours"),
            x="daily_hours",
            y="name",
            color="workload_tier",
            color_discrete_map=color_map,
            orientation="h",
            text="daily_hours",
            labels={"daily_hours": "Daily Hours", "name": "Trainer", "workload_tier": "Tier"},
        )
        fig_daily.update_traces(textposition="outside")
        fig_daily.update_layout(
            height=420,
            xaxis=dict(range=[0, 8]),
            legend_title="Workload Tier",
            margin=dict(l=10, r=30, t=20, b=10),
        )
        st.plotly_chart(fig_daily, use_container_width=True)

    with col_b:
        st.subheader("Free Periods per Trainer")
        fig_free = px.bar(
            filt.sort_values("free_periods"),
            x="free_periods",
            y="name",
            color="free_periods",
            color_continuous_scale=["#D85A30", "#FAC775", "#1D9E75"],
            orientation="h",
            text="free_periods",
            labels={"free_periods": "Free Periods", "name": "Trainer"},
        )
        fig_free.update_traces(textposition="outside")
        fig_free.update_layout(
            height=420,
            xaxis=dict(range=[0, 3], dtick=1),
            coloraxis_showscale=False,
            margin=dict(l=10, r=30, t=20, b=10),
        )
        st.plotly_chart(fig_free, use_container_width=True)

    st.subheader("Daily vs Weekly Hours Comparison")
    fig_dual = go.Figure()
    fig_dual.add_trace(go.Bar(
        name="Daily Hours",
        x=filt["name"],
        y=filt["daily_hours"],
        marker_color="#378ADD",
        text=filt["daily_hours"],
        textposition="outside",
    ))
    fig_dual.add_trace(go.Bar(
        name="Weekly Hours",
        x=filt["name"],
        y=filt["weekly_hours"],
        marker_color="#7F77DD",
        text=filt["weekly_hours"],
        textposition="outside",
        yaxis="y2",
    ))
    fig_dual.update_layout(
        height=380,
        barmode="group",
        yaxis=dict(title="Daily Hours", range=[0, 9]),
        yaxis2=dict(title="Weekly Hours", overlaying="y", side="right", range=[0, 45]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig_dual, use_container_width=True)

    st.info(
        "**Key Insight — Capacity Compression:** The majority of trainers operate at 6–7 h/day, "
        "signalling the system is near maximum capacity. A subset remains at 4–5 h, "
        "exposing inefficient workload distribution and a potential burnout risk for high-load trainers."
    )

# ══════════════════════════════════════════════
# TAB 2 — Schedule Grid
# ══════════════════════════════════════════════
with tab2:
    st.subheader("Full Slot Assignment Grid")

    def colour_slot(val):
        if val == "Free Period":
            return "background-color: #fef9ec; color: #92681d; font-weight: 500"
        return "background-color: #eaf3fb; color: #185FA5; font-weight: 500"

    display_cols = ["staff_id", "name", "course"] + TIME_COLS + ["daily_hours", "weekly_hours"]
    styled = (
        filt[display_cols]
        .rename(columns={
            "staff_id": "ID", "name": "Trainer", "course": "Course",
            "daily_hours": "Daily h", "weekly_hours": "Weekly h",
        })
        .style
        .applymap(colour_slot, subset=TIME_COLS)
        .bar(subset=["Daily h"], color="#378ADD", vmin=0, vmax=7)
    )
    st.dataframe(styled, use_container_width=True, height=430)

    st.caption("🔵 Blue = active session  |  🟡 Yellow = Free Period")

    st.subheader("Slot Occupancy Heatmap")
    heat_data = []
    for _, row in filt.iterrows():
        for slot in TIME_COLS:
            heat_data.append({
                "Trainer": row["name"],
                "Slot": slot,
                "Busy": 0 if row[slot] == "Free Period" else 1,
                "Assignment": row[slot],
            })
    heat_df = pd.DataFrame(heat_data)
    pivot = heat_df.pivot(index="Trainer", columns="Slot", values="Busy")

    fig_heat = px.imshow(
        pivot,
        color_continuous_scale=["#f1efe8", "#378ADD"],
        aspect="auto",
        labels=dict(color="Occupied"),
        title="1 = Session assigned  |  0 = Free Period",
    )
    fig_heat.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
    fig_heat.update_coloraxes(showscale=False)
    st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — Course Allocation
# ══════════════════════════════════════════════
with tab3:
    st.subheader("Daily Hours Allocated per Course")

    course_df = (
        filt.groupby("course")
        .agg(total_daily=("daily_hours", "sum"), trainer_count=("name", "count"))
        .reset_index()
        .sort_values("total_daily", ascending=False)
    )

    fig_course = px.bar(
        course_df,
        x="total_daily",
        y="course",
        color="total_daily",
        color_continuous_scale=["#9FE1CB", "#0F6E56"],
        orientation="h",
        text="total_daily",
        labels={"total_daily": "Total Daily Hours", "course": "Course"},
    )
    fig_course.update_traces(textposition="outside")
    fig_course.update_layout(
        height=380,
        coloraxis_showscale=False,
        margin=dict(l=10, r=30, t=20, b=10),
    )
    st.plotly_chart(fig_course, use_container_width=True)

    col_p, col_t = st.columns(2)

    with col_p:
        st.subheader("Hours Share by Course")
        fig_pie = px.pie(
            course_df,
            names="course",
            values="total_daily",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(height=350, showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_t:
        st.subheader("Trainers per Course")
        fig_tc = px.bar(
            course_df.sort_values("trainer_count"),
            x="trainer_count",
            y="course",
            orientation="h",
            text="trainer_count",
            color="trainer_count",
            color_continuous_scale=["#CECBF6", "#534AB7"],
            labels={"trainer_count": "No. of Trainers", "course": "Course"},
        )
        fig_tc.update_traces(textposition="outside")
        fig_tc.update_layout(
            height=350,
            coloraxis_showscale=False,
            margin=dict(l=10, r=30, t=20, b=10),
        )
        st.plotly_chart(fig_tc, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — Utilisation
# ══════════════════════════════════════════════
with tab4:
    st.subheader("Trainer Utilisation (% of 7 h max)")

    fig_util = px.bar(
        filt.sort_values("utilization_pct"),
        x="utilization_pct",
        y="name",
        color="utilization_pct",
        color_continuous_scale=["#1D9E75", "#FAC775", "#D85A30"],
        range_color=[50, 100],
        orientation="h",
        text=filt.sort_values("utilization_pct")["utilization_pct"].apply(lambda v: f"{v}%"),
        labels={"utilization_pct": "Utilisation (%)", "name": "Trainer"},
    )
    fig_util.update_traces(textposition="outside")
    fig_util.update_layout(
        height=420,
        xaxis=dict(range=[0, 115], ticksuffix="%"),
        coloraxis_showscale=False,
        margin=dict(l=10, r=30, t=20, b=10),
    )
    fig_util.add_vline(x=100, line_dash="dash", line_color="gray", annotation_text="Max (7 h)")
    st.plotly_chart(fig_util, use_container_width=True)

    st.subheader("Utilisation vs Free Periods (Scatter)")
    fig_scatter = px.scatter(
        filt,
        x="utilization_pct",
        y="free_periods",
        size="daily_hours",
        color="course",
        hover_name="name",
        hover_data={"daily_hours": True, "weekly_hours": True},
        labels={
            "utilization_pct": "Utilisation (%)",
            "free_periods": "Free Periods",
            "daily_hours": "Daily Hours",
        },
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig_scatter.update_layout(
        height=380,
        xaxis=dict(ticksuffix="%"),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    over  = filt[filt["utilization_pct"] == 100]["name"].tolist()
    under = filt[filt["utilization_pct"] <= 57]["name"].tolist()

    c1, c2 = st.columns(2)
    with c1:
        st.error(f"**⚠ Fully utilised (100%):** {', '.join(over) if over else 'None'}")
    with c2:
        st.warning(f"**📉 Under-utilised (≤57%):** {', '.join(under) if under else 'None'}")

    st.info(
        "**Recommendation:** Redistribute 1–2 sessions from fully utilised trainers "
        "(Akhil Nair, Kiran Kumar) to trainers with 2 free slots (Meera Joseph, Aravind P) "
        "to close the 43-point utilisation gap and reduce burnout risk."
    )

# ══════════════════════════════════════════════
# TAB 5 — Raw Data
# ══════════════════════════════════════════════
with tab5:
    st.subheader("Raw Dataset")
    st.dataframe(filt, use_container_width=True, height=450)

    csv_bytes = filt.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download filtered data as CSV",
        data=csv_bytes,
        file_name="filtered_staff_schedule.csv",
        mime="text/csv",
    )
