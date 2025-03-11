import os
import sys
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit_option_menu import option_menu
from visualization.analyze_flux import show_flux_analysis
from visualization.data_table import show_data_table
from visualization.ip_analysis import show_ip_analysis
from visualization.stats_summary import show_stats

# Menu latéral
with st.sidebar:
    page = option_menu(
        menu_title="Navigation",
        options=["Tableau des Logs","Analyse des Flux", "Visualisation IPs", "Statistiques"],
        default_index=0,
        icons=["house","chart-line","dashboard","graph-up"]
    )



if page == "Analyse des Flux":
    show_flux_analysis()
elif page == "Tableau des Logs":
    show_data_table()
    pass
elif page == "Visualisation IPs":
    show_ip_analysis()
    pass
else:
    show_stats()