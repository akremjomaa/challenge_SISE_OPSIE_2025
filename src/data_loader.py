# # src/data_loader.py

# import os
# import pandas as pd
# from config import LOG_FILE, CLEANED_FILE_PATH

# # Vérifier si le fichier brut existe
# if not os.path.exists(LOG_FILE):
#     raise FileNotFoundError(f"Le fichier brut {LOG_FILE} est introuvable ! Vérifie son emplacement.")

# def clean_and_save_logs():
#     """Charge, nettoie et sauvegarde les logs au format structuré."""

#     # Charger le fichier brut
#     df = pd.read_csv(LOG_FILE, encoding="utf-8")

#     # Renommer les colonnes pour correspondre aux attentes
#     df.columns = [
#         "source_ip", "destination_ip", "destination_port", "protocol", "action", "date", "rule_id"
#     ]

#     # Convertir la colonne "date" en datetime
#     df["date"] = pd.to_datetime(df["date"])
#     # Ajouter des colonnes manquantes avec des valeurs par défaut
#     df["interface_in"] = "Unknown"  # Interface d’entrée inconnue
#     df["interface_out"] = "Unknown"  # Interface de sortie inconnue

#     # Vérification des types de données après transformation
#     print(df.info())

#     # Sauvegarder les données nettoyées
#     df.to_csv(CLEANED_FILE_PATH, index=False)
#     print(f"✅ Données nettoyées enregistrées dans {CLEANED_FILE_PATH}")

# if __name__ == "__main__":
#     clean_and_save_logs()


#src/data_loader.py

import os
import pandas as pd
from config import LOG_FILE, CLEANED_FILE_PATH

# Vérifier si le fichier brut existe
if not os.path.exists(LOG_FILE):
    raise FileNotFoundError(f"Le fichier brut {LOG_FILE} est introuvable ! Vérifie son emplacement.")

def clean_and_save_logs():
    """Charge, nettoie et sauvegarde les logs au format structuré."""

    # Charger le fichier brut
    df = pd.read_parquet(LOG_FILE,engine="pyarrow")
    columns_to_keep = [
    "date",           # Date complète
    "ipsrc",          # Adresse IP Source
    "ipdst",          # Adresse IP Destination
    "proto",          # Protocole (TCP/UDP)
    "portdst",        # Port de destination
    "action",         # Permit / Deny
    "regle",          # ID de la règle firewall
    "interface_in",   # Interface d'entrée
    "Interface_out"   # Interface de sortie
]
    df = df[columns_to_keep].copy()

    df = df.rename(columns={
    "date": "timestamp",
    "ipsrc": "source_ip",
    "ipdst": "destination_ip",
    "proto": "protocol",
    "portdst": "destination_port",
    "action": "action",
    "regle": "firewall_rule",
    "interface_in": "interface_in",
    "Interface_out": "interface_out"
})

    # Convertir la colonne "timestamp" en format datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Convertir les ports en entier
    df["destination_port"] = df["destination_port"].fillna(0).astype(int)

    # Convertir la règle firewall en entier (999 pour cleanup)
    df["firewall_rule"] = df["firewall_rule"].fillna(999).astype(int)

    # Uniformiser les actions (Permit/Deny)
    df["action"] = df["action"].str.upper()

    # Remplir les valeurs manquantes dans les interfaces
    df["interface_out"] = df["interface_out"].fillna("Unknown")

    # Sauvegarder les données nettoyées
    df.to_parquet(CLEANED_FILE_PATH, index=False)
    print(f"✅ Données nettoyées enregistrées dans {CLEANED_FILE_PATH}")

if __name__ == "__main__":
    clean_and_save_logs()
