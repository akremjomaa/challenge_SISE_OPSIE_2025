# Utiliser une image officielle de Python
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY config.py .  
COPY config.py /app/src/  
# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers
COPY src/ /app/src/
COPY data/ /app/data/

# Ajouter un utilisateur non-root pour la sécurité
RUN useradd -m appuser
USER appuser

# Exposer le port 8501 pour Streamlit
EXPOSE 8501

# Démarrer l'application
CMD ["streamlit", "run", "/app/src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
