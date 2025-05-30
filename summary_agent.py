import logging

class SummaryAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def compare_prices(self, data, min_price=30.0):
        filtered = []
        for item in data:
            try:
                price_str = item['price'].replace('$', '').replace(',', '').split()[0]
                if '-' in price_str:
                    price_str = price_str.split('-')[0]
                item['price_num'] = float(price_str)
                if item['price_num'] >= min_price:
                    filtered.append(item)
            except:
                item['price_num'] = float('inf')
                filtered.append(item)
        return sorted(filtered, key=lambda x: x['price_num'])

    def generate_summary(self, product_name, results):
        if not results:
            return f"Sorry, no results for {product_name}."
        summary = f"Here's what I found for '{product_name}':\n\n"
        for i, item in enumerate(results[:3], 1):
            summary += f"{i}. {item['site']}\n   Product: {item['title']}\n   Price: {item['price']}\n   Link: {item['link']}\n\n"
        summary += f"✨ Best deal: {results[0]['site']} for {results[0]['price']}."
        return summary
