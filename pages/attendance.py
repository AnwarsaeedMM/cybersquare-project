#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ### Load dataset

# In[2]:


att=pd.read_csv("../data/attendance_current_month.csv")


# In[3]:


cls=pd.read_csv("../data/classroom.csv")


# In[4]:


att.head()


# In[5]:


cls.head()


# In[6]:


att.columns


# In[7]:


cls.columns


# In[8]:


att['Status'].unique()


# In[9]:


att['course'].unique()


# In[10]:


att.duplicated().sum()


# In[11]:


cls.duplicated().sum()


# In[12]:


att.isna().sum()


# In[13]:


cls.isna().sum()


# ## Visualisation

# ### KPI's

# In[14]:


# --- Data ---
status_counts = att['Status'].value_counts()

excellent = int(status_counts.get('Excellent', 0))
warning   = int(status_counts.get('Warning', 0))
critical  = int(status_counts.get('Critical', 0))

total_students = len(att)

# Example: overall attendance % (adjust if needed)
overall_attendance = round((excellent*1 + warning*0.7 + critical*0.4) / total_students * 100, 1)

# --- Create subplots ---
fig = go.Figure()

# Helper to create KPI
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

# Add KPIs
add_kpi(overall_attendance, "Overall Attendance %", [0.00, 0.22]," %")
add_kpi(excellent, "Excellent Students", [0.26, 0.48])
add_kpi(warning, "At Risk (Warning) Students", [0.52, 0.74])
add_kpi(critical, "Critical Students", [0.78, 1.00])

# Layout
fig.update_layout(
    title_text="<b>Attendance Dashboard</b>",
    title_x=0.5,
    height=200,
    margin=dict(t=50, b=10, l=10, r=10,
    )

)

fig.show()


# ### Attendence status

# In[15]:


status_colors= {
    'Excellent': '#2ECC71',
    'Regular':   '#3498DB',
    'Warning':   '#F39C12',
    'Critical':  '#E74C3C',
}


# In[16]:


status_counts = (att['Status']
                 .value_counts()
                 .reset_index()
                 .rename(columns={'count':'Count'}))


# In[17]:


status_counts 


# In[18]:


fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Count by Status', 'Percentage Split'],
    specs=[[{'type':'bar'}, {'type':'pie'}]]
)

# Bar
bar_fig = px.bar(
    status_counts,
    x='Status',
    y='Count',
    color_discrete_sequence=[['#2ECC71','#3498DB','#F39C12','#E74C3C']],
    text='Count'
)

bar_fig.update_traces(
    textposition='outside',
    showlegend=False
)

fig.add_trace(bar_fig.data[0], row=1, col=1)

# Pie
pie_fig = px.pie(
    status_counts,
    names='Status',
    values='Count',
    color='Status',
    color_discrete_map=status_colors,
    hole=0.5
)

pie_fig.update_traces(
    textinfo='label+percent',
    textposition='inside'
)

fig.add_trace(pie_fig.data[0], row=1, col=2)

# Layout
fig.update_layout(
    title='<b>Attendance Status Distribution</b>',
    height=473,
    showlegend=False,
    plot_bgcolor='#F8F9FA',
    paper_bgcolor='white'
)

fig.show()


# ### Course x Attendance

# In[19]:


course_status = (att.groupby(['course','Status'])
                 .size().reset_index(name='Count'))


# In[20]:


course_status


# In[21]:


fig = px.bar(
    course_status,
    x='course',
    y='Count',
    color='Status',
    barmode='group',
    color_discrete_map=status_colors,
    title='<b>Course × Attendance Status — Grouped Bar</b>',
    labels={'course': 'Course', 'Count': 'Students'},
    category_orders={'Status': ['Excellent','Regular','Warning','Critical']}
)

fig.update_layout(
    xaxis_tickangle=-30,
    height=470,
    title_font_size=18,
    plot_bgcolor='#F8F9FA',
    paper_bgcolor='white',
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)
fig.show()


# ### Daily attendence trend

# In[22]:


# Step 1: extract April columns
day_cols = [c for c in att.columns if '-Apr' in c]

# Step 2: calculate daily %
daily = {}
for d in day_cols:
    col = att[d].astype(str).str.strip().str.upper()
    working = col.isin(['P','A'])
    if working.sum() > 0:
        daily[d] = round((col == 'P').sum() / working.sum() * 100, 1)

# Step 3: create dataframe
daily_df = pd.DataFrame({
    'Day': list(daily.keys()),
    'Pct': list(daily.values())
})

# Step 4: sort
daily_df['DayNum'] = daily_df['Day'].str.replace('-Apr','').astype(int)
daily_df = daily_df.sort_values('DayNum')

# Step 5: mean
mean_pct = daily_df['Pct'].mean()


# In[23]:


# Line chart
fig = px.line(
    daily_df,
    x='DayNum',
    y='Pct',
    markers=True,
    title='<b>Daily Attendance Trend — April</b>'
)

# Color markers based on percentage
fig.update_traces(
    line=dict(color='#2980B9', width=2.5),
    marker=dict(
        size=8,
        color=daily_df['Pct'],
        colorscale='RdYlGn',
        cmin=60,
        cmax=100,
        showscale=True,
        colorbar_title='%'
    ),
    fill='tozeroy',
    fillcolor='rgba(52,152,219,0.12)',
)

# Add mean line (same as GO)
fig.add_hline(
    y=mean_pct,
    line_dash='dot',
    line_color='#E74C3C',
    annotation_text=f'Monthly Mean: {mean_pct:.1f}%',
    annotation_position='bottom right'
)

# Layout
fig.update_layout(
    xaxis_title='Day of April',
    yaxis_title='Attendance %',
    yaxis_range=[0, 110],
    height=430,
    plot_bgcolor='#F8F9FA',
    paper_bgcolor='white'
)

fig.show()


# In[24]:


batch_status = (att.groupby(['batch_id','Status'])
                .size().unstack(fill_value=0))
for col in ['Excellent','Regular','Warning','Critical']:
    if col not in batch_status.columns:
        batch_status[col] = 0
batch_status = batch_status[['Excellent','Regular','Warning','Critical']]


# In[25]:


batch_status


# In[26]:


fig = go.Figure(go.Heatmap(
    z=batch_status.values,
    x=batch_status.columns.tolist(),
    y=batch_status.index.tolist(),
    colorscale='RdYlGn',
    reversescale=True,
    text=batch_status.values,
    texttemplate='%{text}',
    textfont_size=12,
    colorbar_title='Students'
))

fig.update_layout(
    title_text='<b>Student Count — Batch × Attendance Status</b>',
    title_font_size=18,
    xaxis_title='Attendance Status',
    yaxis_title='Batch ID',
    height=520,
    paper_bgcolor='white'
)
fig.show()


# In[27]:


top_absent = att.sort_values(by='Absent', ascending=False).head(10)


# In[28]:


top_absent = top_absent.groupby(
    ['student_name', 'Status'], as_index=False
).agg({
    'Absent': 'sum',
    'course': 'first',
    'batch_id': 'first',
    'Attendance %': 'first',
    'Present': 'sum'
})


# In[29]:


top_absent = top_absent.sort_values(by='Absent', ascending=True)


# In[30]:


top_absent


# In[31]:


fig = px.bar(
    top_absent,
    y='student_name',
    x='Absent',
    orientation='h',
    color='Status',
    color_discrete_map=status_colors,
    text='Absent',
    hover_data={'course': True, 'batch_id': True,
                'Attendance %': True, 'Present': True},
    labels={'student_name': 'Student', 'Absent': 'Days Absent'},
    title='<b>Top 10 Most Absent Students</b>'
)

fig.update_traces(textposition='outside')
fig.update_layout(
    height=450,
    title_font_size=18,
    plot_bgcolor='#F8F9FA',
    paper_bgcolor='white',
    xaxis_range=[0, top_absent['Absent'].max() + 5]
)
fig.show()


# In[32]:


course_pa = (att.groupby('course')[['Present','Absent']]
             .mean()
             .round(1)
             .reset_index()
             .sort_values('Present', ascending=False))

fig = go.Figure()
fig.add_trace(go.Bar(
    name='Present',
    x=course_pa['course'],
    y=course_pa['Present'],
    marker_color='#2ECC71',
    hovertemplate='<b>%{x}</b><br>Avg Present: %{y} days<extra></extra>'
))
fig.add_trace(go.Bar(
    name='Absent',
    x=course_pa['course'],
    y=course_pa['Absent'],
    marker_color='#E74C3C',
    hovertemplate='<b>%{x}</b><br>Avg Absent: %{y} days<extra></extra>'
))

fig.update_layout(
    barmode='stack',
    title_text='<b>Average Present vs Absent Days by Course</b>',
    title_font_size=18,
    xaxis_tickangle=-30,
    yaxis_title='Average Days',
    height=470,
    plot_bgcolor='#F8F9FA',
    paper_bgcolor='white',
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)
fig.show()


# In[ ]:




