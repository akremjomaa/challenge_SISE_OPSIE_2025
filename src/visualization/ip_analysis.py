# visualization/ip_analysis.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from config import CLEANED_FILE_PATH

# Charger les données et les mettre en cache
@st.cache_data
def load_data():
    """Charge et met en cache les logs Firewall depuis un fichier Parquet."""
    return pd.read_parquet(CLEANED_FILE_PATH, engine="pyarrow")

def preprocess_data(df):
    """Pré-traite les données pour accélérer le rendu et améliorer l'affichage du graphe."""
    
    #  Supprimer les valeurs manquantes dans `destination_ip`
    df = df.dropna(subset=["destination_ip"])

    #  Calcul du nombre de destinations contactées par chaque IP source
    ip_dest_counts = df.groupby("source_ip")["destination_ip"].nunique().reset_index()
    ip_dest_counts.columns = ["source_ip", "nb_destinations"]

    # Calcul du nombre de flux autorisés (`PERMIT`) et rejetés (`DENY`)
    ip_action_counts = df.groupby(["source_ip", "action"]).size().unstack(fill_value=0).reset_index()

    # Fusion des deux datasets
    merged_df = pd.merge(ip_dest_counts, ip_action_counts, on="source_ip", how="left")

    # Gérer les valeurs manquantes
    merged_df["PERMIT"] = merged_df.get("PERMIT", 0)
    merged_df["DENY"] = merged_df.get("DENY", 0)

    merged_df["nb_destinations_log"] = np.log1p(merged_df["nb_destinations"])

    # Trier les IPs par activité
    merged_df = merged_df.sort_values(by=["PERMIT", "DENY"], ascending=False)

    return merged_df

def show_ip_analysis():
    st.title("Analyse Interactive des IP Sources")

    # Charger les données pré-traitées
    df = load_data()
    merged_df = preprocess_data(df)

    # Option pour voir uniquement les `DENY`
    show_only_deny = st.checkbox("🚨 Voir uniquement les IPs suspectes (`DENY` > 0)", value=False)
    if show_only_deny:
        merged_df = merged_df[merged_df["DENY"] > 0]

    # Sélecteur du nombre d'IPs à afficher
    top_n = st.slider("🔢 Sélectionner le nombre d'IP Sources à afficher :", 10, 500, 50)
    sampled_df = merged_df.head(top_n)

   # Création du graphique 
    fig = go.Figure()

    # Points pour les flux rejetés (`DENY`)
    fig.add_trace(go.Scatter(
        x=sampled_df["nb_destinations"], 
        y=np.log10(sampled_df["DENY"] + 1), 
        mode="markers",
        marker=dict(color="red", size=5, opacity=0.6),
        name="Flux Rejetés (DENY)"
    ))

    # Points pour les flux autorisés (`PERMIT`)
    fig.add_trace(go.Scatter(
        x=sampled_df["nb_destinations"],
        y=np.log10(sampled_df["PERMIT"] + 1),
        mode="markers",
        marker=dict(color="blue", size=5, opacity=0.6),
        name="Flux Autorisés (PERMIT)"
    ))

    # Ajout des titres et labels
    fig.update_layout(
        title="📡 IP Sources vs Nombre d'IP Destinations Contactées ",
        xaxis_title="Nombre d'IP Destinations Contactées ",
        yaxis_title="Log10(Nombre de Flux +1)",
        legend_title="Type de Flux",
        template="plotly_dark",
        hovermode="closest",
        xaxis=dict(tickformat=","),
        yaxis=dict(tickformat=".2f"),
    )

    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    show_ip_analysis()
