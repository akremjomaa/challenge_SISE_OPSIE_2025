# Projet Firewall Logs Analysis

Ce projet est une **application Streamlit** permettant d'analyser les logs du firewall. Il propose des **visualisations interactives**, des **analyses des flux autorisés/rejetés**, et des **statistiques détaillées** sur les connexions réseau.

---

## 🚀 Fonctionnalités Principales

✅ **Analyse des flux autorisés et rejetés** (TCP, UDP) avec filtrage des ports selon la **RFC 6056**\
✅ **Exploration interactive des logs** avec pagination et tri\
✅ **Visualisation des IPs sources suspectes** en fonction du nombre de connexions rejetées\
✅ **Heatmap des connexions** pour détecter les tendances horaires et identifier les IPs suspectes\
✅ **Classement des IPs et ports les plus actifs** (Top 5 IPs sources, Top 10 ports)

---

## 📂 Structure du Projet

```
📦 challenge_SISE_OPSIE_2025
├── 📂 src
│   ├── app.py                   # Point d'entrée Streamlit
│   ├── data_loader.py            # Chargement et nettoyage des logs
│   ├── 📂 visualization           # Scripts pour la visualisation des données
│   │   ├── data_table.py
│   │   ├── ip_analysis.py
│   │   ├── analyze_flux.py
│   │   ├── stats_summary.py
├── 📂 data
│   ├── log_export.parquet        # Fichier des logs (exemple)
├── Dockerfile                     # Fichier Docker pour conteneuriser l'application
├── requirements.txt                # Liste des dépendances Python
├── config.py                       # Configuration du projet
└── README.md                       # Documentation
```

---

## 🐳 **Installation et Exécution avec Docker**

### 🔹 **1️⃣ Construire l’image Docker**

```sh
docker build -t streamlit-app .
```

### 🔹 **2️⃣ Lancer le conteneur**

```sh
docker run -p 8501:8501 --name streamlit-container streamlit-app
```

📌 **Accéder à l'application** : Ouvre [http://localhost:8501](http://localhost:8501) dans ton navigateur.


🚀 **Bonnes analyses de logs !**

