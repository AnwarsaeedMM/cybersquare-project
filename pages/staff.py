#!/usr/bin/env python
# coding: utf-8

# # 📊 Cyber Square Institute - Staff Analysis
# 
# ## 🎯 Objective
# This project analyzes staff distribution, workload patterns, and course allocation to identify inefficiencies and provide actionable recommendations.
# 
# ## 📁 Dataset
# - File: `staff_dataset.csv`
# - Total Records: 17 staff members
# 
# ## 🔍 Key Focus Areas
# - Staff composition (Teaching vs Non-Teaching)
# - Workload distribution (hours & batches)
# - Course-wise dependency
# - Organizational efficiency

# ##  Setup & Data Loading

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

import warnings
warnings.filterwarnings('ignore')


# In[2]:


# Load dataset
df = pd.read_csv("../data/staff_dataset.csv")


# In[3]:


df.head()


# ## Data Overview

# In[4]:


df.shape


# In[5]:


df.info()


# In[6]:


df.describe()


# ## KPIs

# In[9]:


# ── Clean data ──
df.columns = df.columns.str.strip().str.lower()

# ── KPI calculations ──
total_staff      = len(df)
teaching_staff   = (df['department'] == 'Teaching').sum()
non_teaching     = total_staff - teaching_staff
avg_hours        = round(df['hours_per_day'].mean(), 1)

# ✅ Most loaded trainer (based on batches)
top_trainer = df.loc[df['hours_per_day'].idxmax(), 'name']
# ── Figure ──
fig = go.Figure()

# Helper
def add_kpi(value, title, x_pos, suffix=""):
    fig.add_trace(go.Indicator(
        mode="number",
        value=value,
        title={"text": f"<b>{title}</b>"},
        number={"font": {"size": 40}, "suffix": suffix},
        domain={'x': x_pos, 'y': [0, 1]}
    ))

# ── KPIs ──
add_kpi(total_staff,    "Total Staff",        [0.00, 0.22])
add_kpi(teaching_staff, "Teaching Staff",     [0.26, 0.48])
add_kpi(non_teaching,   "Non-Teaching Staff", [0.52, 0.74])
add_kpi(avg_hours,      "Avg Hours/Day",      [0.78, 1.00], " h")

# ── Add Most Loaded Trainer (below KPIs) ──
fig.add_annotation(
    x=0.5, y=0.05,
    text=f"<b>Most Loaded Trainer:</b> {top_trainer}",
    showarrow=False,
    xref="paper", yref="paper",
    font=dict(size=14),
    align="center"
)

# ── Layout ──
fig.update_layout(
    title_text="<b>Staff Overview Dashboard</b>",
    title_x=0.5,
    height=220,
    margin=dict(t=50, b=30, l=10, r=10),
    template="plotly_white"
)

fig.show()


# ## Staff Composition
# 
# Understanding how staff are distributed between Teaching and Non-Teaching roles.

# In[ ]:


total_staff = len(df)
teaching_df = df[df['department'] == 'Teaching']

teaching_count = len(teaching_df)
non_teaching_count = total_staff - teaching_count

print(f"Total Staff: {total_staff}")
print(f"Teaching Staff: {teaching_count}")
print(f"Non-Teaching Staff: {non_teaching_count}")
print(f"Teaching %: {teaching_count/total_staff*100:.1f}%")


# In[ ]:


fig = px.bar(
    df,
    x=df['department'].value_counts().index,
    y=df['department'].value_counts().values,
    color=df['department'].value_counts().index,
    title="Staff Distribution by Department",
    labels={'x': 'Department', 'y': 'Count'}
)
fig.show()


# ## ⏱️ Workload Analysis
# 
# We analyze working hours and batch allocation to detect imbalance.

# In[ ]:


print("Total Hours:", df['hours_per_day'].sum())
print("Average Hours (Teaching):", teaching_df['hours_per_day'].mean())
print("Max Hours:", teaching_df['hours_per_day'].max())
print("Min Hours:", teaching_df['hours_per_day'].min())


# In[ ]:


plt.figure(figsize=(7,4))
sns.histplot(df['hours_per_day'], kde=True)
plt.title("Distribution of Working Hours")
plt.xlabel("Hours per Day")
plt.show()


# ### 📊 Distribution of Working Hours ( Teaching )
# 
# Working hours range from **2 to 5 hours per day**, with an average of **~3.6 hours**.
# 
# - Most staff are concentrated between **3 to 4 hours**
# - A few staff are at the higher end (**5 hours**) → potential higher workload
# - Very few at the lower end (**2 hours**) → possible underutilization
# 
# ➡️ The distribution is slightly uneven, indicating that workload is not perfectly balanced across staff

# In[ ]:


df_sorted = df.sort_values(by='hours_per_day', ascending=False)

fig = px.bar(
    df_sorted,
    x='hours_per_day',
    y='name',
    color='department',
    orientation='h',
    title="Staff Workload Ranking (Hours per Day)"
)
fig.show()


# ### 📊 Staff Workload Ranking
# 
# Working hours show a clear variation across staff, ranging from **2 to 8 hours per day**.
# 
# - A few staff members (e.g., top entries) are working around **8 hours**, which is significantly above the overall average (~3.6 hours)
# - Most teaching staff fall within the **3 to 5 hours** range
# - Some staff are at **2–3 hours**, indicating lower workload levels
# 
# ➡️ The gap between lowest and highest workload is **6 hours**, which is substantial
# 
# ➡️ Non-teaching roles (like Finance, Admin, HR) appear among the highest hour values, suggesting they may have more fixed or full-day responsibilities
# 
# ➡️ Teaching staff show moderate variation, while non-teaching staff tend to appear at the higher end

# ##  Batch Handling Analysis

# In[ ]:


teaching_df = df[df['department'] == 'Teaching']


# In[ ]:


fig = px.bar(
    teaching_df.sort_values(by='batches_handling'),
    x='batches_handling',
    y='name',
    orientation='h',
    color='batches_handling',
    title="Batch Allocation per Trainer"
)
fig.show()


# ### 📦 Batch Handling Distribution
# 
# Teaching staff handle either **2 or 3 batches**, with a clear majority handling **3 batches**.
# 
# - Most trainers are assigned **3 batches**
# - A smaller group handles **2 batches**
# - No trainers exceed 3 batches
# 
# ➡️ Batch allocation is fairly standardized, with limited variation across staff
# 
# ➡️ Since most trainers handle similar batch counts, differences in workload (observed earlier) are likely due to **working hours rather than batch allocation**

# ## Course Analysis

# In[ ]:


course_counts = teaching_df['course'].value_counts().reset_index()
course_counts.columns = ['course', 'count']

fig = px.bar(
    course_counts,
    x='count',
    y='course',
    orientation='h',
    text='count',
    title="Number of Trainers per Course"
)

fig.update_traces(textposition='outside')
fig.show()


# ### 📚 Course-wise Staff Distribution
# 
# Out of 9 courses, **7 courses are handled by only 1 trainer**, while only **2 courses have 2 trainers each**.
# 
# - Courses with **2 trainers**:
#   - Python Full Stack Development
#   - Data Science with Python
# 
# - All other courses (UI/UX, Flutter, Business Analytics, Cyber Security, DevOps, MERN, React) have **only 1 trainer**
# 
# ➡️ This shows a strong imbalance in staff distribution across courses
# 
# ➡️ Majority of courses are **highly dependent on a single trainer**, creating operational risk
# 
# ➡️ Only a few core courses have backup support, indicating better resource planning in those areas

# In[ ]:


fig = px.scatter(
    teaching_df,
    x='batches_handling',
    y='hours_per_day',
    size='hours_per_day',
    color='hours_per_day',
    hover_data=['name'],
    title="Workload vs Batch Responsibility (Teaching Staff)"
)
fig.show()


# ### 🔗 Workload vs Batch Responsibility
# 
# Trainers handling **3 batches show a wider range of working hours (3 to 5 hrs)** compared to those handling 2 batches (2 to 4 hrs).
# 
# - Same batch count (3) → different workloads (3, 4, 5 hrs)
# - This shows workload is **not evenly distributed even within same batch level**
# - Trainers with **2 batches consistently stay on lower side (2–4 hrs)**
# 
# ➡️ Batch count alone does not determine workload
# 
# ➡️ Variations are likely caused by:
# - Course complexity differences
# - Uneven scheduling
# - Additional responsibilities assigned to certain trainers
# 
# ➡️ Indicates need for better workload standardization across trainers

# # 📊 Final Insights
# 
# ### 1. Staff Composition
# - Teaching staff make up **64.7% (11 out of 17)** of total staff
# - Non-teaching staff account for **35.3% (6 out of 17)**
# ➡️ The institute is primarily focused on academic delivery, with a strong teaching base
# 
# ---
# 
# ### 2. Workload Distribution
# - Working hours range from **2 to 8 hours per day**
# - Average workload is around **~3.6 hours**
# - Some staff operate at **high workload (5–8 hrs)** while others are at **2–3 hrs**
# ➡️ Indicates significant imbalance in workload distribution
# 
# ---
# 
# ### 3. Batch Handling
# - Trainers handle only **2 or 3 batches**
# - Majority handle **3 batches (8 trainers)** vs **2 batches (3 trainers)**
# ➡️ Batch allocation is fairly uniform and not a major source of imbalance
# 
# ---
# 
# ### 4. Workload vs Batch Relationship
# - Trainers with **3 batches show varied workload (3–5 hrs)**
# - Same batch count does not result in equal workload
# ➡️ Workload is influenced by additional factors beyond batch count
# 
# ---
# 
# ### 5. Course Distribution
# - Out of 9 courses:
#   - **7 courses have only 1 trainer**
#   - **2 courses have 2 trainers**
# ➡️ High dependency on individual trainers for most courses
# 
# ---
# 
# ### 6. Key Pattern
# ➡️ Workload imbalance is primarily driven by:
# - Uneven scheduling
# - Course complexity
# - Staff role differences
# 
# NOT by batch allocation

# ## ✅ Recommendations
# 
# ### 1. Balance Workload
# - Redistribute working hours to reduce gap between **2 hrs and 8 hrs**
# - Target a more consistent workload range (~3–5 hrs)
# 
# ---
# 
# ### 2. Optimize Scheduling
# - Standardize class scheduling across trainers
# - Avoid overloading specific individuals
# 
# ---
# 
# ### 3. Reduce Course Dependency
# - Assign **backup trainers** for courses with only 1 staff
# - Cross-train trainers across multiple courses
# 
# ---
# 
# ### 4. Monitor High Workload Staff
# - Identify staff consistently working **5+ hours**
# - Prevent burnout through redistribution
# 
# ---
# 
# ### 5. Improve Resource Planning
# - Allocate staff based on both **batch count and course complexity**
# - Not just number of batches
# 
# ---
# 
# ➡️ Implementing these changes can improve efficiency, reduce risk, and ensure better workload balance across the institute

# In[ ]:




