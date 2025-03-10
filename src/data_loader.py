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
    df = pd.read_parquet(LOG_FILE, engine="pyarrow")

    # Colonnes à conserver
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

    # Renommer les colonnes
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
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')

    # Supprimer les lignes où le timestamp est invalide
    df = df.dropna(subset=["timestamp"])

    # Convertir les ports en entier, supprimer les lignes où les ports sont manquants
    df["destination_port"] = pd.to_numeric(df["destination_port"], errors="coerce").fillna(0).astype(int)

    # Convertir la règle firewall en entier (999 pour cleanup)
    df["firewall_rule"] = pd.to_numeric(df["firewall_rule"], errors="coerce").fillna(999).astype(int)

   # Nettoyer et uniformiser la colonne "action"
    df["action"] = df["action"].str.upper().str.strip()  # Mettre en majuscules et supprimer les espaces
    df["action"] = df["action"].replace("", None)  # Remplacer les chaînes vides par NaN
    df = df.dropna(subset=["action"])  # Supprimer les lignes où "action" est vide ou invalide
    df = df[df["action"].isin(["PERMIT", "DENY"])]  # Conserver uniquement les valeurs valides


    # Remplir les valeurs manquantes ou vides dans les interfaces
    df["interface_in"] = df["interface_in"].replace("", "Unknown").fillna("Unknown")
    df["interface_out"] = df["interface_out"].replace("", "Unknown").fillna("Unknown")

    # Supprimer les lignes où les IPs source ou destination sont manquantes ou invalides
    df = df.dropna(subset=["source_ip", "destination_ip"])
    # Sauvegarder les données nettoyées
    df.to_parquet(CLEANED_FILE_PATH, index=False)
    print(f"✅ Données nettoyées enregistrées dans {CLEANED_FILE_PATH}")

if __name__ == "__main__":
    clean_and_save_logs()
