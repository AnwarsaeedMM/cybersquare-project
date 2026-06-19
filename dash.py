import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go   
from pathlib import Path

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Cyber Square Performance Dashboard",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.markdown("## 🎓 Cyber Square")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "📂 Select Dashboard",
    [
        "🏠 Overview",
        "📝 Admissions",
        "🎓 Students",
        "📊 Attendance",
        "📚 Courses",
        "👨‍🏫 Staff",
        "🗓️ Scheduling",
        "🏫 Classroom",
        "💼 Placement"
    ]
)

st.sidebar.markdown("---")

# ---------------------------------------------------
# PAGE FILE MAPPING
# ---------------------------------------------------
PAGES = {
    "🏠 Overview": "overview.py",
    "📝 Admissions": "admissions.py",
    "🎓 Students": "students.py",
    "📊 Attendance": "attendance.py",
    "📚 Courses": "courses.py",
    "👨‍🏫 Staff": "staff.py",
    "🗓️ Scheduling": "staff_scheduling.py",
    "🏫 Classroom": "classroom.py",
    "💼 Placement": "placement.py",
}
# ---------------------------------------------------
# LOAD PAGE
# ---------------------------------------------------

page_path = Path("pages") / PAGES[page]

import os
st.write("Trying:", page_path)

if not page_path.exists():
    st.error(f"File not found: {page_path}")
    st.stop()

with open(page_path, encoding="utf-8") as f:
    exec(f.read())