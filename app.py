import streamlit as st
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
        "🎓 Students",
        "📝 Admissions",
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
    "🏠 Overview": "Overview.py",
    "🎓 Students": "Students.py",
    "📝 Admissions": "Admissions.py",
    "📊 Attendance": "Attendance.py",
    "📚 Courses": "Courses.py",
    "👨‍🏫 Staff": "Staff.py",
    "🗓️ Scheduling": "Staff_Scheduling.py",
    "🏫 Classroom": "Classroom.py",
    "💼 Placement": "Placement.py",
}

# ---------------------------------------------------
# LOAD PAGE
# ---------------------------------------------------

page_path = Path("pages") / PAGES[page]

with open(page_path, encoding="utf-8") as f:
    exec(f.read())