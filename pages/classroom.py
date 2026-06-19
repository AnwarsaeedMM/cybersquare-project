#!/usr/bin/env python
# coding: utf-8
# Cyber Square Institute — Classroom Schedule Dashboard
# Run: streamlit run class_dashboard.py

import warnings
warnings.filterwarnings("ignore")


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Project root
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Classroom Dashboard — Cyber Square",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────

DATA_PATH = DATA_DIR / "classroom.csv"

TIME_SLOTS = ["10:00-12:00", "12:00-02:00", "02:30-04:30", "04:30-05:30"]

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    for col in TIME_SLOTS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    def slot_filled(row):
        return sum(1 for s in TIME_SLOTS if row.get(s, "").strip() not in ["", "nan", "None"])

    df["filled_slots"] = df.apply(slot_filled, axis=1)
    df["utilization_pct"] = (df["filled_slots"] / len(TIME_SLOTS) * 100).round(1)

    def occupancy_status(row):
        if row["filled_slots"] == len(TIME_SLOTS):
            return "Fully Occupied"
        elif row["filled_slots"] > 0:
            return "Partially Used"
        else:
            return "Unused"

    df["status"] = df.apply(occupancy_status, axis=1)

    # Extract unique courses from all slots
    all_courses = []
    for s in TIME_SLOTS:
        all_courses.extend(df[s].tolist())
    df["courses_assigned"] = df[TIME_SLOTS].apply(
        lambda row: ", ".join([v for v in row if v not in ["", "nan", "None"]]), axis=1
    )
    return df

df = load_data(DATA_PATH)

# Melt to long form for charts
long_df = df.melt(
    id_vars=["CID", "Occupancy", "status", "utilization_pct"],
    value_vars=TIME_SLOTS,
    var_name="Slot",
    value_name="Batch",
)
long_df["Occupied"] = long_df["Batch"].apply(
    lambda x: 0 if str(x).strip() in ["", "nan", "None"] else 1
)

# ─────────────────────────────────────────────
# Sidebar filters
# ─────────────────────────────────────────────
st.sidebar.title("🔍 Filters")

all_cids = sorted(df["CID"].unique().tolist())
sel_rooms = st.sidebar.multiselect("Classroom", all_cids, default=all_cids)

all_statuses = df["status"].unique().tolist()
sel_status = st.sidebar.multiselect("Occupancy Status", all_statuses, default=all_statuses)

sel_slots = st.sidebar.multiselect("Time Slots", TIME_SLOTS, default=TIME_SLOTS)

filt = df[df["CID"].isin(sel_rooms) & df["status"].isin(sel_status)].copy()
filt_long = long_df[long_df["CID"].isin(sel_rooms) & long_df["Slot"].isin(sel_slots)].copy()

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(filt)}** of **{len(df)}** classrooms")

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("🏫 Classroom Dashboard")
st.caption("Classroom utilisation · slot occupancy · batch allocation")
st.divider()

# ─────────────────────────────────────────────
# KPI Row
# ─────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

total_rooms    = len(filt)
fully_occ      = int((filt["status"] == "Fully Occupied").sum())
unused         = int((filt["status"] == "Unused").sum())
avg_util       = round(filt["utilization_pct"].mean(), 1)

k1.metric("🏫 Total Rooms",       total_rooms)
k2.metric("✅ Fully Occupied",    fully_occ)
k3.metric("⬜ Unused",            unused)
k4.metric("📊 Avg Utilisation",   f"{avg_util}%")

st.divider()

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Schedule Grid",
    "📈 Utilisation",
    "🗂 Batch Allocation",
    "🔥 Slot Heatmap",
    "📋 Raw Data",
])

# ══════════════════════════════════════════════
# TAB 1 — Schedule Grid (Heatmap)
# ══════════════════════════════════════════════
with tab1:
    st.subheader("Classroom × Time Slot Schedule")

    slot_cols = [s for s in sel_slots if s in TIME_SLOTS]

    z_text, z_val = [], []
    for _, row in filt.iterrows():
        row_text, row_val = [], []
        for i, s in enumerate(slot_cols):
            cell = str(row.get(s, "")).strip()
            row_text.append(cell if cell not in ["", "nan", "None"] else "—")
            row_val.append(i + 1)
        z_text.append(row_text)
        z_val.append(row_val)

    colorscales = [
        [0.00, "#AED6F1"], [0.25, "#A9DFBF"],
        [0.50, "#FAD7A0"], [0.75, "#D2B4DE"],
        [1.00, "#F9E79F"],
    ]

    fig_grid = go.Figure(go.Heatmap(
        z=z_val,
        x=slot_cols,
        y=filt["CID"].tolist(),
        text=z_text,
        texttemplate="%{text}",
        textfont_size=12,
        colorscale=colorscales,
        showscale=False,
        hovertemplate="<b>%{y}  —  %{x}</b><br>Batch: %{text}<extra></extra>",
    ))
    fig_grid.update_layout(
        xaxis_title="Time Slot",
        yaxis_title="Classroom",
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_grid, use_container_width=True)
    st.caption("Each cell shows the batch assigned to that room and time slot.")

    # Slot-wise occupancy summary table
    st.subheader("Slot-wise Occupancy Summary")
    summary_rows = []
    for s in slot_cols:
        filled = filt[s].apply(lambda x: str(x).strip() not in ["", "nan", "None"]).sum()
        summary_rows.append({
            "Time Slot": s,
            "Rooms Occupied": int(filled),
            "Rooms Free": int(len(filt) - filled),
            "Occupancy %": f"{round(filled / len(filt) * 100, 1)}%" if len(filt) > 0 else "0%",
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 2 — Utilisation
# ══════════════════════════════════════════════
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Room Utilisation (%)")
        status_color = {
            "Fully Occupied": "#1D9E75",
            "Partially Used": "#378ADD",
            "Unused":         "#D85A30",
        }
        fig_util = px.bar(
            filt.sort_values("utilization_pct"),
            x="utilization_pct",
            y="CID",
            color="status",
            color_discrete_map=status_color,
            orientation="h",
            text=filt.sort_values("utilization_pct")["utilization_pct"].apply(lambda v: f"{v}%"),
            labels={"utilization_pct": "Utilisation (%)", "CID": "Classroom", "status": "Status"},
        )
        fig_util.update_traces(textposition="outside")
        fig_util.add_vline(x=100, line_dash="dash", line_color="gray", annotation_text="100%")
        fig_util.update_layout(
            height=340,
            xaxis=dict(range=[0, 120], ticksuffix="%"),
            margin=dict(l=10, r=30, t=20, b=10),
        )
        st.plotly_chart(fig_util, use_container_width=True)

    with col_b:
        st.subheader("Occupancy Status Breakdown")
        status_counts = filt["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_pie = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.45,
            color="Status",
            color_discrete_map=status_color,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(
            height=340,
            showlegend=True,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Filled Slots per Classroom")
    fig_filled = px.bar(
        filt,
        x="CID",
        y="filled_slots",
        color="status",
        color_discrete_map=status_color,
        text="filled_slots",
        labels={"filled_slots": "Filled Slots", "CID": "Classroom", "status": "Status"},
    )
    fig_filled.update_traces(textposition="outside")
    fig_filled.add_hline(
        y=len(TIME_SLOTS), line_dash="dash", line_color="gray",
        annotation_text=f"Max ({len(TIME_SLOTS)} slots)"
    )
    fig_filled.update_layout(
        height=320,
        yaxis=dict(range=[0, len(TIME_SLOTS) + 1], dtick=1),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_filled, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — Batch Allocation
# ══════════════════════════════════════════════
with tab3:
    st.subheader("Batch → Classroom Mapping")

    batch_rows = []
    for _, row in filt.iterrows():
        for s in TIME_SLOTS:
            val = str(row.get(s, "")).strip()
            if val not in ["", "nan", "None"]:
                batch_rows.append({"Classroom": row["CID"], "Slot": s, "Batch": val, "Occupancy": row["Occupancy"]})

    batch_df = pd.DataFrame(batch_rows)

    if not batch_df.empty:
        col_x, col_y = st.columns(2)

        with col_x:
            st.subheader("Batches per Classroom")
            bpc = batch_df.groupby("Classroom")["Batch"].count().reset_index()
            bpc.columns = ["Classroom", "Batch Count"]
            fig_bpc = px.bar(
                bpc,
                x="Classroom", y="Batch Count",
                color="Batch Count",
                color_continuous_scale=["#9FE1CB", "#0F6E56"],
                text="Batch Count",
            )
            fig_bpc.update_traces(textposition="outside")
            fig_bpc.update_layout(
                height=300, coloraxis_showscale=False,
                yaxis=dict(range=[0, len(TIME_SLOTS) + 1], dtick=1),
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig_bpc, use_container_width=True)

        with col_y:
            st.subheader("Batches per Time Slot")
            bps = batch_df.groupby("Slot")["Batch"].count().reset_index()
            bps.columns = ["Slot", "Batch Count"]
            bps["Slot"] = pd.Categorical(bps["Slot"], categories=TIME_SLOTS, ordered=True)
            bps = bps.sort_values("Slot")
            fig_bps = px.bar(
                bps,
                x="Slot", y="Batch Count",
                color="Batch Count",
                color_continuous_scale=["#CECBF6", "#534AB7"],
                text="Batch Count",
            )
            fig_bps.update_traces(textposition="outside")
            fig_bps.update_layout(
                height=300, coloraxis_showscale=False,
                yaxis=dict(range=[0, len(filt) + 1], dtick=1),
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig_bps, use_container_width=True)

        st.subheader("Full Batch Assignment Table")
        st.dataframe(batch_df, use_container_width=True, hide_index=True)
    else:
        st.info("No batch data available for selected filters.")

# ══════════════════════════════════════════════
# TAB 4 — Slot Heatmap (Occupied / Free)
# ══════════════════════════════════════════════
with tab4:
    st.subheader("Slot Occupancy Heatmap (1 = Occupied, 0 = Free)")

    pivot = filt_long[filt_long["Slot"].isin(sel_slots)].pivot_table(
        index="CID", columns="Slot", values="Occupied", aggfunc="max"
    ).reindex(columns=sel_slots)

    if not pivot.empty:
        fig_heat = px.imshow(
            pivot,
            color_continuous_scale=["#f1efe8", "#1D9E75"],
            aspect="auto",
            text_auto=True,
            labels=dict(color="Occupied"),
        )
        fig_heat.update_coloraxes(showscale=False)
        fig_heat.update_layout(
            height=320,
            xaxis_title="Time Slot",
            yaxis_title="Classroom",
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("Slot Load — How Many Rooms Are Occupied Each Slot")
    slot_load = (
        filt_long[filt_long["Slot"].isin(sel_slots)]
        .groupby("Slot")["Occupied"].sum()
        .reset_index()
    )
    slot_load["Slot"] = pd.Categorical(slot_load["Slot"], categories=TIME_SLOTS, ordered=True)
    slot_load = slot_load.sort_values("Slot")

    fig_load = px.line(
        slot_load,
        x="Slot",
        y="Occupied",
        markers=True,
        text="Occupied",
        labels={"Occupied": "Rooms Occupied", "Slot": "Time Slot"},
        color_discrete_sequence=["#378ADD"],
    )
    fig_load.update_traces(textposition="top center", line_width=2.5, marker_size=9)
    fig_load.add_hline(
        y=len(filt), line_dash="dash", line_color="#D85A30",
        annotation_text=f"Max ({len(filt)} rooms)"
    )
    fig_load.update_layout(
        height=300,
        yaxis=dict(range=[0, len(filt) + 1], dtick=1),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_load, use_container_width=True)

    st.info(
        "**Key Insight:** All 5 classrooms are fully occupied across all 4 time slots "
        "— 100% utilisation with no idle capacity. This indicates maximum scheduling efficiency "
        "but leaves zero buffer for demand spikes or maintenance windows."
    )

# ══════════════════════════════════════════════
# TAB 5 — Raw Data
# ══════════════════════════════════════════════
with tab5:
    st.subheader("Raw Dataset")
    st.dataframe(filt, use_container_width=True, height=420)

    csv_bytes = filt.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download filtered data as CSV",
        data=csv_bytes,
        file_name="filtered_classroom.csv",
        mime="text/csv",
    )
