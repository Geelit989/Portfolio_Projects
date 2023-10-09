#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


import numpy as np
import pandas as pd
import sqlite3
import matplotlib as mpl
import matplotlib.pyplot as plt


# ## THIS IS THE START OF MY END TO END MLOPS RESEARCH PROJECT

# In[3]:


url_macbook = '/Users/macbookpro/Desktop/aws-docs/Portfolio_Projects/Aws_MLOPs/nba-data/seasons_total.pq'
url_imac = '/Users/duk3y2/Desktop/aws-e2e/Portfolio_Projects/Aws_MLOPs/nba-data/seasons_total.pq'
x = pd.read_parquet(url_imac)


# In[4]:


x


# In[5]:


x.shape


# In[6]:


x.describe().T


# In[7]:


# Loop through field goal percent column and set nan to 0
for i in range(len(x)):
    if pd.isna(x.loc[i,'FT%']):
        x.loc[i,'FT%'] = 0


# In[8]:


x.plot(x = 'FT%',
       y = 'FTA',
       kind='scatter',
       figsize = (9,9),
)
plt.show()
