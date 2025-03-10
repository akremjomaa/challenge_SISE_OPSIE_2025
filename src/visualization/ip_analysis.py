# visualization/ip_analysis.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from config import CLEANED_FILE_PATH

# 📌 Charger les données et les mettre en cache
@st.cache_data
def load_data():
    """Charge et met en cache les logs Firewall depuis un fichier Parquet."""
    return pd.read_parquet(CLEANED_FILE_PATH, engine="pyarrow")

def preprocess_data(df):
    """Pré-traite les données pour accélérer le rendu et améliorer l'affichage du graphe."""
    
    # 📌 Calcul du nombre de destinations contactées par chaque IP source
    ip_dest_counts = df.groupby("source_ip")["destination_ip"].nunique().reset_index()
    ip_dest_counts.columns = ["source_ip", "nb_destinations"]

    # 📌 Calcul du nombre de flux autorisés (`PERMIT`) et rejetés (`DENY`)
    ip_action_counts = df.groupby(["source_ip", "action"]).size().unstack(fill_value=0).reset_index()

    # 📌 Fusion des deux datasets
    merged_df = pd.merge(ip_dest_counts, ip_action_counts, on="source_ip", how="left")

    # 📌 Gérer les valeurs manquantes
    merged_df["PERMIT"] = merged_df.get("PERMIT", 0)
    merged_df["DENY"] = merged_df.get("DENY", 0)

    # 🔄 **Transformation logarithmique pour éviter les valeurs écrasées**
    merged_df["nb_destinations_log"] = np.log1p(merged_df["nb_destinations"])  # Log-scaling de X

    return merged_df

def show_ip_analysis():
    st.title("📡 Analyse Interactive des IP Sources")

    # 📌 Charger les données pré-traitées
    df = load_data()
    merged_df = preprocess_data(df)

    # 📊 **Afficher un résumé des valeurs pour compréhension**
    st.write(f"📊 **Statistiques du dataset :**")
    st.write(merged_df[["nb_destinations", "PERMIT", "DENY"]].describe())

    # 📌 Sélecteur du nombre d'IPs à afficher
    top_n = st.slider("🔢 Sélectionner le nombre d'IP Sources à afficher :", 10, 500, 50)

    # 📌 Sous-échantillonnage des données pour améliorer la performance
    sampled_df = merged_df.head(top_n)

    # 📌 Sélecteur interactif pour une IP source spécifique
    selected_ip = st.selectbox("📌 Sélectionnez une IP source :", ["Toutes"] + list(sampled_df["source_ip"]))

    if selected_ip != "Toutes":
        sampled_df = sampled_df[sampled_df["source_ip"] == selected_ip]

    # 📌 Création du graphique (Nuage de points avec log-scaling)
    fig = go.Figure()

    # 🔴 Points pour les flux rejetés (`DENY`)
    fig.add_trace(go.Scatter(
        x=sampled_df["nb_destinations_log"],
        y=sampled_df["DENY"],
        mode="markers",
        marker=dict(color="red", size=5, opacity=0.6),
        name="Flux Rejetés (DENY)"
    ))

    # 🟢 Points pour les flux autorisés (`PERMIT`)
    fig.add_trace(go.Scatter(
        x=sampled_df["nb_destinations_log"],
        y=sampled_df["PERMIT"],
        mode="markers",
        marker=dict(color="blue", size=5, opacity=0.6),
        name="Flux Autorisés (PERMIT)"
    ))

    # 📌 Ajout d’une ligne verte pour marquer une IP sélectionnée
    if selected_ip != "Toutes":
        selected_x = sampled_df["nb_destinations_log"].values[0]
        fig.add_vline(x=selected_x, line_color="green")

    # 📌 Mise en page optimisée
    fig.update_layout(
        title="📡 IP Sources vs Nombre d'IP Destinations Contactées (Nuage de Points - Log Scale)",
        xaxis_title="Log(Nombre d’IP Destinations Contactées +1)",
        yaxis_title="Nombre de Flux",
        legend_title="Type de Flux",
        template="plotly_dark",
        hovermode="closest",
        xaxis_range=[0, sampled_df["nb_destinations_log"].max() + 0.5],  # 📏 Étendre l'axe X
    )

    # 📌 Affichage du graphique interactif
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show_ip_analysis()
