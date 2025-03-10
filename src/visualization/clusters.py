# visualization/ip_analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pickle

# 📌 Charger les données et les mettre en cache
@st.cache_data
def load_data():
    """Charge et met en cache les logs Firewall depuis un fichier Parquet."""
    return pd.read_parquet("/Users/yac/Downloads/log_export.parquet", engine="pyarrow")

def show_clusters():
    # 📌 Charger les données
    df = load_data()
    st.title("Résultats du Clustering")
    # Selecting relevant features
    var_actives = ['portsrc', 'portdst', 'regle', 'divers']
    XVA = df[var_actives]

    # Handling missing values
    XVA = XVA.dropna().reset_index(drop=True)

    # Standardizing the data
    std = StandardScaler()
    ZVA = std.fit_transform(XVA)
    ZVA = pd.DataFrame(ZVA, index=XVA.index, columns=XVA.columns)

    # 🔥 User Chooses 2 or 3 Clusters
    k = st.slider("Choisissez le nombre de clusters (k)", min_value=2, max_value=4, value=3)

    if k == 2:
        with open("/Users/yac/Downloads/kmeans_num_k_2.pkl", "rb") as f:
            kmeans = pickle.load(f)
    elif k == 3:
        with open("/Users/yac/Downloads/kmeans_num_k_3.pkl", "rb") as f:
            kmeans = pickle.load(f)
    else:
        with open("/Users/yac/Downloads/kmeans_num_k_4.pkl", "rb") as f:
            kmeans = pickle.load(f)

    # Define sample size
    sample_size = 1000 
    # Randomly sample indices
    sample_indices = np.random.choice(XVA.index, size=min(sample_size, len(XVA)), replace=False)

    # 📊 Plotting Clusters
    for k, couleur in zip(np.unique(kmeans.labels_), ['red', 'green', 'blue', 'orange']):
        plt.scatter(XVA.loc[(kmeans.labels_ == k) & (XVA.index.isin(sample_indices)), 'regle'], 
                    XVA.loc[(kmeans.labels_ == k) & (XVA.index.isin(sample_indices)), 'portdst'], 
                    c=couleur, label=f"Cluster {k}", alpha=0.6)  # alpha for transparency


    # Add axis labels
    plt.ylabel("Port Destination")  
    plt.xlabel("Règle")  


    # Show the plot
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)  # Display the plot in Streamlit


if __name__ == "__main__":
    show_clusters()