import logging
from typing import List, Dict
from core.utils import speak


class ComparisonEngine:
    def __init__(self, llm=None):  # LLM can be added later
        self.logger = logging.getLogger(__name__)

    def extract_features(self, products: List[Dict]) -> List[Dict]:
        """Enhanced feature extraction"""
        compared = []
        for product in products:
            features = {
                'name': product['title'],
                'price': product['price_num'],
                'site': product['site'],
                'features': self._identify_key_features(product['title'])
            }
            compared.append(features)
        return compared

    def _identify_key_features(self, title: str) -> List[str]:
        """Identify specs from product titles"""
        features = []
        if 'GB' in title:
            features.append(title.split('GB')[0] + 'GB')
        if 'inch' in title.lower():
            features.append(title.split('inch')[0].split()[-1] + 'inch')
        return features or ['General Product']

    def generate_comparison(self, products: List[Dict]) -> str:
        """Generate comparison matrix"""
        compared = self.extract_features(products)
        matrix = "🆚 Comparison Matrix:\n\n"
        matrix += "| Feature".ljust(20) + "".join([f"| {p['site']}".ljust(30) for p in compared]) + "\n"
        matrix += "-" * (20 + 30 * len(compared)) + "\n"

        # Price row
        matrix += "| Price".ljust(20)
        for p in compared:
            matrix += f"| {p['price']}".ljust(30)
        matrix += "\n"

        # Features rows
        max_features = max(len(p['features']) for p in compared)
        for i in range(max_features):
            matrix += f"| Feature {i + 1}".ljust(20)
            for p in compared:
                feature = p['features'][i] if i < len(p['features']) else "-"
                matrix += f"| {feature}".ljust(30)
            matrix += "\n"

        return matrix
