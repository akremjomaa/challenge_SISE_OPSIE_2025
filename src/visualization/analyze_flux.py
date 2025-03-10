# visualization/analyze_flux.py

import streamlit as st
import pandas as pd
import plotly.express as px
from config import CLEANED_FILE_PATH

# 🔹 Définition des plages de ports selon la RFC 6056
PORT_RANGES = {
    "Well-Known Ports (0-1023)": (0, 1023),
    "Registered Ports (1024-49151)": (1024, 49151),
    "Dynamic/Private Ports (49152-65535)": (49152, 65535)
}

# 📌 Cache du chargement des données pour éviter la relecture à chaque interaction
@st.cache_data
def load_data():
    """Charge et met en cache les logs Firewall depuis un fichier Parquet."""
    return pd.read_parquet(CLEANED_FILE_PATH, engine="pyarrow")

# 📌 Cache du filtrage pour optimiser les performances
@st.cache_data
def filter_by_port_range(df, port_range):
    """Filtre les logs par plage de ports définie dans RFC 6056."""
    min_port, max_port = PORT_RANGES[port_range]
    return df[(df["destination_port"] >= min_port) & (df["destination_port"] <= max_port)]

def show_flux_analysis():
    st.title("📊 Analyse des Flux TCP/UDP (Avec Filtrage RFC 6056)")

    # 📌 Charger les données une seule fois grâce au cache
    df = load_data()

    # 📌 Sélection de la plage de ports à analyser
    selected_range = st.selectbox("📌 Sélectionnez une plage de ports :", list(PORT_RANGES.keys()))

    # 📌 Filtrer les données selon la plage de ports sélectionnée (optimisé avec `st.cache_data`)
    df_filtered = filter_by_port_range(df, selected_range)

    # 📌 Vérifier si des données sont disponibles après filtrage
    if df_filtered.empty:
        st.warning(f"Aucune connexion détectée pour la plage {selected_range}.")
        return

    # 📌 Vérifier si UDP est présent dans les logs filtrés
    if "UDP" not in df_filtered["protocol"].unique():
        st.info("ℹ️ Aucune donnée UDP trouvée dans cette sélection.")

    # 📌 Compter les flux TCP/UDP autorisés et rejetés
    protocol_action_counts = df_filtered.groupby(["protocol", "action"]).size().unstack(fill_value=0)

    # ✅ Correction : Réindexation explicite pour s'assurer que PERMIT et DENY sont bien ordonnés
    for col in ["PERMIT", "DENY"]:
        if col not in protocol_action_counts.columns:
            protocol_action_counts[col] = 0  # Ajout d'une colonne manquante pour éviter les erreurs

    protocol_action_counts = protocol_action_counts[["PERMIT", "DENY"]]  # Assurer l'ordre correct

    # 🔹 Affichage avec `Plotly` pour améliorer l’interactivité
    fig = px.bar(
        protocol_action_counts,
        x=protocol_action_counts.index,
        y=["PERMIT", "DENY"],
        title=f"✅❌ Flux Autorisés vs Rejetés ({selected_range})",
        labels={"value": "Nombre de Connexions", "index": "Protocole"},
        barmode="stack",
        color_discrete_map={"PERMIT": "green", "DENY": "red"}
    )

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show_flux_analysis()
