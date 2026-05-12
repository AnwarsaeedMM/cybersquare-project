#!/usr/bin/env python
# coding: utf-8

# # PROJECT EDA
# 

# In[1]:

from turtle import st

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots   
import warnings         
warnings.filterwarnings('ignore')
from pathlib import Path

# Project root
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"


st.set_page_config(page_title="Placement Dashboard", layout="wide")
st.title("📋 Placement Dashboard")
dt=pd.read_csv(DATA_DIR / "placement.csv")
dt.head(10)
# ----------------------------
# 🎛️ FILTERS
# ----------------------------

st.sidebar.header("🔍 Placement Filters")

# Course Filter
course_filter = st.sidebar.multiselect(
    "Select Course",
    sorted(dt['course'].dropna().unique())
)

# Status Filter
status_filter = st.sidebar.multiselect(
    "Select Status",
    sorted(dt['status'].dropna().unique())
)

# Company Filter
company_filter = st.sidebar.multiselect(
    "Select Company",
    sorted(dt['company'].dropna().unique())
)

# Package Range Filter
package_col = [c for c in dt.columns if 'package' in c.lower()][0]

min_pkg = float(dt[package_col].min())
max_pkg = float(dt[package_col].max())

package_filter = st.sidebar.slider(
    "Package Range (LPA)",
    min_value=min_pkg,
    max_value=max_pkg,
    value=(min_pkg, max_pkg)
)

# ----------------------------
# APPLY FILTERS
# ----------------------------

filtered_dt = dt.copy()

# Course
if course_filter:
    filtered_dt = filtered_dt[
        filtered_dt['course'].isin(course_filter)
    ]

# Status
if status_filter:
    filtered_dt = filtered_dt[
        filtered_dt['status'].isin(status_filter)
    ]

# Company
if company_filter:
    filtered_dt = filtered_dt[
        filtered_dt['company'].isin(company_filter)
    ]

# Package Range
filtered_dt = filtered_dt[
    (filtered_dt[package_col] >= package_filter[0]) &
    (filtered_dt[package_col] <= package_filter[1])
]

# Final filtered dataframe
dt = filtered_dt.copy()
# ### KPIs

# ── Clean columns ──
col = [c for c in dt.columns if 'package' in c.lower()][0]


dt['status'] = dt['status'].str.strip()

# ── Compute KPIs ──
total_students    = len(dt)
placed_count      = (dt['status'] == 'Placed').sum()
not_placed_count  = (dt['status'] == 'Not Placed').sum()
placement_rate    = round(placed_count / total_students * 100, 1) if total_students else 0
avg_package       = avg_package = round(pd.to_numeric(dt[col], errors='coerce').dropna().mean(),2)

# ✅ FIX: define top_company
top_company = dt.loc[dt['company'].notna(), 'company'].value_counts().idxmax()

# ── Figure ──
fig = go.Figure()

# Helper
def add_kpi(value, title, x_pos, suffix=""):
    fig.add_trace(go.Indicator(
        mode="number",
        value=value,
        title={"text": f"<b>{title}</b>"},
        number={
            "font": {"size": 40},
            "suffix": suffix
        },
        domain={'x': x_pos, 'y': [0, 1]}
    ))

# ── KPIs ──
add_kpi(total_students,   "Total Students",   [0.00, 0.22])
add_kpi(placement_rate,   "Placement Rate",   [0.26, 0.48], " %")
add_kpi(avg_package,      "Avg Package",      [0.52, 0.74], " L")
add_kpi(not_placed_count, "Not Placed",       [0.78, 1.00])

# ── Top Recruiter (clean position) ──
fig.add_annotation(
    x=0.5, y=0.05,   # ✅ FIXED POSITION
    text=f"<b>Top Recruiter:</b> {top_company}",
    showarrow=False,
    xref="paper", yref="paper",
    font=dict(size=14),
    align="center"
)

# --- Layout ---
fig.update_layout(
    height=250,
    margin=dict(t=50, b=10, l=10, r=10)
)

st.plotly_chart(fig, use_container_width=True)


# In[ ]:


avg_pkg = dt[dt['package(Rs.L)'].notna()].groupby('course')['package(Rs.L)'].mean().reset_index()
fig = px.area(avg_pkg, x='course', y='package(Rs.L)', title='Avg Package by Course (Area)', markers=True)
fig.update_layout(xaxis_tickangle=-40)
st.plotly_chart(fig, use_container_width=True)  


# In[ ]:


COLOR_MAP = {'Placed': '#1D9E75', 'Not Placed': '#D85A30', 'In Progress': '#EF9F27'}

fig = px.treemap(
    dt,
    path=[px.Constant('All'), 'course', 'status'],
    title='<b>Course → Placement Status Breakdown</b>',
    color='status',
    color_discrete_map=COLOR_MAP
)
fig.update_layout(
    title_font_size=18,
    margin=dict(t=50, l=10, r=10, b=10),
    paper_bgcolor='white'
)
fig.update_traces(textinfo="label+value+percent root")
st.plotly_chart(fig, use_container_width=True)  


# In[ ]:


# Course → Company → Role (only placed students)
df_chart1 = dt[dt['company'].notna() & dt['role'].notna()].copy()

fig1 = px.sunburst(
    df_chart1,
    path=['course', 'company', 'role'],
    title='<b>Course → Company → Role</b>',
    color='course',
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig1.update_traces(
    textinfo='label+percent parent',
    insidetextorientation='radial'
)
fig1.update_layout(
    title_font_size=18,
    paper_bgcolor='white',
    margin=dict(t=60, b=20, l=20, r=20),
    height=600
)
st.plotly_chart(fig1, use_container_width=True) 


# In[ ]:


avg_pkg = (
    dt[dt['package(Rs.L)'].notna()]
    .groupby('course')['package(Rs.L)']
    .agg(['mean', 'min', 'max', 'count'])
    .reset_index()
    .rename(columns={'mean': 'Avg Package', 'min': 'Min', 'max': 'Max', 'count': 'Students Placed'})
    .sort_values('Avg Package', ascending=False)
)

fig = px.bar(
    avg_pkg,
    x='course',
    y='Avg Package',
    text='Avg Package',
    color='Avg Package',
    color_continuous_scale='Teal',
    hover_data={'Min': True, 'Max': True, 'Students Placed': True},
    title='<b>Average Package by Course (Rs. Lakhs)</b>'
)
fig.update_traces(texttemplate='₹%{text:.1f}L', textposition='outside')
fig.update_layout(
    xaxis_tickangle=-40,
    title_font_size=18,
    coloraxis_showscale=True,
    paper_bgcolor='white',
    plot_bgcolor='#f8f9fa',
    yaxis_title='Avg Package (Rs. Lakhs)',
    margin=dict(t=50, b=100)
)
st.plotly_chart(fig, use_container_width=True)  

# In[ ]:


status_course = (
    dt.groupby(['course', 'status'])
    .size()
    .reset_index(name='Count')
)
total_course = dt.groupby('course').size().reset_index(name='Total')
status_course = status_course.merge(total_course, on='course')
status_course['Percentage'] = (status_course['Count'] / status_course['Total'] * 100).round(1)

fig = px.bar(
    status_course,
    x='course',
    y='Percentage',
    color='status',
    barmode='group',
    text='Percentage',
    color_discrete_map=COLOR_MAP,
    title='<b>Placement Rate by Course (%)</b>'
)
fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(
    xaxis_tickangle=-35,
    title_font_size=18,
    paper_bgcolor='white',
    plot_bgcolor='#f8f9fa',
    yaxis_title='Percentage of Students (%)',
    legend_title='Status',
    margin=dict(t=60, b=80)
)
st.plotly_chart(fig, use_container_width=True)


# In[ ]:


company_hiring = (
    dt[dt['company'].notna()]
    .groupby('company')
    .size()
    .reset_index(name='Hired Count')
    .sort_values('Hired Count', ascending=True)
)

fig = px.bar(
    company_hiring,
    x='Hired Count',
    y='company',
    orientation='h',
    text='Hired Count',
    color='Hired Count',
    color_continuous_scale='Blues',
    title='<b>Company-wise Hiring Count</b>'
)
fig.update_traces(textposition='outside')
fig.update_layout(
    title_font_size=18,
    coloraxis_showscale=False,
    paper_bgcolor='white',
    plot_bgcolor='#f8f9fa',
    xaxis_title='Number of Students Hired',
    margin=dict(t=60, r=60)
)
st.plotly_chart(fig, use_container_width=True)  


# In[ ]:


status_counts = dt['status'].value_counts().reset_index()
status_counts.columns = ['status', 'Count']

fig = go.Figure(go.Pie(
    labels=status_counts['status'],
    values=status_counts['Count'],
    hole=0.55,
    marker=dict(colors=[COLOR_MAP.get(s, '#999') for s in status_counts['status']]),
    textinfo='label+percent',
    textfont_size=13,
    pull=[0.05 if s == 'Placed' else 0 for s in status_counts['status']]
))

total = status_counts['Count'].sum()
fig.update_layout(
    title='<b>Overall Placement Outcome</b>',
    title_font_size=18,
    paper_bgcolor='white',
    annotations=[dict(text=f'<b>{total}<br>Students</b>', x=0.5, y=0.5,
                      font_size=16, showarrow=False)],
    legend=dict(orientation='h', y=-0.1),
    margin=dict(t=60, b=60)
)
st.plotly_chart(fig, use_container_width=True)  

# In[ ]:


company_pkg = (
    dt[dt['package(Rs.L)'].notna()]
    .groupby('company')
    .agg(
        Avg_Package=('package(Rs.L)', 'mean'),
        Total_Hired=('package(Rs.L)', 'count'),
        Max_Package=('package(Rs.L)', 'max')
    )
    .reset_index()
)

fig = px.scatter(
    company_pkg,
    x='Total_Hired',
    y='Avg_Package',
    text='company',
    size='Max_Package',
    color='Avg_Package',
    color_continuous_scale='RdYlGn',
    trendline='ols',           # shows if hiring more = paying more
    hover_data={'Max_Package': True, 'Total_Hired': True},
    title='<b>Do Companies That Hire More Pay Better? (Trend Line)</b>',
    size_max=35
)
fig.update_traces(textposition='top center', selector=dict(mode='markers+text'))
fig.update_layout(
    title_font_size=16,
    paper_bgcolor='white',
    plot_bgcolor='#f8f9fa',
    xaxis_title='Total Students Hired',
    yaxis_title='Avg Package (Rs. Lakhs)',
    coloraxis_showscale=False,
    margin=dict(t=70, b=40)
)
st.plotly_chart(fig, use_container_width=True)  

# In[ ]:

# ----------------------------
#5- 📋 RAW DATA
# ----------------------------
st.subheader("📋 Raw Data")

st.dataframe(dt, use_container_width=True)




