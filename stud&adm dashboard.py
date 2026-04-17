"""
Student & Admission Insights Dashboard
A professional BI dashboard built with Streamlit and Plotly.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Student & Admission Insights",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME / GLOBAL STYLE
# ─────────────────────────────────────────────
PALETTE = {
    "primary":   "#2563EB",   # blue
    "secondary": "#10B981",   # green
    "accent":    "#F59E0B",   # amber
    "danger":    "#EF4444",   # red
    "gray":      "#6B7280",
    "light":     "#F3F4F6",
    "courses": px.colors.qualitative.Pastel,
}

st.markdown(
    """
    <style>
        /* ── Global Reset ── */
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .main { background: #FFFFFF; }
        section[data-testid="stSidebar"] { background: #F8FAFC; border-right: 1px solid #E2E8F0; }

        /* ── KPI Cards ── */
        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px 24px;
            box-shadow: 0 1px 4px rgba(0,0,0,.06);
        }
        .kpi-label  { font-size: 12px; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: .6px; margin-bottom: 6px; }
        .kpi-value  { font-size: 32px; font-weight: 700; color: #111827; line-height: 1; }
        .kpi-delta  { font-size: 13px; margin-top: 6px; color: #6B7280; }
        .kpi-delta .up   { color: #10B981; font-weight: 600; }
        .kpi-delta .down { color: #EF4444; font-weight: 600; }

        /* ── Section Headers ── */
        .section-header {
            font-size: 17px;
            font-weight: 700;
            color: #111827;
            padding-bottom: 4px;
            border-bottom: 2px solid #2563EB;
            margin-bottom: 16px;
            display: inline-block;
        }

        /* ── Divider ── */
        hr { border: none; border-top: 1px solid #E2E8F0; margin: 24px 0; }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    students   = pd.read_csv("students.csv")
    admissions = pd.read_csv("admission.csv")

    # Parse dates
    students["enrollment_date"]  = pd.to_datetime(students["enrollment_date"],  dayfirst=False, errors="coerce")
    admissions["admission_date"] = pd.to_datetime(admissions["admission_date"], dayfirst=False, errors="coerce")

    # Derived columns
    students["enrollment_month"]    = students["enrollment_date"].dt.to_period("M").astype(str)
    admissions["admission_month"]   = admissions["admission_date"].dt.to_period("M").astype(str)
    admissions["is_admitted"]       = admissions["status"] == "Admitted"

    return students, admissions


students_raw, admissions_raw = load_data()


# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")

    all_courses = sorted(students_raw["course"].dropna().unique().tolist())
    sel_courses = st.multiselect("📚 Course", all_courses, default=all_courses)

    all_modes = sorted(students_raw["mode"].dropna().unique().tolist())
    sel_modes = st.multiselect("🖥️ Mode", all_modes, default=all_modes)

    all_edu = sorted(students_raw["education_level"].dropna().unique().tolist())
    sel_edu = st.multiselect("🎓 Education Level", all_edu, default=all_edu)

    all_locations = sorted(admissions_raw["location"].dropna().unique().tolist())
    sel_locations = st.multiselect("📍 Location", all_locations, default=all_locations)

    st.markdown("---")
    st.caption("Data last refreshed on load.")


# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
students = students_raw[
    students_raw["course"].isin(sel_courses) &
    students_raw["mode"].isin(sel_modes) &
    students_raw["education_level"].isin(sel_edu)
].copy()

admissions = admissions_raw[
    admissions_raw["course"].isin(sel_courses) &
    admissions_raw["mode"].isin(sel_modes) &
    admissions_raw["location"].isin(sel_locations)
].copy()


# ─────────────────────────────────────────────
# HELPER: chart layout defaults
# ─────────────────────────────────────────────
def clean_layout(fig, title="", height=340):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#111827"), x=0),
        height=height,
        margin=dict(l=16, r=16, t=40, b=16),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter", size=12, color="#374151"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(showgrid=False, linecolor="#E2E8F0", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#F3F4F6", linecolor="#E2E8F0", tickfont=dict(size=11)),
    )
    return fig


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    """
    <div style="padding: 8px 0 20px 0;">
        <div style="font-size:26px; font-weight:800; color:#111827;">🎓 Student & Admission Insights Dashboard</div>
        <div style="font-size:14px; color:#6B7280; margin-top:4px;">
            A 360° view of enrollment patterns, admission trends, and course performance.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# KPI METRICS
# ─────────────────────────────────────────────
total_students   = len(students)
total_admissions = len(admissions)
admitted         = admissions["is_admitted"].sum()
not_admitted     = (~admissions["is_admitted"]).sum()
admission_rate   = round(admitted / total_admissions * 100, 1) if total_admissions else 0
internship_pct   = round((students["internship"] != "No").sum() / total_students * 100, 1) if total_students else 0

k1, k2, k3, k4 = st.columns(4)

def kpi_card(col, label, value, delta_html=""):
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">{delta_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

kpi_card(k1, "Total Students",   total_students,
         f"<span>{len(students_raw)} in full dataset</span>")
kpi_card(k2, "Total Inquiries",  total_admissions,
         f"<span>{len(admissions_raw)} in full dataset</span>")
kpi_card(k3, "Admission Rate",   f"{admission_rate}%",
         f'<span class="up">✔ {admitted} admitted</span> &nbsp;|&nbsp; '
         f'<span class="down">✘ {not_admitted} not admitted</span>')
kpi_card(k4, "Internship Rate",  f"{internship_pct}%",
         f"<span>Students with internship placement</span>")

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION A — STUDENT INSIGHTS
# ─────────────────────────────────────────────
st.markdown('<span class="section-header">📊 Student Insights</span>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# 1. Course-wise student count
with col1:
    course_counts = students["course"].value_counts().reset_index()
    course_counts.columns = ["Course", "Students"]
    fig = px.bar(
        course_counts, x="Students", y="Course",
        orientation="h",
        color="Course",
        color_discrete_sequence=PALETTE["courses"],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False)
    clean_layout(fig, "Students by Course")
    st.plotly_chart(fig, use_container_width=True)

# 2. Education level distribution
with col2:
    edu_counts = students["education_level"].value_counts().reset_index()
    edu_counts.columns = ["Education Level", "Count"]
    fig = px.pie(
        edu_counts, names="Education Level", values="Count",
        hole=0.55,
        color_discrete_sequence=[PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"], "#A78BFA"],
    )
    fig.update_traces(textposition="outside", textinfo="percent+label",
                      marker=dict(line=dict(color="white", width=2)))
    clean_layout(fig, "Education Level Split")
    st.plotly_chart(fig, use_container_width=True)

# 3. Mode (Online vs Offline)
with col3:
    mode_counts = students["mode"].value_counts().reset_index()
    mode_counts.columns = ["Mode", "Count"]
    fig = px.bar(
        mode_counts, x="Mode", y="Count",
        color="Mode",
        color_discrete_map={"Online": PALETTE["primary"], "Offline": PALETTE["secondary"]},
        text="Count",
    )
    fig.update_traces(marker_line_width=0, textposition="outside")
    fig.update_layout(showlegend=False)
    clean_layout(fig, "Online vs Offline Enrollment")
    st.plotly_chart(fig, use_container_width=True)

# Row 2 — Age distribution + Enrollment over time
col4, col5 = st.columns([1, 2])

with col4:
    fig = px.histogram(
        students, x="age", nbins=15,
        color_discrete_sequence=[PALETTE["primary"]],
    )
    fig.update_traces(marker_line_color="white", marker_line_width=1)
    clean_layout(fig, "Age Distribution of Students")
    st.plotly_chart(fig, use_container_width=True)

with col5:
    enroll_trend = (
        students.groupby("enrollment_month")
        .size()
        .reset_index(name="Count")
        .sort_values("enrollment_month")
    )
    fig = px.area(
        enroll_trend, x="enrollment_month", y="Count",
        color_discrete_sequence=[PALETTE["primary"]],
        markers=True,
    )
    fig.update_traces(line_width=2.5, marker_size=5)
    clean_layout(fig, "Enrollment Trend Over Time")
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION B — ADMISSION INSIGHTS
# ─────────────────────────────────────────────
st.markdown('<span class="section-header">📋 Admission Insights</span>', unsafe_allow_html=True)

col6, col7, col8 = st.columns(3)

# Admissions over time
with col6:
    adm_trend = (
        admissions.groupby("admission_month")
        .size()
        .reset_index(name="Inquiries")
        .sort_values("admission_month")
    )
    fig = px.line(
        adm_trend, x="admission_month", y="Inquiries",
        color_discrete_sequence=[PALETTE["secondary"]],
        markers=True,
    )
    fig.update_traces(line_width=2.5, marker_size=6)
    clean_layout(fig, "Admission Inquiries Over Time")
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

# Status distribution
with col7:
    status_counts = admissions["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig = px.pie(
        status_counts, names="Status", values="Count",
        hole=0.55,
        color_discrete_map={"Admitted": PALETTE["secondary"], "Not Admitted": PALETTE["danger"]},
    )
    fig.update_traces(textposition="outside", textinfo="percent+label",
                      marker=dict(line=dict(color="white", width=2)))
    clean_layout(fig, "Admission Status")
    st.plotly_chart(fig, use_container_width=True)

# Admissions by location
with col8:
    loc_counts = admissions["location"].value_counts().reset_index()
    loc_counts.columns = ["Location", "Count"]
    fig = px.bar(
        loc_counts, x="Location", y="Count",
        color="Location",
        color_discrete_sequence=PALETTE["courses"],
        text="Count",
    )
    fig.update_traces(marker_line_width=0, textposition="outside")
    fig.update_layout(showlegend=False)
    clean_layout(fig, "Inquiries by Location")
    st.plotly_chart(fig, use_container_width=True)

# Row 2 — Course-wise admission rate + Counsellor performance
col9, col10 = st.columns(2)

with col9:
    course_adm = admissions.groupby("course")["is_admitted"].agg(["sum", "count"]).reset_index()
    course_adm.columns = ["Course", "Admitted", "Total"]
    course_adm["Admission Rate (%)"] = (course_adm["Admitted"] / course_adm["Total"] * 100).round(1)
    course_adm = course_adm.sort_values("Admission Rate (%)", ascending=True)

    fig = px.bar(
        course_adm, x="Admission Rate (%)", y="Course",
        orientation="h",
        color="Admission Rate (%)",
        color_continuous_scale=["#BFDBFE", PALETTE["primary"]],
        text="Admission Rate (%)",
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
    fig.update_coloraxes(showscale=False)
    clean_layout(fig, "Admission Rate (%) by Course")
    st.plotly_chart(fig, use_container_width=True)

with col10:
    counsellor = admissions.groupby("attended_by")["is_admitted"].agg(["sum", "count"]).reset_index()
    counsellor.columns = ["Counsellor", "Admitted", "Total Handled"]
    counsellor["Not Admitted"] = counsellor["Total Handled"] - counsellor["Admitted"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Admitted",
        x=counsellor["Counsellor"], y=counsellor["Admitted"],
        marker_color=PALETTE["secondary"], text=counsellor["Admitted"],
        textposition="inside", marker_line_width=0,
    ))
    fig.add_trace(go.Bar(
        name="Not Admitted",
        x=counsellor["Counsellor"], y=counsellor["Not Admitted"],
        marker_color="#FCA5A5", text=counsellor["Not Admitted"],
        textposition="inside", marker_line_width=0,
    ))
    fig.update_layout(barmode="stack")
    clean_layout(fig, "Counsellor Performance — Admissions Handled")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION C — COMBINED INSIGHTS
# ─────────────────────────────────────────────
st.markdown('<span class="section-header">🔗 Combined Insights</span>', unsafe_allow_html=True)

col11, col12 = st.columns(2)

# Inquiry → Enrollment funnel per course
with col11:
    inq_course  = admissions.groupby("course").size().reset_index(name="Inquiries")
    enr_course  = students.groupby("course").size().reset_index(name="Enrolled")
    funnel_df   = pd.merge(inq_course, enr_course, on="course", how="outer").fillna(0)
    funnel_df   = funnel_df.sort_values("Inquiries", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Inquiries", x=funnel_df["course"], y=funnel_df["Inquiries"],
        marker_color="#BFDBFE", marker_line_width=0,
    ))
    fig.add_trace(go.Bar(
        name="Enrolled", x=funnel_df["course"], y=funnel_df["Enrolled"],
        marker_color=PALETTE["primary"], marker_line_width=0,
    ))
    fig.update_layout(barmode="group")
    clean_layout(fig, "Inquiry vs Enrollment by Course")
    fig.update_xaxes(tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

# Monthly inquiries vs enrollments on dual axis
with col12:
    monthly_adm = (
        admissions.groupby("admission_month").size()
        .reset_index(name="Inquiries")
        .sort_values("admission_month")
    )
    monthly_stu = (
        students.groupby("enrollment_month").size()
        .reset_index(name="Enrolled")
        .rename(columns={"enrollment_month": "admission_month"})
        .sort_values("admission_month")
    )
    combined = pd.merge(monthly_adm, monthly_stu, on="admission_month", how="outer").fillna(0)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(name="Inquiries", x=combined["admission_month"], y=combined["Inquiries"],
               marker_color="#BFDBFE", marker_line_width=0),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(name="Enrolled", x=combined["admission_month"], y=combined["Enrolled"],
                   mode="lines+markers", line=dict(color=PALETTE["primary"], width=2.5),
                   marker=dict(size=6)),
        secondary_y=True,
    )
    fig.update_layout(
        height=340,
        margin=dict(l=16, r=16, t=44, b=16),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter", size=12),
        title=dict(text="Monthly Inquiries vs Enrolled (Dual Axis)", font=dict(size=14), x=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(showgrid=False, linecolor="#E2E8F0", tickangle=-30, tickfont=dict(size=11)),
    )
    fig.update_yaxes(title_text="Inquiries", secondary_y=False,
                     gridcolor="#F3F4F6", tickfont=dict(size=11))
    fig.update_yaxes(title_text="Enrolled",  secondary_y=True,
                     tickfont=dict(size=11))
    st.plotly_chart(fig, use_container_width=True)

# Qualification mix in admissions + Duration preference
col13, col14 = st.columns(2)

with col13:
    qual_counts = admissions["qualification"].value_counts().reset_index()
    qual_counts.columns = ["Qualification", "Count"]
    fig = px.bar(
        qual_counts, x="Qualification", y="Count",
        color="Qualification",
        color_discrete_sequence=PALETTE["courses"],
        text="Count",
    )
    fig.update_traces(marker_line_width=0, textposition="outside")
    fig.update_layout(showlegend=False)
    clean_layout(fig, "Inquiry Leads by Qualification")
    st.plotly_chart(fig, use_container_width=True)

with col14:
    dur_counts = students["duration"].value_counts().reset_index()
    dur_counts.columns = ["Duration", "Students"]
    fig = px.pie(
        dur_counts, names="Duration", values="Students",
        hole=0.5,
        color_discrete_sequence=[PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"]],
    )
    fig.update_traces(textposition="outside", textinfo="percent+label",
                      marker=dict(line=dict(color="white", width=2)))
    clean_layout(fig, "Course Duration Preference")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECTION D — DATA TABLE (Optional exploration)
# ─────────────────────────────────────────────
with st.expander("🗂️ Raw Data Explorer", expanded=False):
    tab1, tab2 = st.tabs(["Students", "Admissions"])
    with tab1:
        st.dataframe(students.reset_index(drop=True), use_container_width=True, height=300)
    with tab2:
        st.dataframe(admissions.reset_index(drop=True), use_container_width=True, height=300)

# Footer
st.markdown(
    "<div style='text-align:center; color:#9CA3AF; font-size:12px; padding: 16px 0;'>"
    "Student & Admission Insights Dashboard • Built with Streamlit & Plotly</div>",
    unsafe_allow_html=True,
)
