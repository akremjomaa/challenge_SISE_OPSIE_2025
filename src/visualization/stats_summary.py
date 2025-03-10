# 📌 visualization/stats_summary.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import CLEANED_FILE_PATH, ALLOWED_IP_PREFIXES  # Définir ALLOWED_IP_PREFIXES dans config.py

# 📌 Charger les données et les mettre en cache pour améliorer les performances
@st.cache_data
def load_data():
    """Charge et met en cache les logs Firewall depuis un fichier Parquet."""
    return pd.read_parquet(CLEANED_FILE_PATH, engine="pyarrow")

# 📌 Fonction pour calculer les statistiques des flux
@st.cache_data
def compute_statistics(df):
    """Calcule les statistiques des flux."""

    # ✅ **Top 5 des IP Sources les Plus Émettrices**
    top_5_ips = df["source_ip"].value_counts().nlargest(5).reset_index()
    top_5_ips.columns = ["source_ip", "nb_flux"]

    # ✅ **Top 10 des Ports Inférieurs à 1024 les Plus Accédés**
    top_ports = df[df["destination_port"] <= 1024]["destination_port"].value_counts().nlargest(10).reset_index()
    top_ports.columns = ["destination_port", "nb_connexions"]

    # ✅ **Lister les Accès des IPs Hors Plan d’Adressage**
    df_outside_university = df[~df["source_ip"].astype(str).str.startswith(tuple(ALLOWED_IP_PREFIXES))]

    return top_5_ips, top_ports, df_outside_university

# 📌 Fonction principale pour afficher les statistiques
def show_stats():
    st.title("📊 Statistiques des Flux Firewall")

    # 📌 Charger les données avec cache
    df = load_data()

    # 📌 Calculer les statistiques avec cache
    top_5_ips, top_ports, df_outside_university = compute_statistics(df)

    # ✅ **Affichage du Top 5 des IPs Sources les Plus Émettrices sous forme de graphique**
    st.write("### 🚀 Top 5 des IPs Sources les Plus Émettrices")
    fig_ip, ax_ip = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_5_ips["source_ip"], y=top_5_ips["nb_flux"], palette="Blues_r", ax=ax_ip)
    ax_ip.set_title("Top 5 des IPs Sources les Plus Émettrices")
    ax_ip.set_xlabel("IP Source")
    ax_ip.set_ylabel("Nombre de Flux")
    ax_ip.set_xticklabels(ax_ip.get_xticklabels(), rotation=45, ha="right")
    st.pyplot(fig_ip)

    # ✅ **Affichage du Top 10 des Ports ≤ 1024 avec une échelle logarithmique**
    st.write("### 🔥 Top 10 des Ports Inférieurs à 1024 les Plus Accédés")
    fig_ports, ax_ports = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_ports["destination_port"].astype(str), y=top_ports["nb_connexions"], palette="Oranges", ax=ax_ports)
    ax_ports.set_yscale("log")  # ✅ Échelle logarithmique pour équilibrer les différences de connexions
    ax_ports.set_title("Top 10 des Ports ≤ 1024 les Plus Accédés")
    ax_ports.set_xlabel("Port")
    ax_ports.set_ylabel("Connexions (log)")
    ax_ports.set_xticklabels(ax_ports.get_xticklabels(), rotation=45, ha="right")
    st.pyplot(fig_ports)

    # ✅ **Affichage des statistiques des accès hors plan d’adressage**
    st.write("### 🔴 Accès des IPs Hors Plan d’Adressage")

    # 📌 Nombre total de logs et des logs hors plan
    total_logs = len(df)
    total_outside = len(df_outside_university)
    outside_ratio = (total_outside / total_logs) * 100

    # 📌 Affichage des statistiques sous forme de texte
    st.markdown(f"""
    📌 **Total des logs enregistrés :** {total_logs:,}  
    📌 **Total des accès hors plan :** {total_outside:,} (**{outside_ratio:.2f}%** du total)
    """)

    # 📌 Ajout d’une pagination pour afficher les logs hors plan (évite surcharge mémoire)
    page_size = 1000  # Nombre de lignes par page
    total_pages = (total_outside // page_size) + 1

    # 📌 Sélecteur de page
    selected_page = st.slider("📄 Page :", 1, total_pages, 1)

    # 📌 Affichage des données paginées
    start_idx = (selected_page - 1) * page_size
    end_idx = start_idx + page_size
    st.dataframe(df_outside_university.iloc[start_idx:end_idx])

    # 📌 Ajout d’un bouton pour télécharger le fichier complet
    csv_outside = df_outside_university.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger les accès hors plan", csv_outside, "acces_hors_plan.csv", "text/csv")

if __name__ == "__main__":
    show_stats()
