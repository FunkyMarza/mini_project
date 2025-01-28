# Streamlit live coding script

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

# First some MPG Data Exploration
mpg_df_raw = load_data(path="./data/raw/mpg.csv")
mpg_df = deepcopy(mpg_df_raw)

# Add title and header
st.title("Introduction to Streamlit")
st.header("MPG Data Exploration")

#st.table(data=mpg_df)
if st.checkbox("Show Dataframe"):

    st.subheader("This is my dataset:")
    st.dataframe(data=mpg_df)
