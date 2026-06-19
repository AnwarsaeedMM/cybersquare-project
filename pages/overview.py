from pathlib import Path
import warnings
warnings.filterwarnings("ignore")
import streamlit as st  
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from IPython.display import HTML, display
from pathlib import Path



THEME = {
    "navy": "#0B1F3A",
    "navy_2": "#102A43",
    "ink": "#172033",
    "muted": "#667085",
    "line": "#E6EAF0",
    "panel": "#F7F9FC",
    "white": "#FFFFFF",
    "blue": "#2F80ED",
    "teal": "#00A6A6",
    "green": "#21A67A",
    "amber": "#F5A623",
    "red": "#D64545",
    "violet": "#7C3AED",
    "slate": "#475467",
}

PALETTE = [
    THEME["blue"], THEME["teal"], THEME["green"], THEME["amber"],
    THEME["violet"], "#344054", "#98A2B3", THEME["red"],
]




px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = PALETTE

display(HTML(f"""
<style>
    div#notebook-container, .jp-Notebook {{
        background: {THEME["white"]};
    }}
    .rendered_html, .jp-RenderedHTMLCommon {{
        font-family: Inter, Segoe UI, Arial, sans-serif;
        color: {THEME["ink"]};
    }}
    .rendered_html h1, .rendered_html h2, .rendered_html h3,
    .jp-RenderedHTMLCommon h1, .jp-RenderedHTMLCommon h2, .jp-RenderedHTMLCommon h3 {{
        color: {THEME["navy"]};
        letter-spacing: 0;
        font-weight: 800;
    }}
    .executive-hero {{
        background: linear-gradient(135deg, {THEME["navy"]} 0%, {THEME["navy_2"]} 100%);
        color: white;
        padding: 28px 32px;
        border-radius: 8px;
        margin: 10px 0 24px 0;
        box-shadow: 0 18px 45px rgba(11,31,58,.16);
    }}
    .executive-hero h1 {{
        margin: 0 0 8px 0;
        color: white;
        font-size: 30px;
        line-height: 1.15;
    }}
    .executive-hero p {{
        margin: 0;
        color: #D9E2EC;
        font-size: 14px;
    }}
    .section-divider {{
        margin: 30px 0 14px 0;
        padding: 0 0 10px 0;
        border-bottom: 1px solid {THEME["line"]};
        color: {THEME["navy"]};
        font-size: 20px;
        font-weight: 800;
    }}
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin: 10px 0 24px 0;
    }}
    .kpi-card {{
        background: {THEME["white"]};
        border: 1px solid {THEME["line"]};
        border-radius: 8px;
        padding: 16px 18px;
        box-shadow: 0 10px 28px rgba(16,42,67,.06);
        min-height: 105px;
        position: relative;
        overflow: hidden;
    }}
    .kpi-card::before {{
        content: "";
        position: absolute;
        inset: 0 auto 0 0;
        width: 4px;
        background: var(--accent);
    }}
    .kpi-label {{
        color: {THEME["muted"]};
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .04em;
        margin-bottom: 8px;
    }}
    .kpi-value {{
        color: {THEME["navy"]};
        font-size: 28px;
        line-height: 1;
        font-weight: 800;
        margin-bottom: 8px;
    }}
    .kpi-note {{
        color: {THEME["muted"]};
        font-size: 12px;
        line-height: 1.35;
    }}
    .insight-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin: 12px 0 22px 0;
    }}
    .insight-card {{
        background: {THEME["panel"]};
        border: 1px solid {THEME["line"]};
        border-radius: 8px;
        padding: 16px 18px;
    }}
    .insight-card b {{
        display: block;
        color: {THEME["navy"]};
        font-size: 14px;
        margin-bottom: 6px;
    }}
    .insight-card span {{
        color: {THEME["slate"]};
        font-size: 13px;
        line-height: 1.45;
    }}
    .dataframe {{
        font-family: Inter, Segoe UI, Arial, sans-serif;
        border-collapse: collapse;
    }}
    .dataframe th {{
        background: {THEME["navy"]};
        color: white;
        font-weight: 700;
        padding: 8px 10px;
    }}
    .dataframe td {{
        padding: 8px 10px;
        border-bottom: 1px solid {THEME["line"]};
    }}
    @media (max-width: 900px) {{
        .kpi-grid, .insight-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
    }}
</style>
"""))

def pct(numerator, denominator, digits=1):
    denominator = denominator if denominator not in [0, None] else np.nan
    value = numerator / denominator * 100
    return 0 if pd.isna(value) else round(value, digits)


def compact_number(value):
    if pd.isna(value):
        return "-"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value/1_000:.1f}K"
    return f"{value:,.0f}"


def metric_card(label, value, note="", accent=None):
    accent = accent or THEME["blue"]
    return f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-note">{note}</div>
    </div>
    """


def section_title(title, kicker=None):
    kicker_html = f"<span style='color:{THEME['muted']}; font-size:13px; font-weight:600; margin-left:8px'>{kicker}</span>" if kicker else ""
    display(HTML(f"<div class='section-divider'>{title}{kicker_html}</div>"))


def style_fig(fig, title=None, height=430, showlegend=True):
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else None,
            x=0,
            xanchor="left",
            font=dict(size=18, color=THEME["navy"], family="Inter, Segoe UI, Arial"),
        ),
        height=height,
        paper_bgcolor=THEME["white"],
        plot_bgcolor=THEME["white"],
        margin=dict(t=66 if title else 34, b=44, l=48, r=34),
        font=dict(family="Inter, Segoe UI, Arial", size=12, color=THEME["ink"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11, color=THEME["slate"]),
            bgcolor="rgba(255,255,255,0)",
        ),
        hoverlabel=dict(
            bgcolor=THEME["navy"],
            bordercolor=THEME["navy"],
            font=dict(color="white", family="Inter, Segoe UI, Arial", size=12),
        ),
        showlegend=showlegend,
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=THEME["line"],
        tickfont=dict(color=THEME["slate"]),
        title_font=dict(color=THEME["slate"]),
    )
    fig.update_yaxes(
        gridcolor=THEME["line"],
        zeroline=False,
        linecolor=THEME["line"],
        tickfont=dict(color=THEME["slate"]),
        title_font=dict(color=THEME["slate"]),
    )
    return fig


# ## 1. Load and Prepare Data
# 

# In[12]:
st.set_page_config(page_title="Cyber Square Performance Dashboard", layout="wide", initial_sidebar_state="collapsed")

REQUIRED_FILES = {
    "students": "students.csv",
    "admission": "admission.csv",
    "attendance": "attendance_current_month.csv",
    "placement": "placement.csv",
    "staff": "staff_dataset.csv",
    "schedule": "staff_schedule_with_weekly.csv",
    "courses": "course_dataset.csv",
    "classroom": "classroom.csv",
}

candidate_dirs = [Path.cwd(), Path.cwd() / "data", Path.cwd().parent / "data"]
DATA_DIR = next((p for p in candidate_dirs if all((p / f).exists() for f in REQUIRED_FILES.values())), None)
if DATA_DIR is None:
    raise FileNotFoundError("Could not find the required CSV files. Keep the notebook beside the CSVs or run it from the project root.")

students = pd.read_csv(DATA_DIR / REQUIRED_FILES["students"])
admission = pd.read_csv(DATA_DIR / REQUIRED_FILES["admission"])
attendance = pd.read_csv(DATA_DIR / REQUIRED_FILES["attendance"])
placement = pd.read_csv(DATA_DIR / REQUIRED_FILES["placement"])
staff = pd.read_csv(DATA_DIR / REQUIRED_FILES["staff"])
schedule = pd.read_csv(DATA_DIR / REQUIRED_FILES["schedule"])
courses = pd.read_csv(DATA_DIR / REQUIRED_FILES["courses"])
classroom = pd.read_csv(DATA_DIR / REQUIRED_FILES["classroom"])

# Type hygiene keeps visuals stable when CSV fields are read as text.
for df, cols in [
    (attendance, ["Attendance %", "Total Days", "Present", "Absent"]),
    (placement, ["package(Rs.L)"]),
    (staff, ["batches_handling", "hours_per_day"]),
    (courses, ["total_staff", "total_batches", "avg_hours"]),
    (classroom, ["Occupancy"]),
    (schedule, ["daily_hours", "weekly_hours"]),
]:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

for df, cols in [
    (students, ["enrollment_date"]),
    (admission, ["admission_date"]),
    (placement, ["offer_date"]),
]:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

slot_cols = [c for c in classroom.columns if ":" in c]
day_cols = [c for c in attendance.columns if "-Apr" in c]

def is_filled(value):
    text = str(value).strip()
    return text not in ["", "nan", "NaN", "None", "Free Period", "Free"]

display(HTML(f"""
<div class="executive-hero">
    <h1>Institute Performance Dashboard</h1>
    <p>Data source: {DATA_DIR} | {len(students):,} students | {len(admission):,} admission records | {len(placement):,} placement records</p>
</div>
"""))

source_summary = pd.DataFrame({
    "Dataset": ["Students", "Admissions", "Attendance", "Placement", "Staff", "Schedule", "Courses", "Classrooms"],
    "Rows": [len(students), len(admission), len(attendance), len(placement), len(staff), len(schedule), len(courses), len(classroom)],
    "Columns": [students.shape[1], admission.shape[1], attendance.shape[1], placement.shape[1], staff.shape[1], schedule.shape[1], courses.shape[1], classroom.shape[1]],
})


# ## A. Executive Summary
# 

# In[14]:

import streamlit as st
import pandas as pd

# ---------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------

placed_count = int((placement["status"] == "Placed").sum())

in_progress_count = int(
    (placement["status"] == "In Progress").sum()
)

not_placed_count = int(
    (placement["status"] == "Not Placed").sum()
)

admitted_count = int(
    (admission["status"] == "Admitted").sum()
)

# Percent helper
def pct(a, b, r=1):
    return round((a / b) * 100, r) if b else 0

# Metrics
admission_rate = pct(admitted_count, len(admission), 1)

placement_rate = pct(placed_count, len(placement), 1)

pipeline_rate = pct(in_progress_count, len(placement), 1)

avg_attendance = attendance["Attendance %"].mean()

low_attendance_count = int(
    (attendance["Attendance %"] < 75).sum()
)

placed_packages = placement.loc[
    placement["status"] == "Placed",
    "package(Rs.L)"
].dropna()

avg_package = placed_packages.mean()

low_attendance_count = int(
    (attendance["Attendance %"] < 75).sum()
)

# Classroom utilisation %
# ---------------------------------------------------
# CLASSROOM UTILISATION
# ---------------------------------------------------

TIME_SLOTS = [
    "10:00-12:00",
    "12:00-02:00",
    "02:30-04:30",
    "04:30-05:30"
]

# Count filled slots
def slot_filled(row):
    return sum(
        1
        for s in TIME_SLOTS
        if str(row.get(s, "")).strip()
        not in ["", "nan", "None"]
    )

# Add filled slot count
classroom["filled_slots"] = classroom.apply(
    slot_filled,
    axis=1
)

# Total occupied slots
occupied_slots = int(
    classroom["filled_slots"].sum()
)

# Total available slots
total_slots = int(
    len(classroom) * len(TIME_SLOTS)
)

# Classroom utilisation %
classroom_fill = round(
    (occupied_slots / total_slots) * 100,
    1
) if total_slots > 0 else 0

active_batches = int(
    courses["total_batches"].sum()
)

# ---------------------------------------------------
# DASHBOARD TITLE
# ---------------------------------------------------

st.title("🎓 Cyber Square Performance Dashboard")

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Students",
    f"{len(students):,}"
)

col2.metric(
    "Admission Rate",
    f"{admission_rate:.1f}%"
)

col3.metric(
    "Placement Rate",
    f"{placement_rate:.1f}%"
)

col4.metric(
    "Avg Attendance",
    f"{avg_attendance:.1f}%"
)

# ---------------------------------------------------

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "Avg Package",
    f"₹ {avg_package:.1f}L"
)

col6.metric(
    "Students at Risk",
    f"{low_attendance_count:,}"
)

col7.metric(
    "Classroom Fill",
    f"{classroom_fill:.0f}%"
)

col8.metric(
    "Active Batches",
    f"{active_batches:,}"
)

# ---------------------------------------------------
# INSIGHTS
# ---------------------------------------------------

st.markdown("---")

st.subheader("📌 Strategic Insights")

# Top Course
top_course = students["course"].value_counts().idxmax()

# Weakest Attendance Course
weakest_att_course = (
    attendance.groupby("course")["Attendance %"]
    .mean()
    .sort_values()
    .index[0]
)

# Top Location
top_location = (
    admission["location"]
    .value_counts()
    .idxmax()
)

# Best Counsellor
best_counsellor = (
    admission.assign(
        is_admitted=admission["status"]
        .eq("Admitted")
        .astype(int)
    )
    .groupby("attended_by")
    .agg(
        enquiries=("admission_id", "count"),
        admitted=("is_admitted", "sum")
    )
    .assign(
        conversion=lambda d:
        d["admitted"] / d["enquiries"] * 100
    )
    .sort_values(
        ["conversion", "enquiries"],
        ascending=False
    )
    .head(1)
)

# Insight Cards
st.info(
    f"📚 {top_course} is the largest enrolled course and acts as the flagship program."
)

st.warning(
    f"⚠️ {weakest_att_course} has the lowest average attendance and needs intervention."
)

st.success(
    f"📍 {top_location} is the strongest enquiry location for admissions."
)

st.success(
    f"🏆 {best_counsellor.index[0]} leads counsellor conversion at "
    f"{best_counsellor['conversion'].iloc[0]:.1f}%."
)

st.warning(
    f"🏫 Classroom utilisation is {classroom_fill:.0f}%."
)

st.info(
    f"💼 {pipeline_rate:.1f}% of placement records are still in progress."
)

# ## B. Admissions Funnel
# 

# In[15]:


section_title("B. Admissions Funnel", "Lead quality, counsellor productivity and location performance")

enrolled_ids = set(students["student_id"].dropna())
admitted_ids = set(admission.loc[admission["status"].eq("Admitted"), "student_id"].dropna())

funnel = pd.DataFrame({
    "Stage": ["Total Enquiries", "Admitted", "Enrolled Students", "Placement Records", "Placed Students"],
    "Count": [len(admission), admitted_count, len(enrolled_ids), len(placement), placed_count],
})
funnel["Conversion vs Previous"] = (funnel["Count"] / funnel["Count"].shift(1) * 100).fillna(100).round(1)

counsellor = (
    admission.assign(is_admitted=admission["status"].eq("Admitted").astype(int))
    .groupby("attended_by", as_index=False)
    .agg(Enquiries=("admission_id", "count"), Admitted=("is_admitted", "sum"))
)
counsellor["Conversion"] = (counsellor["Admitted"] / counsellor["Enquiries"] * 100).round(1)
counsellor = counsellor.sort_values("Conversion", ascending=True)

location = (
    admission.assign(is_admitted=admission["status"].eq("Admitted").astype(int))
    .groupby("location", as_index=False)
    .agg(Enquiries=("admission_id", "count"), Admitted=("is_admitted", "sum"))
)
location["Pending"] = location["Enquiries"] - location["Admitted"]
location["Conversion"] = (location["Admitted"] / location["Enquiries"] * 100).round(1)
location = location.sort_values("Enquiries", ascending=True)

fig = make_subplots(
    rows=2, cols=2,
    specs=[[{"type": "funnel", "rowspan": 2}, {"type": "xy"}], [None, {"type": "xy"}]],
    column_widths=[0.42, 0.58],
    row_heights=[0.50, 0.50],
    horizontal_spacing=0.16,
    vertical_spacing=0.24,
    subplot_titles=["Admissions to outcomes", "Counsellor conversion", "Location demand mix"],
)

fig.add_trace(go.Funnel(
    y=funnel["Stage"],
    x=funnel["Count"],
    textinfo="value+percent initial",
    marker=dict(color=[THEME["navy"], THEME["blue"], THEME["teal"], THEME["amber"], THEME["green"]]),
    connector=dict(line=dict(color=THEME["line"], width=1.4)),
    hovertemplate="<b>%{y}</b><br>Count: %{x:,}<extra></extra>",
    showlegend=False,
), row=1, col=1)

fig.add_trace(go.Bar(
    y=counsellor["attended_by"],
    x=counsellor["Enquiries"],
    orientation="h",
    name="Enquiries",
    marker_color="#E8EEF7",
    hovertemplate="<b>%{y}</b><br>Enquiries: %{x:,}<extra></extra>",
    showlegend=False,
), row=1, col=2)
fig.add_trace(go.Bar(
    y=counsellor["attended_by"],
    x=counsellor["Admitted"],
    orientation="h",
    name="Admitted",
    marker_color=THEME["blue"],
    text=counsellor["Conversion"].map(lambda x: f"{x:.0f}%"),
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Admitted: %{x:,}<br>Conversion: %{text}<extra></extra>",
    showlegend=False,
), row=1, col=2)

fig.add_trace(go.Bar(
    y=location["location"],
    x=location["Enquiries"],
    orientation="h",
    name="Total enquiries",
    marker_color="#E8EEF7",
    hovertemplate="<b>%{y}</b><br>Total enquiries: %{x:,}<extra></extra>",
    showlegend=False,
), row=2, col=2)
fig.add_trace(go.Bar(
    y=location["location"],
    x=location["Admitted"],
    orientation="h",
    name="Admitted",
    marker_color=THEME["teal"],
    text=location["Conversion"].map(lambda x: f"{x:.0f}%"),
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Admitted: %{x:,}<br>Conversion: %{text}<extra></extra>",
    showlegend=False,
), row=2, col=2)

fig.update_layout(barmode="overlay")
fig.update_annotations(font=dict(size=14, color=THEME["navy"], family="Inter, Segoe UI, Arial"))
fig.update_xaxes(title_text="Records", range=[0, counsellor["Enquiries"].max() * 1.28], row=1, col=2)
fig.update_xaxes(title_text="Enquiries", range=[0, location["Enquiries"].max() * 1.22], row=2, col=2)
fig.update_yaxes(automargin=True, row=1, col=1)
fig.update_yaxes(automargin=True, row=1, col=2)
fig.update_yaxes(automargin=True, row=2, col=2)
style_fig(fig, "Admissions Funnel and Conversion Drivers", height=720, showlegend=False)
st.plotly_chart(fig, use_container_width=True)


# ## C. Attendance and Risk Analysis
# 

# In[ ]:


section_title("C. Attendance and Risk Analysis", "Learner engagement, retention risk and course-level patterns")

risk_order = ["Critical (<60%)", "Watch (60-75%)", "Healthy (75-85%)", "Excellent (85%+)"]
attendance["Risk Band"] = pd.cut(
    attendance["Attendance %"],
    bins=[-0.1, 60, 75, 85, 100.1],
    labels=risk_order,
    right=False,
)
risk = attendance["Risk Band"].value_counts().reindex(risk_order).fillna(0).astype(int).reset_index()
risk.columns = ["Risk Band", "Students"]

course_att = (
    attendance.groupby("course", as_index=False)
    .agg(Avg_Attendance=("Attendance %", "mean"), Students=("student_id", "count"))
    .sort_values("Avg_Attendance")
)

active_day_cols = [col for col in day_cols if attendance[col].isin(["P", "A"]).any()]

heatmap_rows = []
for course_name, grp in attendance.groupby("course"):
    values = []
    for col in active_day_cols:
        valid = grp[col].isin(["P", "A"])
        rate = grp.loc[valid, col].eq("P").mean() * 100 if valid.any() else np.nan
        values.append(rate)
    heatmap_rows.append([course_name] + values)
daily_course = pd.DataFrame(heatmap_rows, columns=["course"] + active_day_cols).set_index("course")

fig_overview = make_subplots(
    rows=1, cols=2,
    column_widths=[0.38, 0.62],
    horizontal_spacing=0.18,
    subplot_titles=["Risk band distribution", "Average attendance by course"],
)

fig_overview.add_trace(go.Bar(
    y=risk["Risk Band"], x=risk["Students"],
    orientation="h",
    marker_color=[THEME["red"], THEME["amber"], THEME["teal"], THEME["green"]],
    text=risk["Students"], textposition="outside",
    hovertemplate="<b>%{y}</b><br>Students: %{x:,}<extra></extra>",
    showlegend=False,
), row=1, col=1)

fig_overview.add_trace(go.Bar(
    y=course_att["course"], x=course_att["Avg_Attendance"],
    orientation="h",
    marker_color=np.where(course_att["Avg_Attendance"] < 75, THEME["red"], THEME["blue"]),
    text=course_att["Avg_Attendance"].map(lambda x: f"{x:.1f}%"),
    textposition="outside",
    customdata=course_att[["Students"]],
    hovertemplate="<b>%{y}</b><br>Avg attendance: %{x:.1f}%<br>Students: %{customdata[0]:,}<extra></extra>",
    showlegend=False,
), row=1, col=2)
fig_overview.add_vline(x=75, line_dash="dot", line_color=THEME["red"], row=1, col=2)

fig_overview.update_xaxes(title_text="Students", row=1, col=1)
fig_overview.update_xaxes(range=[0, 105], title_text="Average attendance %", row=1, col=2)
fig_overview.update_yaxes(automargin=True, row=1, col=1)
fig_overview.update_yaxes(automargin=True, row=1, col=2)
style_fig(fig_overview, "Attendance Risk Overview", height=460, showlegend=False)
fig_overview.update_layout(margin=dict(t=76, b=46, l=150, r=42))
st.plotly_chart(fig_overview, use_container_width=True)


# ## D. Placement Performance
# 

# In[17]:


section_title("D. Placement Performance", "Placement rate, package quality and outcome concentration")

placement_course = (
    placement.assign(is_placed=placement["status"].eq("Placed").astype(int))
    .groupby("course", as_index=False)
    .agg(Candidates=("student_id", "count"), Placed=("is_placed", "sum"), Avg_Package=("package(Rs.L)", "mean"))
)
placement_course["Placement Rate"] = (placement_course["Placed"] / placement_course["Candidates"] * 100).round(1)
placement_course = placement_course.sort_values("Placement Rate")

placed = placement[placement["status"].eq("Placed")].copy()
placed_att = placed.merge(
    attendance[["student_id", "Attendance %"]],
    on="student_id",
    how="left",
).dropna(subset=["Attendance %", "package(Rs.L)"])

officer = (
    placement.dropna(subset=["placement_officer"])
    .assign(is_placed=placement["status"].eq("Placed").astype(int))
    .groupby("placement_officer", as_index=False)
    .agg(Handled=("student_id", "count"), Placed=("is_placed", "sum"), Avg_Package=("package(Rs.L)", "mean"))
)
officer["Placement Rate"] = (officer["Placed"] / officer["Handled"] * 100).round(1)
officer = officer.sort_values("Placement Rate")

fig = make_subplots(
    rows=2, cols=2,
    specs=[[{"type": "xy"}, {"type": "xy"}], [{"type": "xy"}, {"type": "xy"}]],
    subplot_titles=[
        "Placement rate by course",
        "Package distribution by course",
        "Attendance vs package",
        "Placement officer effectiveness",
    ],
    horizontal_spacing=0.12,
    vertical_spacing=0.18,
)

fig.add_trace(go.Bar(
    y=placement_course["course"], x=placement_course["Placement Rate"],
    orientation="h",
    marker_color=np.where(placement_course["Placement Rate"] >= placement_rate, THEME["green"], THEME["blue"]),
    text=placement_course["Placement Rate"].map(lambda x: f"{x:.1f}%"),
    textposition="outside",
    customdata=placement_course[["Candidates", "Placed"]],
    hovertemplate="<b>%{y}</b><br>Placement rate: %{x:.1f}%<br>Candidates: %{customdata[0]:,}<br>Placed: %{customdata[1]:,}<extra></extra>",
    showlegend=False,
), row=1, col=1)
fig.add_vline(x=placement_rate, line_dash="dot", line_color=THEME["navy"], row=1, col=1)

for course_name, sub in placed.dropna(subset=["package(Rs.L)"]).groupby("course"):
    fig.add_trace(go.Box(
        y=sub["package(Rs.L)"],
        name=course_name,
        boxpoints="outliers",
        marker_color=PALETTE[len(fig.data) % len(PALETTE)],
        hovertemplate=f"<b>{course_name}</b><br>Package: Rs. %{{y:.1f}}L<extra></extra>",
        showlegend=False,
    ), row=1, col=2)

fig.add_trace(go.Scatter(
    x=placed_att["Attendance %"],
    y=placed_att["package(Rs.L)"],
    mode="markers",
    marker=dict(size=10, color=THEME["blue"], opacity=0.78, line=dict(color="white", width=1)),
    text=placed_att["student_name"],
    customdata=placed_att[["course"]],
    hovertemplate="<b>%{text}</b><br>%{customdata[0]}<br>Attendance: %{x:.1f}%<br>Package: Rs. %{y:.1f}L<extra></extra>",
    name="Placed students",
    showlegend=False,
), row=2, col=1)

if len(placed_att) >= 2:
    slope, intercept = np.polyfit(placed_att["Attendance %"], placed_att["package(Rs.L)"], 1)
    x_line = np.linspace(placed_att["Attendance %"].min(), placed_att["Attendance %"].max(), 50)
    fig.add_trace(go.Scatter(
        x=x_line,
        y=slope * x_line + intercept,
        mode="lines",
        line=dict(color=THEME["red"], dash="dash"),
        name="Trend",
        hoverinfo="skip",
        showlegend=False,
    ), row=2, col=1)

fig.add_trace(go.Bar(
    y=officer["placement_officer"], x=officer["Placement Rate"],
    orientation="h",
    marker_color=THEME["teal"],
    text=officer["Placement Rate"].map(lambda x: f"{x:.0f}%"),
    textposition="outside",
    customdata=officer[["Handled", "Placed", "Avg_Package"]],
    hovertemplate="<b>%{y}</b><br>Placement rate: %{x:.1f}%<br>Handled: %{customdata[0]:,}<br>Placed: %{customdata[1]:,}<br>Avg package: Rs. %{customdata[2]:.1f}L<extra></extra>",
    showlegend=False,
), row=2, col=2)

fig.update_xaxes(title_text="Placement rate %", range=[0, 105], row=1, col=1)
fig.update_yaxes(title_text="Package (Rs. L)", row=1, col=2)
fig.update_xaxes(title_text="Attendance %", row=2, col=1)
fig.update_yaxes(title_text="Package (Rs. L)", row=2, col=1)
fig.update_xaxes(title_text="Placement rate %", range=[0, 105], row=2, col=2)
style_fig(fig, "Placement Performance Dashboard", height=760, showlegend=False)
st.plotly_chart(fig, use_container_width=True)


# ## E. Revenue / Business Metrics
# 

# In[18]:


section_title("E. Revenue / Business Metrics", "Demand, business mix and outcome-value proxies")

display(HTML(f"""
<div class="insight-card" style="margin-bottom:14px; background:white">
    <b>Revenue data note</b>
    <span>The current CSVs do not include course fee, discount, collection or invoice fields. This section therefore shows business metrics using admission demand, course mix, internship mix and placement package value as proxies. Add fee and payment data to convert this into true revenue analytics.</span>
</div>
"""))

course_business = (
    admission.assign(is_admitted=admission["status"].eq("Admitted").astype(int))
    .groupby("course", as_index=False)
    .agg(Enquiries=("admission_id", "count"), Admissions=("is_admitted", "sum"))
)
course_business["Conversion"] = (course_business["Admissions"] / course_business["Enquiries"] * 100).round(1)
enrolled_mix = students.groupby("course", as_index=False).agg(Enrolled=("student_id", "count"))
package_mix = placement[placement["status"].eq("Placed")].groupby("course", as_index=False).agg(
    Placed=("student_id", "count"),
    Package_Pool=("package(Rs.L)", "sum"),
    Avg_Package=("package(Rs.L)", "mean"),
)
course_business = (
    course_business.merge(enrolled_mix, on="course", how="left")
    .merge(package_mix, on="course", how="left")
    .fillna({"Enrolled": 0, "Placed": 0, "Package_Pool": 0, "Avg_Package": 0})
    .sort_values("Enquiries", ascending=False)
)

internship_mix = students["internship"].fillna("Not specified").value_counts().reset_index()
internship_mix.columns = ["Internship", "Students"]

mode_mix = admission.groupby(["mode", "status"]).size().reset_index(name="Records")

demand_view = course_business.sort_values("Enquiries", ascending=True)
package_view = course_business.sort_values("Package_Pool", ascending=True)

fig_business = make_subplots(
    rows=1, cols=2,
    column_widths=[0.52, 0.48],
    horizontal_spacing=0.20,
    subplot_titles=[
        "Course demand and admission conversion",
        "Placement package pool by course",
    ],
)

fig_business.add_trace(go.Bar(
    y=demand_view["course"],
    x=demand_view["Enquiries"],
    orientation="h",
    marker_color="#E8EEF7",
    name="Enquiries",
    hovertemplate="<b>%{y}</b><br>Enquiries: %{x:,}<extra></extra>",
    showlegend=False,
), row=1, col=1)
fig_business.add_trace(go.Bar(
    y=demand_view["course"],
    x=demand_view["Admissions"],
    orientation="h",
    marker_color=THEME["blue"],
    text=demand_view["Conversion"].map(lambda x: f"{x:.0f}%"),
    textposition="outside",
    name="Admissions",
    customdata=demand_view[["Enquiries", "Admissions"]],
    hovertemplate="<b>%{y}</b><br>Enquiries: %{customdata[0]:,}<br>Admissions: %{customdata[1]:,}<br>Conversion: %{text}<extra></extra>",
    showlegend=False,
), row=1, col=1)

fig_business.add_trace(go.Bar(
    y=package_view["course"],
    x=package_view["Package_Pool"],
    orientation="h",
    marker_color=THEME["green"],
    text=package_view["Package_Pool"].map(lambda x: f"Rs. {x:.1f}L"),
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Package pool: Rs. %{x:.1f}L<extra></extra>",
    showlegend=False,
), row=1, col=2)

fig_business.update_layout(barmode="overlay")
fig_business.update_annotations(font=dict(size=14, color=THEME["navy"], family="Inter, Segoe UI, Arial"))
fig_business.update_xaxes(title_text="Enquiries / admissions", range=[0, demand_view["Enquiries"].max() * 1.25], row=1, col=1)
fig_business.update_xaxes(title_text="Placement package pool (Rs. L)", range=[0, max(package_view["Package_Pool"].max() * 1.18, 1)], row=1, col=2)
fig_business.update_yaxes(automargin=True, row=1, col=1)
fig_business.update_yaxes(automargin=True, row=1, col=2)
style_fig(fig_business, "Business Metrics and Revenue-Readiness View", height=560, showlegend=False)
fig_business.update_layout(margin=dict(t=84, b=52, l=210, r=90))
st.plotly_chart(fig_business, use_container_width=True)
fig_mix = make_subplots(
    rows=1, cols=2,
    specs=[[{"type": "domain"}, {"type": "xy"}]],
    column_widths=[0.42, 0.58],
    horizontal_spacing=0.18,
    subplot_titles=["Internship mix", "Admission channel mix"],
)

fig_mix.add_trace(go.Pie(
    labels=internship_mix["Internship"],
    values=internship_mix["Students"],
    hole=0.62,
    marker=dict(colors=[THEME["blue"], THEME["teal"], THEME["amber"], THEME["slate"]]),
    textinfo="label+percent",
    textposition="outside",
    hovertemplate="<b>%{label}</b><br>Students: %{value:,}<br>Share: %{percent}<extra></extra>",
    showlegend=False,
), row=1, col=1)

status_colors = {"Admitted": THEME["green"], "Not Admitted": "#D7DEE8", "Pending": THEME["amber"]}
for status, sub in mode_mix.groupby("status"):
    fig_mix.add_trace(go.Bar(
        x=sub["mode"],
        y=sub["Records"],
        name=status,
        marker_color=status_colors.get(status, THEME["blue"]),
        text=sub["Records"],
        textposition="inside",
        hovertemplate="<b>%{x}</b><br>Status: " + status + "<br>Records: %{y:,}<extra></extra>",
    ), row=1, col=2)

fig_mix.update_layout(barmode="stack")
fig_mix.update_annotations(font=dict(size=14, color=THEME["navy"], family="Inter, Segoe UI, Arial"))
fig_mix.update_xaxes(title_text="Admission mode", row=1, col=2)
fig_mix.update_yaxes(title_text="Admission records", row=1, col=2)
style_fig(fig_mix, "Business Mix Diagnostics", height=440, showlegend=True)
fig_mix.update_layout(margin=dict(t=84, b=54, l=54, r=42), legend=dict(orientation="h", y=1.12, x=0.48, xanchor="left"))
st.plotly_chart(fig_mix, use_container_width=True)

course_business.rename(columns={
    "Package_Pool": "Placement Package Pool (Rs. L)",
    "Avg_Package": "Avg Package (Rs. L)",
}).round(1)


# ## F. Staff and Classroom Utilisation
# 
section_title(
    "F. Staff and Classroom Utilisation",
    "Capacity pressure, classroom fill and trainer workload"
)

# ---------------------------------------------------
# TEACHING STAFF ONLY
# ---------------------------------------------------

staff_load = staff[
    staff["department"].str.strip().str.lower() == "teaching"
].copy()

staff_load["Capacity %"] = (
    staff_load["batches_handling"] / 3 * 100
).clip(upper=140).round(0)

staff_load = staff_load.sort_values("Capacity %")

# ---------------------------------------------------
# SCHEDULE UTILISATION
# ---------------------------------------------------

schedule_cols = [
    c for c in schedule.columns
    if ":" in c
]

schedule_long = schedule.melt(
    id_vars=["staff_id", "name", "course"],
    value_vars=schedule_cols,
    var_name="Slot",
    value_name="Assignment",
)

schedule_long["Occupied"] = schedule_long[
    "Assignment"
].map(is_filled)

slot_util = schedule_long.groupby(
    "Slot",
    as_index=False
)["Occupied"].mean()

slot_util["Utilisation"] = (
    slot_util["Occupied"] * 100
).round(1)

# ---------------------------------------------------
# PLOTS
# ---------------------------------------------------

fig = make_subplots(
    rows=1,
    cols=2,
    specs=[[{"type": "xy"}, {"type": "xy"}]],
    column_widths=[0.6, 0.4],
    horizontal_spacing=0.12,
    subplot_titles=[
        "Teaching Staff Workload vs Capacity",
        "Trainer Schedule Utilisation"
    ],
)

# Background bars
fig.add_trace(
    go.Bar(
        y=staff_load["name"],
        x=[100] * len(staff_load),
        orientation="h",
        marker_color="#EEF2F6",
        hoverinfo="skip",
        showlegend=False,
    ),
    row=1,
    col=1
)

# Actual workload
fig.add_trace(
    go.Bar(
        y=staff_load["name"],
        x=staff_load["Capacity %"],
        orientation="h",
        marker_color=np.where(
            staff_load["Capacity %"] >= 100,
            THEME["red"],
            THEME["teal"]
        ),
        text=staff_load["batches_handling"].map(
            lambda x: f"{int(x)} batches"
        ),
        textposition="inside",
        customdata=staff_load[
            ["role", "course", "hours_per_day"]
        ],
        hovertemplate=
        "<b>%{y}</b><br>"
        "%{customdata[0]}<br>"
        "Course: %{customdata[1]}<br>"
        "Load: %{x:.0f}%<br>"
        "Hours/day: %{customdata[2]}"
        "<extra></extra>",
        showlegend=False,
    ),
    row=1,
    col=1
)

# Schedule utilisation
fig.add_trace(
    go.Bar(
        x=slot_util["Slot"].str.replace(
            ":00",
            "",
            regex=False
        ),
        y=slot_util["Utilisation"],
        marker_color=THEME["green"],
        text=slot_util["Utilisation"].map(
            lambda x: f"{x:.0f}%"
        ),
        textposition="outside",
        hovertemplate=
        "<b>%{x}</b><br>"
        "Trainer utilisation: %{y:.1f}%"
        "<extra></extra>",
        showlegend=False,
    ),
    row=1,
    col=2
)

# Axis updates
fig.update_xaxes(
    title_text="Capacity %",
    range=[0, 120],
    row=1,
    col=1
)

fig.update_yaxes(
    autorange="reversed",
    row=1,
    col=1
)

fig.update_yaxes(
    title_text="Utilisation %",
    range=[0, 110],
    row=1,
    col=2
)

style_fig(
    fig,
    "Teaching Staff Utilisation",
    height=570,
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ## G. Strategic Insights and Recommendations
# 

# In[24]:


section_title("G. Strategic Insights and Recommendations", "Priority actions for leadership")

course_health = (
    students.groupby("course", as_index=False).agg(Enrollment=("student_id", "count"))
    .merge(attendance.groupby("course", as_index=False).agg(Attendance=("Attendance %", "mean")), on="course", how="left")
    .merge(placement_course[["course", "Placement Rate"]], on="course", how="left")
    .merge(course_business[["course", "Conversion", "Enquiries"]], on="course", how="left")
).fillna(0)

course_health["Health Score"] = (
    course_health["Attendance"] * 0.35
    + course_health["Placement Rate"] * 0.35
    + course_health["Conversion"] * 0.20
    + (course_health["Enrollment"] / course_health["Enrollment"].max() * 100) * 0.10
).round(1)
course_health = course_health.sort_values("Health Score", ascending=False)

priority_course = course_health.sort_values("Health Score").iloc[0]
high_demand_low_conversion = course_business.sort_values(["Enquiries", "Conversion"], ascending=[False, True]).iloc[0]
overload_staff = staff_load.sort_values("Capacity %", ascending=False).head(1).iloc[0]

recommendations = pd.DataFrame([
    {
        "Priority": "1",
        "Theme": "Attendance recovery",
        "Action": f"Launch a retention sprint for {priority_course['course']} and all learners below 75% attendance.",
        "Business rationale": "Improves completion probability and protects placement outcomes.",
        "Owner": "Academic Lead",
    },
    {
        "Priority": "2",
        "Theme": "Admissions conversion",
        "Action": f"Review counselling scripts and objections for {high_demand_low_conversion['course']} where demand is high but conversion is weaker.",
        "Business rationale": "Captures more value from existing enquiry flow before increasing marketing spend.",
        "Owner": "Admissions Head",
    },
    {
        "Priority": "3",
        "Theme": "Placement pipeline",
        "Action": f"Convert the {in_progress_count} in-progress placement records through weekly employer follow-ups and interview readiness checkpoints.",
        "Business rationale": "Near-term placement wins will improve headline placement rate and board confidence.",
        "Owner": "Placement Lead",
    },
    {
        "Priority": "4",
        "Theme": "Capacity management",
        "Action": f"Rebalance trainer load for {overload_staff['name']} and protect buffer capacity because classroom fill is {classroom_fill:.0f}%.",
        "Business rationale": "Reduces service risk as utilisation approaches full capacity.",
        "Owner": "Operations Lead",
    },
    {
        "Priority": "5",
        "Theme": "Revenue instrumentation",
        "Action": "Add fee, discount, collection date, payment status and refund fields to the data model.",
        "Business rationale": "Enables true revenue, cohort profitability, collection efficiency and LTV analytics.",
        "Owner": "Finance / Data",
    },
])

card_html = "".join([
    f"<div class='insight-card'><b>{row['Priority']}. {row['Theme']}</b><span>{row['Action']}<br><br><b>Rationale:</b> {row['Business rationale']}</span></div>"
    for _, row in recommendations.iterrows()
])
display(HTML(f"<div class='insight-grid'>{card_html}</div>"))

fig = go.Figure(go.Bar(
    y=course_health.sort_values("Health Score")["course"],
    x=course_health.sort_values("Health Score")["Health Score"],
    orientation="h",
    marker_color=np.where(course_health.sort_values("Health Score")["Health Score"] < 55, THEME["red"], THEME["blue"]),
    text=course_health.sort_values("Health Score")["Health Score"].map(lambda x: f"{x:.1f}"),
    textposition="outside",
    customdata=course_health.sort_values("Health Score")[["Enrollment", "Attendance", "Placement Rate", "Conversion"]],
    hovertemplate="<b>%{y}</b><br>Health score: %{x:.1f}<br>Enrollment: %{customdata[0]:,}<br>Attendance: %{customdata[1]:.1f}%<br>Placement: %{customdata[2]:.1f}%<br>Admissions conversion: %{customdata[3]:.1f}%<extra></extra>",
))
fig.update_xaxes(range=[0, 105], title_text="Composite health score")
style_fig(fig, "Course Health Scorecard", height=520, showlegend=False) 


recommendations

