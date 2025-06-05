import requests
from bs4 import BeautifulSoup
import logging

class WebScraperAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_amazon(self, query):
        url = f'https://www.amazon.co.uk/s?k={query.replace(" ", "+")}'
        try:
            resp = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            items = soup.find_all('div', {'data-component-type': 's-search-result'})
            results = []
            for item in items[:3]:
                try:
                    title = item.find('h2').text.strip()
                    price_whole = item.find('span', {'class': 'a-price-whole'})
                    price_frac = item.find('span', {'class': 'a-price-fraction'})
                    price = f"${price_whole.text}{price_frac.text}" if price_whole and price_frac else "N/A"
                    link = 'https://www.amazon.com' + item.find('a', {'class': 'a-link-normal'})['href']
                    results.append({'site': 'Amazon', 'title': title, 'price': price, 'link': link})
                except:
                    continue
            return results
        except Exception as e:
            self.logger.error(f"Amazon scrape error: {e}")
            return []

    def scrape_ebay(self, query):
        url = f'https://www.ebay.com/sch/i.html?_nkw={query.replace(" ", "+")}'
        try:
            resp = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            items = soup.find_all('div', {'class': 's-item__info'})[1:4]
            results = []
            for item in items:
                try:
                    title = item.find('div', {'class': 's-item__title'}).text.strip()
                    price = item.find('span', {'class': 's-item__price'}).text.strip()
                    link = item.find('a', {'class': 's-item__link'})['href']
                    results.append({'site': 'eBay', 'title': title, 'price': price, 'link': link})
                except:
                    continue
            return results
        except Exception as e:
            self.logger.error(f"eBay scrape error: {e}")
            return []
