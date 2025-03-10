# Utiliser une image officielle de Python
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .  
COPY src/app /app  

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port 8501 (port par défaut de Streamlit)
EXPOSE 8501

# Lancer l'application Streamlit
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
