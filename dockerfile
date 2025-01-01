# Utiliser une image de base officielle de Python
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet dans le conteneur
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port (optionnel, pour l'utilisation de l'API ou du serveur web si besoin)
EXPOSE 5000

# Commande par défaut pour exécuter le scraper
CMD ["python", "scraper.py"]
