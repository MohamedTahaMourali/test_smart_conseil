import argparse
import time
import pymongo
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FacebookScraper:
    def __init__(self, username, password, mongo_uri="mongodb://localhost:27017/", db_name="facebook_scraping",
                 collection_name="posts"):
        """
        Initialisation du scraper Facebook avec les informations d'identification et la connexion à MongoDB.
        """
        self.username = username
        self.password = password
        self.driver = self._init_driver()
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.collection = self.db[collection_name]

    def _init_driver(self):
        """
        Initialise le navigateur avec les options appropriées pour éviter les notifications.
        """
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=chrome_options)

    def login(self):
        """
        Effectue la connexion à Facebook avec l'email et le mot de passe fournis.
        """
        self.driver.get("http://www.facebook.com")

        email_input = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']"))
        )
        password_input = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']"))
        )

        email_input.clear()
        email_input.send_keys(self.username)

        password_input.clear()
        password_input.send_keys(self.password)

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    def search(self, query):
        """
        Effectue une recherche sur Facebook pour un terme donné.
        """
        search_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search Facebook']"))
        )
        search_input.clear()
        search_input.send_keys(query)
        search_input.send_keys(Keys.RETURN)

    def scroll_and_scrape(self, query, max_scrolls=10):
        """
        Récupère les posts en scrollant dans les résultats de recherche.
        """
        try:
            # Attendre l'apparition des résultats de recherche
            time.sleep(5)
            results_container = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='x193iq5w x1xwk8fm']"))
            )

            for _ in range(max_scrolls):  # Ajustez le nombre de scrolls
                posts = results_container.find_elements(By.CSS_SELECTOR, "div[data-ad-preview='message']")

                for post in posts:
                    self._scrape_post(post, query)

                # Scroller à l'intérieur du conteneur des résultats
                self._scroll_down(results_container)

            print(f"Les posts ont été sauvegardés dans la base de données MongoDB.")

        except Exception as e:
            print(f"Erreur : {e}")
            self.driver.save_screenshot("error_screenshot.png")  # Capture d'écran pour débogage

    def _scrape_post(self, post, query):
        """
        Extrait et sauvegarde le contenu du post dans la base de données MongoDB.
        """
        try:
            # Vérifier s'il y a un bouton "See more" pour afficher le texte complet
            self._expand_post(post)

            content = post.text.strip()
            if content:
                post_data = {
                    "content": content,
                    "query": query,
                    "timestamp": time.time()
                }
                self.collection.insert_one(post_data)

        except Exception as e:
            print(f"Erreur lors de l'extraction du post : {e}")

    def _expand_post(self, post):
        """
        Si un bouton 'See more' existe, l'actionner pour afficher le texte complet du post.
        """
        try:
            see_more_button = post.find_element(
                By.XPATH,
                ".//div[contains(@role, 'button') and contains(text(), 'See more')]"
            )
            self.driver.execute_script("arguments[0].click();", see_more_button)
            time.sleep(1)  # Pause pour charger le contenu
        except Exception:
            pass  # Si le bouton 'See more' n'est pas trouvé, continuer

    def _scroll_down(self, container):
        """
        Effectue un scroll vers le bas dans le conteneur des résultats de recherche.
        """
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", container)
        time.sleep(5)  # Pause pour charger les nouveaux résultats

    def close(self):
        """
        Ferme le navigateur.
        """
        self.driver.quit()


def main():
    # Argument parser pour récupérer les arguments utilisateur
    parser = argparse.ArgumentParser(description="Scraper les posts Facebook.")
    parser.add_argument("--username", required=True, help="Nom d'utilisateur Facebook")
    parser.add_argument("--password", required=True, help="Mot de passe Facebook")
    parser.add_argument("--query", required=True, help="Terme de recherche sur Facebook")

    args = parser.parse_args()

    # Créer une instance du scraper et exécuter l'extraction
    scraper = FacebookScraper(args.username, args.password)
    scraper.login()
    scraper.search(args.query)
    scraper.scroll_and_scrape(args.query)
    scraper.close()


if __name__ == "__main__":
    main()
