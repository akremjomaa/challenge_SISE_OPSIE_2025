# 📌 visualization/analyze_flux.py

import streamlit as st
import pandas as pd
import plotly.express as px
import ipaddress  # Module pour manipuler les adresses IP
from config import CLEANED_FILE_PATH

# 🔹 Définition des plages de ports selon la RFC 6056
PORT_RANGES = {
    "Well-Known Ports (0-1023)": (0, 1023),
    "Registered Ports (1024-49151)": (1024, 49151),
    "Dynamic/Private Ports (49152-65535)": (49152, 65535)
}

# Cache du chargement des données pour éviter la relecture à chaque interaction
@st.cache_data
def load_data():
    """Charge et met en cache les logs Firewall depuis un fichier Parquet."""
    return pd.read_parquet(CLEANED_FILE_PATH, engine="pyarrow")

# Cache du filtrage pour optimiser les performances
@st.cache_data
def filter_by_port_range(df, port_range):
    """Filtre les logs par plage de ports définie dans RFC 6056."""
    min_port, max_port = PORT_RANGES[port_range]
    return df[(df["destination_port"] >= min_port) & (df["destination_port"] <= max_port)]

# Fonction pour détecter si une IP est interne ou externe
def classify_ip(ip):
    """Classifie une IP comme Interne ou Externe."""
    try:
        ip_obj = ipaddress.ip_address(ip)
        if (
            ip_obj.is_private  # Vérifie si l'IP est dans un réseau privé
            or ip_obj.is_loopback  # Vérifie si c'est une adresse de loopback (127.0.0.1)
        ):
            return "Interne"
        else:
            return "Externe"
    except ValueError:
        return "Inconnu"  # Gestion des erreurs si l'IP est mal formatée

def show_flux_analysis():
    st.title("📊 Analyse des Flux TCP/UDP")

    # Charger les données une seule fois grâce au cache
    df = load_data()

    # Sélection de la plage de ports à analyser
    selected_range = st.selectbox("📌 Sélectionnez une plage de ports :", list(PORT_RANGES.keys()))

    # Filtrer les données selon la plage de ports sélectionnée
    df_filtered = filter_by_port_range(df, selected_range)

    # Vérifier si des données sont disponibles après filtrage
    if df_filtered.empty:
        st.warning(f"Aucune connexion détectée pour la plage {selected_range}.")
        return

    # Vérifier si UDP est présent dans les logs filtrés
    if "UDP" not in df_filtered["protocol"].unique():
        st.info("ℹ️ Aucune donnée UDP trouvée dans cette sélection.")

    # Compter les flux TCP/UDP autorisés et rejetés
    protocol_action_counts = df_filtered.groupby(["protocol", "action"]).size().unstack(fill_value=0)

    # Réindexation explicite pour garantir que "PERMIT" et "DENY" sont bien présents
    for col in ["PERMIT", "DENY"]:
        if col not in protocol_action_counts.columns:
            protocol_action_counts[col] = 0  # Ajout d'une colonne manquante

    protocol_action_counts = protocol_action_counts[["PERMIT", "DENY"]]  # Assurer l'ordre correct

    # 🔹 Affichage graphique des flux `PERMIT` vs `DENY`
    fig = px.bar(
        protocol_action_counts,
        x=protocol_action_counts.index,
        y=["PERMIT", "DENY"],
        title=f"Flux Autorisés vs Rejetés ({selected_range})",
        labels={"value": "Nombre de Connexions", "index": "Protocole"},
        barmode="stack",
        color_discrete_map={"PERMIT": "green", "DENY": "red"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Analyser l'origine des connexions `DENY` (Interne vs Externe)
    st.write("### 🔍 Origine des Connexions `DENY` (Interne vs Externe)")

    # Filtrer uniquement les connexions `DENY`
    df_deny = df_filtered[df_filtered["action"] == "DENY"].copy()

    if df_deny.empty:
        st.info("✔ Aucun flux rejeté (DENY) dans cette plage de ports.")
    else:
        # Classifier les IPs sources
        df_deny["ip_type"] = df_deny["source_ip"].apply(classify_ip)

        # Compter les connexions `DENY` internes vs externes
        deny_counts = df_deny["ip_type"].value_counts().reset_index()
        deny_counts.columns = ["Type d'IP", "Nombre de Connexions `DENY`"]

        # Affichage en camembert des connexions rejetées
        fig_deny = px.pie(
            deny_counts,
            names="Type d'IP",
            values="Nombre de Connexions `DENY`",
            title=f"Répartition des Connexions `DENY` ({selected_range})",
            color="Type d'IP",
            color_discrete_map={"Interne": "blue", "Externe": "red", "Inconnu": "gray"}
        )
        st.plotly_chart(fig_deny, use_container_width=True)

    # **Nouvelle section : Heatmap des Connexions par Heure et IP Source**
    st.write("### Heatmap des Connexions par Heure et IP Source")

    # Extraction de l'heure depuis le timestamp
    df_filtered["hour"] = df_filtered["timestamp"].dt.hour

    # Limiter aux `Top 10` IPs les plus actives pour éviter une heatmap illisible
    top_ips = df_filtered["source_ip"].value_counts().nlargest(10).index
    df_heatmap = df_filtered[df_filtered["source_ip"].isin(top_ips)]

    # Grouper les connexions par IP source et heure
    heatmap_data = df_heatmap.groupby(["hour", "source_ip"]).size().reset_index(name="Nombre de Connexions")

    # Affichage de la Heatmap avec `Plotly`
    fig_heatmap = px.density_heatmap(
        heatmap_data,
        x="hour",
        y="source_ip",
        z="Nombre de Connexions",
        color_continuous_scale="reds",
        title="⏰ Heatmap des Connexions par Heure et IP Source",
        labels={"hour": "Heure (0-23)", "source_ip": "IP Source", "Nombre de Connexions": "Nombre de Flux"}
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

if __name__ == "__main__":
    show_flux_analysis()
