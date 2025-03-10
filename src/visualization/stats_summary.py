# visualization/stats_summary.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from config import CLEANED_FILE_PATH, ALLOWED_IP_PREFIXES

def show_stats():
    st.write("### 📊 Statistiques des Flux")

    df = pd.read_parquet(CLEANED_FILE_PATH,engine="pyarrow")

    st.write("### 🚀 Top 5 des IPs Sources les Plus Émettrices")
    st.dataframe(df["source_ip"].value_counts().nlargest(5))

    st.write("### 🔥 Top 10 des Ports Inférieurs à 1024 les Plus Accédés")
    top_ports = df[df["destination_port"] <= 1024]["destination_port"].value_counts().nlargest(10)

    fig, ax = plt.subplots(figsize=(10,5))
    top_ports.plot(kind="bar", ax=ax, color="orange")
    plt.title("Top 10 des Ports ≤ 1024 les Plus Accédés")
    plt.xlabel("Port")
    plt.ylabel("Connexions")
    st.pyplot(fig)

    st.write("### 🔴 Accès des IPs Hors Plan d’Adressage")
    df_outside_university = df[~df["source_ip"].str.startswith(tuple(ALLOWED_IP_PREFIXES))]
    st.dataframe(df_outside_university)

if __name__ == "__main__":
    show_stats()
