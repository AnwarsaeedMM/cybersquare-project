#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as  pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from IPython.display import display, HTML
from pathlib import Path

# Project root
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"

# In[2]:
st.set_page_config(page_title="Course Dashboard", layout="wide")
st.title("📋 Course Dashboard")

dc=pd.read_csv(DATA_DIR / "course_dataset.csv")


# In[3]:


dc.duplicated().sum()


# In[4]:


dc.isnull().sum()


# In[14]:


dc.head()

# ----------------------------
# 🎛️ FILTERS
# ----------------------------

st.sidebar.header("🔍 Course Filters")

# Department Filter
department_filter = st.sidebar.multiselect(
    "Select Department",
    options=sorted(dc['department'].dropna().unique())
)

# Course Filter
course_filter = st.sidebar.multiselect(
    "Select Course",
    options=sorted(dc['course'].dropna().unique())
)

# Staff Range Filter
staff_filter = st.sidebar.slider(
    "Select Staff Range",
    int(dc['total_staff'].min()),
    int(dc['total_staff'].max()),
    (
        int(dc['total_staff'].min()),
        int(dc['total_staff'].max())
    )
)

# Batch Range Filter
batch_filter = st.sidebar.slider(
    "Select Batch Range",
    int(dc['total_batches'].min()),
    int(dc['total_batches'].max()),
    (
        int(dc['total_batches'].min()),
        int(dc['total_batches'].max())
    )
)

# ----------------------------
# APPLY FILTERS
# ----------------------------

filtered_dc = dc.copy()

# Department
if department_filter:
    filtered_dc = filtered_dc[
        filtered_dc['department'].isin(department_filter)
    ]

# Course
if course_filter:
    filtered_dc = filtered_dc[
        filtered_dc['course'].isin(course_filter)
    ]

# Staff Range
filtered_dc = filtered_dc[
    (filtered_dc['total_staff'] >= staff_filter[0]) &
    (filtered_dc['total_staff'] <= staff_filter[1])
]

# Batch Range
filtered_dc = filtered_dc[
    (filtered_dc['total_batches'] >= batch_filter[0]) &
    (filtered_dc['total_batches'] <= batch_filter[1])
]

# Final dataframe
dc = filtered_dc

# KPI

dc['load_index']      = dc['avg_hours'] * dc['total_batches']
dc['batch_per_staff'] = (dc['total_batches'] / dc['total_staff']).round(1)

# ── KPI values ──
total_courses = dc['course'].nunique()
total_staff   = dc['total_staff'].sum()
total_batches = dc['total_batches'].sum()
avg_hours     = round(dc['avg_hours'].mean(), 1)
top_course    = dc.loc[dc['total_batches'].idxmax(), 'course']

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
add_kpi(total_courses, "Total Courses", [0.00, 0.22])
add_kpi(total_batches, "Total Batches", [0.26, 0.48])
add_kpi(total_staff,   "Total Staff",   [0.52, 0.74])
add_kpi(avg_hours,     "Avg Teaching Hours", [0.78, 1.00], " h")

# ── Top Course (below KPIs) ──
fig.add_annotation(
    x=0.5, y=0.05,
    text=f"<b>Top Course:</b> {top_course}",
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


# In[6]:

st.subheader("📊 Batch Distribution by Course")
fig = px.bar(dc, x='course', y='total_batches',
             title='Total Batches Running per Course',
             color='total_batches',
             color_continuous_scale='Teal',
             text='total_batches')
fig.update_traces(textposition='outside')
fig.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig, use_container_width=True)


# In[7]:

st.subheader("📊 Teaching Hours by Course")
# ── Donut 1 — Batch share per course ─────────────────────────────────────
fig1 = px.pie(dc, names='course', values='total_batches',
              hole=0.5,
              title='Batch Share per Course — Which course runs most?',
              color_discrete_sequence=px.colors.qualitative.Set2)
fig1.update_traces(textinfo='label+percent', textposition='outside')
fig1.update_layout(showlegend=True)
st.plotly_chart(fig1, use_container_width=True)


# In[8]:
st.subheader("📊 Efficiency Ratio: Batches per Staff Member")

dc['batches_per_staff'] = (dc['total_batches'] / dc['total_staff']).round(1)

fig = px.bar(dc.sort_values('batches_per_staff', ascending=False),
             x='course', y='batches_per_staff',
             title='Batches Handled per Staff Member (Efficiency Ratio)',
             color='batches_per_staff',
             color_continuous_scale='RdYlGn_r',
             text='batches_per_staff')
fig.update_traces(textposition='outside')
fig.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig, use_container_width=True)

# In[9]:


st.subheader("📊 Average Teaching Hours per Course" )
fig6 = px.bar(dc.sort_values('avg_hours'), x='avg_hours', y='course',
              orientation='h',
              title='Avg Teaching Hours per Course',
              color='avg_hours', color_continuous_scale='Oranges',
              text='avg_hours')
fig6.update_traces(textposition='outside')
fig6.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig6, use_container_width=True)     

# In[10]:

st.subheader("📊 Batch Distribution by Department & Course")
fig = px.treemap(
    dc,
    path=['department', 'course'],
    values='total_batches',
    title='Treemap — Batch Distribution by Department & Course',
    color='avg_hours',
    color_continuous_scale='RdYlGn_r',
    hover_data=['total_staff', 'avg_hours']
)

fig.update_traces(textinfo='label+value+percent root')
fig.update_layout(margin=dict(t=50, l=10, r=10, b=10))
st.plotly_chart(fig, use_container_width=True   )


# ----------------------------
#5- 📋 RAW DATA
# ----------------------------
st.subheader("📋 Raw Data")

st.dataframe(dc, use_container_width=True)




