#!/usr/bin/env python
# coding: utf-8
# Cyber Square Institute — Staff Analysis Dashboard
# Run: streamlit run staff_dashboard.py

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Project root
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Cyber Square — Staff Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_DIR / "staff_dataset.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

teaching_df     = df[df["department"] == "Teaching"].copy()
non_teaching_df = df[df["department"] != "Teaching"].copy()

# ─────────────────────────────────────────────
# Sidebar filters
# ─────────────────────────────────────────────
st.sidebar.title("🔍 Filters")

dept_options = sorted(df["department"].unique().tolist())
sel_dept = st.sidebar.multiselect("Department", dept_options, default=dept_options)

hour_min, hour_max = int(df["hours_per_day"].min()), int(df["hours_per_day"].max())
sel_hours = st.sidebar.slider("Hours per Day", hour_min, hour_max, (hour_min, hour_max))

batch_options = sorted(df["batches_handling"].unique().tolist())
sel_batches = st.sidebar.multiselect("Batches Handling", batch_options, default=batch_options)

filt = df[
    df["department"].isin(sel_dept) &
    df["hours_per_day"].between(sel_hours[0], sel_hours[1]) &
    df["batches_handling"].isin(sel_batches)
].copy()

filt_teaching = filt[filt["department"] == "Teaching"].copy()

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(filt)}** of **{len(df)}** staff members")

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("📊 Staff Analysis")
st.caption("Staff composition · workload distribution · batch allocation · course dependency")
st.divider()

# ─────────────────────────────────────────────
# KPI Row
# ─────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

total_staff      = len(filt)
teaching_count   = int((filt["department"] == "Teaching").sum())
non_teaching_cnt = total_staff - teaching_count
avg_hours        = round(filt["hours_per_day"].mean(), 1) if total_staff else 0
top_trainer      = (
    filt_teaching.loc[filt_teaching["hours_per_day"].idxmax(), "name"]
    if not filt_teaching.empty else "—"
)

# ─────────────────────────────────────────────
# KPI Dashboard Card Style
# ─────────────────────────────────────────────

import plotly.graph_objects as go
import streamlit as st

# ── Figure ──
fig = go.Figure()

# ── Helper Function ──
def add_kpi(value, title, x_pos, suffix=""):
    fig.add_trace(go.Indicator(
        mode="number",
        value=value,
        title={
            "text": f"<b>{title}</b>",
            "font": {"size": 18}
        },
        number={
            "font": {"size": 42},
            "suffix": suffix
        },
        domain={'x': x_pos, 'y': [0.25, 1]}
    ))

# ── KPI Values ──
add_kpi(total_staff,      "👥 Total Staff",        [0.00, 0.22])
add_kpi(teaching_count,   "🎓 Teaching Staff",     [0.26, 0.48])
add_kpi(non_teaching_cnt, "🏢 Non-Teaching Staff", [0.52, 0.74])
add_kpi(avg_hours,        "⏱ Avg Hours / Day",    [0.78, 1.00], " h")

# ── Bottom Annotation ──
fig.add_annotation(
    x=0.5,
    y=0.02,
    text=f"🏆 <b>Most Loaded Trainer:</b> {top_trainer}",
    showarrow=False,
    xref="paper",
    yref="paper",
    font=dict(size=16),
    align="center"
)

# --- Layout ---
fig.update_layout(
    height=250,
    margin=dict(t=50, b=10, l=10, r=10)
)
# ── Remove Empty Axes/Grid ──
fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)

# ── Show ──
st.plotly_chart(fig, use_container_width=True)
# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏗 Staff Composition",
    "⏱ Workload Analysis",
    "📦 Batch Handling",
    "📚 Course Analysis",
    "📋 Raw Data",
])

# ══════════════════════════════════════════════
# TAB 1 — Staff Composition
# ══════════════════════════════════════════════
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Teaching vs Non-Teaching")
        comp_df = filt["department"].apply(
            lambda d: "Teaching" if d == "Teaching" else "Non-Teaching"
        ).value_counts().reset_index()
        comp_df.columns = ["Type", "Count"]

        fig_pie = px.pie(
            comp_df,
            names="Type",
            values="Count",
            hole=0.45,
            color="Type",
            color_discrete_map={"Teaching": "#378ADD", "Non-Teaching": "#1D9E75"},
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label+value")
        fig_pie.update_layout(height=340, showlegend=True, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.subheader("Staff by Department")
        dept_df = filt["department"].value_counts().reset_index()
        dept_df.columns = ["Department", "Count"]

        fig_dept = px.bar(
            dept_df.sort_values("Count"),
            x="Count",
            y="Department",
            orientation="h",
            text="Count",
            color="Count",
            color_continuous_scale=["#CECBF6", "#534AB7"],
        )
        fig_dept.update_traces(textposition="outside")
        fig_dept.update_layout(
            height=340, coloraxis_showscale=False,
            xaxis=dict(range=[0, dept_df["Count"].max() + 2]),
            margin=dict(l=10, r=30, t=20, b=10),
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    st.subheader("Staff Directory")
    role_color = {"Teaching": "#EAF3FB", "Non-Teaching": "#EAFAF1"}
    display = filt[["staff_id", "name", "role", "course", "department", "batches_handling", "hours_per_day"]].copy()
    display.columns = ["ID", "Name", "Role", "Course", "Department", "Batches", "Hours/Day"]
    st.dataframe(
        display.style.apply(
            lambda row: [
                f"background-color: {'#EAF3FB' if row['Department'] == 'Teaching' else '#EAFAF1'}" for _ in row
            ], axis=1
        ),
        use_container_width=True,
        hide_index=True,
        height=350,
    )

    st.info(
        f"**Teaching staff make up {teaching_count/total_staff*100:.1f}%** of total staff. "
        "Non-teaching roles include Administration, Finance, HR/Placement, Marketing, and Front Office."
        if total_staff else "No data for selected filters."
    )

# ══════════════════════════════════════════════
# TAB 2 — Workload Analysis
# ══════════════════════════════════════════════
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Staff Workload Ranking (Hours/Day)")
        fig_rank = px.bar(
            filt.sort_values("hours_per_day"),
            x="hours_per_day",
            y="name",
            color="department",
            orientation="h",
            text="hours_per_day",
            labels={"hours_per_day": "Hours/Day", "name": "Staff", "department": "Department"},
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig_rank.update_traces(textposition="outside")
        fig_rank.update_layout(
            height=450,
            xaxis=dict(range=[0, filt["hours_per_day"].max() + 1.5]),
            margin=dict(l=10, r=30, t=20, b=10),
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    with col_b:
        st.subheader("Hours Distribution")
        fig_hist = px.histogram(
            filt,
            x="hours_per_day",
            color="department",
            nbins=8,
            barmode="overlay",
            labels={"hours_per_day": "Hours/Day", "department": "Department"},
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig_hist.update_layout(
            height=220,
            bargap=0.1,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        st.subheader("Hours Stats by Department")
        stats = (
            filt.groupby("department")["hours_per_day"]
            .agg(["mean", "min", "max", "count"])
            .round(1)
            .reset_index()
        )
        stats.columns = ["Department", "Avg h", "Min h", "Max h", "Count"]
        st.dataframe(stats, use_container_width=True, hide_index=True)

    st.subheader("Teaching Staff — Workload vs Avg Line")
    if not filt_teaching.empty:
        avg_line = filt_teaching["hours_per_day"].mean()
        fig_line = px.bar(
            filt_teaching.sort_values("hours_per_day", ascending=False),
            x="name",
            y="hours_per_day",
            color="hours_per_day",
            color_continuous_scale=["#1D9E75", "#FAC775", "#D85A30"],
            text="hours_per_day",
            labels={"hours_per_day": "Hours/Day", "name": "Trainer"},
        )
        fig_line.add_hline(
            y=avg_line, line_dash="dash", line_color="#185FA5",
            annotation_text=f"Avg: {avg_line:.1f} h", annotation_position="top right"
        )
        fig_line.update_traces(textposition="outside")
        fig_line.update_layout(
            height=320,
            coloraxis_showscale=False,
            yaxis=dict(range=[0, filt_teaching["hours_per_day"].max() + 1.5]),
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.warning(
        "**Workload Gap:** Hours range from "
        f"**{filt['hours_per_day'].min()} h** (min) to **{filt['hours_per_day'].max()} h** (max) — "
        f"a gap of **{filt['hours_per_day'].max() - filt['hours_per_day'].min()} h**. "
        "Non-teaching staff consistently work 8 h while teaching staff vary between 2–5 h."
    )

# ══════════════════════════════════════════════
# TAB 3 — Batch Handling
# ══════════════════════════════════════════════
with tab3:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Batch Allocation per Trainer")
        if not filt_teaching.empty:
            fig_batch = px.bar(
                filt_teaching.sort_values("batches_handling"),
                x="batches_handling",
                y="name",
                orientation="h",
                color="batches_handling",
                color_continuous_scale=["#9FE1CB", "#0F6E56"],
                text="batches_handling",
                labels={"batches_handling": "Batches", "name": "Trainer"},
            )
            fig_batch.update_traces(textposition="outside")
            fig_batch.update_layout(
                height=380,
                coloraxis_showscale=False,
                xaxis=dict(range=[0, filt_teaching["batches_handling"].max() + 1], dtick=1),
                margin=dict(l=10, r=30, t=20, b=10),
            )
            st.plotly_chart(fig_batch, use_container_width=True)

    with col_b:
        st.subheader("Batch Count Distribution")
        if not filt_teaching.empty:
            batch_dist = filt_teaching["batches_handling"].value_counts().reset_index()
            batch_dist.columns = ["Batches", "Trainers"]
            fig_bdist = px.pie(
                batch_dist,
                names="Batches",
                values="Trainers",
                hole=0.45,
                color_discrete_sequence=["#378ADD", "#1D9E75", "#D85A30"],
            )
            fig_bdist.update_traces(textposition="inside", textinfo="percent+label+value")
            fig_bdist.update_layout(
                height=220,
                showlegend=True,
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig_bdist, use_container_width=True)

            st.subheader("Batch vs Hours Scatter")
            fig_scatter = px.scatter(
                filt_teaching,
                x="batches_handling",
                y="hours_per_day",
                size="hours_per_day",
                color="hours_per_day",
                hover_name="name",
                hover_data={"course": True},
                color_continuous_scale=["#1D9E75", "#FAC775", "#D85A30"],
                labels={"batches_handling": "Batches Handling", "hours_per_day": "Hours/Day"},
            )
            fig_scatter.update_layout(
                height=250,
                coloraxis_showscale=False,
                xaxis=dict(dtick=1),
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Workload vs Batch Responsibility (Grouped)")
    if not filt_teaching.empty:
        fig_box = px.box(
            filt_teaching,
            x="batches_handling",
            y="hours_per_day",
            points="all",
            hover_name="name",
            color="batches_handling",
            color_discrete_sequence=["#378ADD", "#1D9E75", "#D85A30"],
            labels={"batches_handling": "Batches Handling", "hours_per_day": "Hours/Day"},
        )
        fig_box.update_layout(
            height=300,
            showlegend=False,
            xaxis=dict(dtick=1),
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.info(
        "**Batch count is not the sole driver of workload.** "
        "Trainers with the same batch count (e.g. 3 batches) show varying hours (3–5 h), "
        "indicating course complexity and scheduling differences play a significant role."
    )

# ══════════════════════════════════════════════
# TAB 4 — Course Analysis
# ══════════════════════════════════════════════
with tab4:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Trainers per Course")
        if not filt_teaching.empty:
            course_counts = filt_teaching["course"].value_counts().reset_index()
            course_counts.columns = ["Course", "Trainers"]
            fig_course = px.bar(
                course_counts.sort_values("Trainers"),
                x="Trainers",
                y="Course",
                orientation="h",
                text="Trainers",
                color="Trainers",
                color_continuous_scale=["#D85A30", "#FAC775", "#1D9E75"],
            )
            fig_course.update_traces(textposition="outside")
            fig_course.add_vline(
                x=1, line_dash="dash", line_color="gray",
                annotation_text="Single trainer risk"
            )
            fig_course.update_layout(
                height=380,
                coloraxis_showscale=False,
                xaxis=dict(range=[0, course_counts["Trainers"].max() + 1], dtick=1),
                margin=dict(l=10, r=40, t=20, b=10),
            )
            st.plotly_chart(fig_course, use_container_width=True)

    with col_b:
        st.subheader("Avg Hours by Course")
        if not filt_teaching.empty:
            course_hrs = (
                filt_teaching.groupby("course")["hours_per_day"]
                .mean().round(1).reset_index()
                .sort_values("hours_per_day")
            )
            course_hrs.columns = ["Course", "Avg Hours"]
            fig_chr = px.bar(
                course_hrs,
                x="Avg Hours",
                y="Course",
                orientation="h",
                text="Avg Hours",
                color="Avg Hours",
                color_continuous_scale=["#9FE1CB", "#0F6E56"],
            )
            fig_chr.update_traces(textposition="outside")
            fig_chr.update_layout(
                height=380,
                coloraxis_showscale=False,
                xaxis=dict(range=[0, course_hrs["Avg Hours"].max() + 1]),
                margin=dict(l=10, r=30, t=20, b=10),
            )
            st.plotly_chart(fig_chr, use_container_width=True)

    st.subheader("Course Dependency Risk")
    if not filt_teaching.empty:
        risk_df = filt_teaching.groupby("course").agg(
            Trainers=("name", "count"),
            Avg_Hours=("hours_per_day", "mean"),
            Total_Batches=("batches_handling", "sum"),
        ).reset_index().round(1)
        risk_df["Risk"] = risk_df["Trainers"].apply(
            lambda x: "🔴 High Risk" if x == 1 else "🟢 Low Risk"
        )
        risk_df.columns = ["Course", "Trainers", "Avg Hours", "Total Batches", "Risk"]
        st.dataframe(risk_df, use_container_width=True, hide_index=True, height=380)

    single = int((filt_teaching["course"].value_counts() == 1).sum()) if not filt_teaching.empty else 0
    multi  = int((filt_teaching["course"].value_counts() > 1).sum()) if not filt_teaching.empty else 0
    st.error(
        f"**⚠ {single} course(s)** rely on a single trainer — creating operational risk. "
        f"Only **{multi} course(s)** have backup trainer coverage."
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
        file_name="filtered_staff_dataset.csv",
        mime="text/csv",
    )
