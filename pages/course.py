#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as  pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from IPython.display import display, HTML


# In[2]:


dc=pd.read_csv("../data/course_dataset.csv")


# In[3]:


dc.duplicated().sum()


# In[4]:


dc.isnull().sum()


# In[14]:


dc.head()


# In[13]:


# ── Derived columns ──
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

# ── Layout ──
fig.update_layout(
    title_text="<b>Course Dashboard</b>",
    title_x=0.5,
    height=220,
    margin=dict(t=50, b=30, l=10, r=10),  # extra bottom space
    template="plotly_white"
)

fig.show()


# In[6]:


fig = px.bar(dc, x='course', y='total_batches',
             title='Total Batches Running per Course',
             color='total_batches',
             color_continuous_scale='Teal',
             text='total_batches')
fig.update_traces(textposition='outside')
fig.update_layout(xaxis_tickangle=-30)
fig.show()


# In[7]:


# ── Donut 1 — Batch share per course ─────────────────────────────────────
fig1 = px.pie(dc, names='course', values='total_batches',
              hole=0.5,
              title='Batch Share per Course — Which course runs most?',
              color_discrete_sequence=px.colors.qualitative.Set2)
fig1.update_traces(textinfo='label+percent', textposition='outside')
fig1.update_layout(showlegend=True)
fig1.show()


# In[8]:


dc['batches_per_staff'] = (dc['total_batches'] / dc['total_staff']).round(1)

fig = px.bar(dc.sort_values('batches_per_staff', ascending=False),
             x='course', y='batches_per_staff',
             title='Batches Handled per Staff Member (Efficiency Ratio)',
             color='batches_per_staff',
             color_continuous_scale='RdYlGn_r',
             text='batches_per_staff')
fig.update_traces(textposition='outside')
fig.update_layout(xaxis_tickangle=-30)
fig.show()


# In[9]:


fig6 = px.bar(dc.sort_values('avg_hours'), x='avg_hours', y='course',
              orientation='h',
              title='Avg Teaching Hours per Course',
              color='avg_hours', color_continuous_scale='Oranges',
              text='avg_hours')
fig6.update_traces(textposition='outside')
fig6.show()


# In[10]:


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
fig.show()


# In[ ]:




