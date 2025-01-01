# Utiliser l'image Python officielle
FROM python:3.9-slim

# Installer les dépendances de Chrome et ChromeDriver
RUN apt-get update && \
    apt-get install -y \
    wget \
    curl \
    unzip \
    ca-certificates \
    libx11-6 \
    libx11-dev \
    libgdk-pixbuf2.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libnspr4 \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Télécharger et installer Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -y --fix-broken install && \
    rm google-chrome-stable_current_amd64.deb

# Télécharger et installer ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    rm chromedriver_linux64.zip

# Installer les dépendances Python nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source dans le conteneur
COPY . /app

# Définir le répertoire de travail
WORKDIR /app

# Définir le point d'entrée de l'application
CMD ["python", "scraper.py"]
