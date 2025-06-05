import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict
from core.utils import speak


class NegotiationAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def find_discounts(self, product_name: str) -> List[Dict]:
        """Search for active coupons"""
        try:
            url = f"https://www.coupons.com/search/?query={product_name.replace(' ', '+')}"
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            coupons = []
            for coupon in soup.select('.coupon-item'):
                coupons.append({
                    'source': 'Coupons.com',
                    'code': coupon.select_one('.coupon-code').text.strip(),
                    'discount': coupon.select_one('.coupon-desc').text.strip()
                })
            return coupons[:3]
        except Exception as e:
            self.logger.error(f"Coupon search failed: {e}")
            return []

    def check_price_history(self, product_id: str) -> float:
        """Mock price history - integrate with your DB later"""
        return 0  # Implement with real data

    def get_negotiation_tips(self, product: Dict) -> str:
        """Generate negotiation strategies"""
        tips = []

        # Coupon strategy
        if coupons := self.find_discounts(product['title']):
            tips.append(f"💳 Apply coupon code '{coupons[0]['code']}' for {coupons[0]['discount']}")

        # Price match strategy
        if product['price_num'] > 100:  # Threshold for negotiation
            tips.append("💬 Ask for price match guarantee (show competitors)")

        return tips or ["No specific negotiation tips available"]
