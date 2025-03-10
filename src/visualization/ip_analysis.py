# visualization/ip_analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from config import CLEANED_FILE_PATH

# 📌 Charger les données et les mettre en cache
@st.cache_data
def load_data():
    """Charge et met en cache les logs Firewall depuis un fichier Parquet."""
    return pd.read_parquet(CLEANED_FILE_PATH, engine="pyarrow")

def show_ip_analysis():
    st.title("📡 Analyse Interactive des IP Sources")

    # 📌 Charger les données une seule fois grâce au cache
    df = load_data()

    # 📌 Vérification des colonnes
    required_columns = {"source_ip", "destination_ip", "action"}
    if not required_columns.issubset(df.columns):
        st.error("Les colonnes requises ne sont pas présentes dans le jeu de données.")
        return

    # 📌 Grouper par IP source et compter les occurrences des destinations contactées et le nombre de flux "DENY"
    df_grouped = df.groupby(["source_ip"]).agg(
        num_destinations=pd.NamedAgg(column="destination_ip", aggfunc="nunique"),
        num_deny=pd.NamedAgg(column="action", aggfunc=lambda x: (x == "DENY").sum())
    ).reset_index()

    # 📌 Trier les données par nombre d'IP destinations contactées
    df_grouped = df_grouped.sort_values(by="num_destinations", ascending=True).reset_index(drop=True)

    # 📌 Sélecteur interactif pour choisir une IP
    ip_selected = st.selectbox("📌 Sélectionnez une IP Source :", df_grouped["source_ip"])

    # 📌 Extraire les informations de l'IP sélectionnée
    selected_ip = df_grouped[df_grouped["source_ip"] == ip_selected].iloc[0]

    # 📌 Affichage des informations sélectionnées
    st.write(f"🔹 **Adresse IP Source** : {selected_ip['source_ip']}")
    st.write(f"📊 **Nombre d'IP destination contactées** : {selected_ip['num_destinations']}")
    st.write(f"🚫 **Nombre de flux rejetés (DENY)** : {selected_ip['num_deny']}")

    # 📌 Création du graphique interactif avec Plotly
    fig = px.scatter(
        df_grouped,
        x=df_grouped.index,
        y="num_destinations",
        color="num_deny",
        color_continuous_scale="reds",
        title="📡 IP Sources vs Nombre d'IP Destinations Contactées",
        labels={"num_destinations": "Nombre d’IP Destinations", "index": "Index des IP Sources"},
        hover_data=["source_ip", "num_deny"]
    )

    # 📌 Ajout d’une ligne verte pour l’IP sélectionnée
    selected_index = df_grouped[df_grouped["source_ip"] == ip_selected].index[0]
    fig.add_vline(x=selected_index, line_color="green")

    # 📌 Affichage du graphique interactif
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show_ip_analysis()
