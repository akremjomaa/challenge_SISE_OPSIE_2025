# Utiliser une image officielle de Python
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY requirements.txt .
COPY config.py .

# Copier tous les fichiers du dossier "src"
COPY src/ /app/src/

# Copier les fichiers de données 
COPY data/ /app/data/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port 8501 (port par défaut de Streamlit)
EXPOSE 8501

# Définir le point d'entrée pour exécuter l'application
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
