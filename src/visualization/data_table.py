# visualization/data_table.py

import streamlit as st
import pandas as pd
from config import CLEANED_FILE_PATH

# Charger les données et les mettre en cache
@st.cache_data
def load_data():
    """Charge les logs à partir du fichier Parquet et les met en cache."""
    return pd.read_parquet(CLEANED_FILE_PATH, engine="pyarrow")

def show_data_table():
    st.write("### 🔍 Les Logs Firewall")

    # Charger les données une seule fois (grâce au cache)
    df = load_data()

    # Afficher le nombre total d’individus dans le jeu de données
    st.write(f"📊 **Nombre total d’enregistrements : {len(df)}**")

    # Liste déroulante dynamique pour sélectionner une IP source
    ip_selected = st.selectbox("📌 Sélectionner une IP source :", ["Toutes"] + sorted(df["source_ip"].unique()))

    # Filtrer les logs si une IP est sélectionnée
    df_filtered = df[df["source_ip"] == ip_selected] if ip_selected != "Toutes" else df

    # Définir la pagination
    page_size = 1000  # Nombre de lignes par page

    # Stocker la page actuelle avec `st.session_state`
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    # Calcul du nombre total de pages
    total_pages = max((len(df_filtered) // page_size), 1)
    current_page = st.session_state.page_number

    # Sélectionner la plage de lignes à afficher
    start_row = (current_page - 1) * page_size
    end_row = start_row + page_size
    df_display = df_filtered.iloc[start_row:end_row]

    # Afficher le nombre d'enregistrements après filtrage
    st.write(f"📊 Page **{current_page}**/{total_pages} - Nombre d'enregistrements affichés : **{df_display.shape[0]}**")

    # Afficher un extrait des données
    st.data_editor(df_display, height=400, num_rows="dynamic", use_container_width=True)

    # Ajout des boutons de pagination en bas à gauche
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_page > 1:
            if st.button("⬅ Précédent"):
                st.session_state.page_number -= 1
                st.rerun()

    with col3:
        if current_page < total_pages:
            if st.button("Suivant ➡"):
                st.session_state.page_number += 1
                st.rerun()

if __name__ == "__main__":
    show_data_table()
