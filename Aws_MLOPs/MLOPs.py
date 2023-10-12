#!/usr/bin/env python
# coding: utf-8

# In[2]:


# Check if running in a Jupyter notebook
try:
    get_ipython
    IN_JUPYTER = True
except NameError:
    IN_JUPYTER = False

# Use %pip in Jupyter, and pip in non-Jupyter (e.g., standalone script)
if IN_JUPYTER:
    get_ipython().run_line_magic('pip', 'install pandas')
    get_ipython().run_line_magic('pip', 'install matplotlib')
    get_ipython().run_line_magic('pip', 'install pyarrow')
    get_ipython().run_line_magic('pip', 'install fastparquet')
else:
    import subprocess
    subprocess.call(['pip', 'install', 'pandas'])
    subprocess.call(['pip', 'install', 'matplotlib'])
    subprocess.call(['pip', 'install', 'pyarrow'])
    subprocess.call(['pip', 'install', 'fastparquet'])


# In[23]:


import numpy as np
import pandas as pd
import sqlite3
import matplotlib as mpl
import matplotlib.pyplot as plt


# ## THIS IS THE START OF MY END TO END MLOPS RESEARCH PROJECT

# In[13]:


# Change url variable depending on location
url_macbook = '/Users/macbookpro/Desktop/aws-docs/Portfolio_Projects/Aws_MLOPs/nba-data/seasons_total.pq'
url_imac = '/Users/duk3y2/Desktop/aws-e2e/Portfolio_Projects/Aws_MLOPs/nba-data/seasons_total.pq'
x = pd.read_parquet(url_imac)


# In[19]:


x


# In[6]:


x.shape


# In[18]:


x['year'] = pd.to_datetime(x['year'],format='%Y').dt.year


# In[ ]:





# In[20]:


x.info()


# In[21]:


x.describe().T


# In[9]:


# Loop through field goal percent column and set nan to 0
for i in range(len(x)):
    if pd.isna(x.loc[i,'FT%']):
        x.loc[i,'FT%'] = 0


# In[82]:


plt.style.use('seaborn-v0_8-colorblind')
fig,axes = plt.subplots(nrows=7,ncols=4,figsize=(30,30))

x_2023 = x[x['year']==2023]
x_2023 = x_2023.drop(['Rk','Player','year','team','team_retcon'],axis=1)

# Iterate through each column and create a histogram plot
for i, col in enumerate(x_2023.columns):
    row_index = i // 4  # Calculate the row index for the subplot
    col_index = i % 4   # Calculate the column index for the subplot
    ax = x_2023[col].plot(kind='hist', ax=axes[row_index, col_index],legend=True)
    ax.set_title(col)  # Set the column name as the title

# Remove any empty subplots
for i in range(x_2023.shape[1], 7 * 4):
    fig.delaxes(axes.flatten()[i])

# plt.tight_layout()
plt.show()

# x_2023.plot(
#     ax=axes,
#     subplots=True,
#     kind='hist',
# )
# ax.set_xlabel('Points')
# ax.set_title('Distribution of Points Scored in Year 2023')

