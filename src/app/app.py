import os
import sys
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit_option_menu import option_menu

# Menu latéral
with st.sidebar:
    page = option_menu(
        menu_title="Navigation",
        options=["Accueil","Données","Dashboard","Statistiques"],
        default_index=0,
        icons=["house","chart-line","dashboard","graph-up"]
    )



# Chargement des pages
if page == "Accueil":
    st.title("Accueil")
    st.write("test_accueil")

elif page == "Données":
    st.title("Données")
    st.write("test_page1")

elif page == "Dashboard":
    st.title("Dashboard")
    st.write("test_page2")

elif page == "Statistiques":
    st.title("Statistiques")
    st.write("test_page3")
