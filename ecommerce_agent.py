from agents.ecommerce_agent.product_capture_agent import ProductCaptureAgent
from agents.ecommerce_agent.web_search_agent import WebScraperAgent
from agents.ecommerce_agent.summary_agent import SummaryAgent
from core.utils import speak
import logging
import time

class EcommerceAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.product_agent = ProductCaptureAgent()
        self.scraper_agent = WebScraperAgent()
        self.summary_agent = SummaryAgent()

    def run(self):
        try:
            product_name = self.product_agent.get_product_name()
            if not product_name:
                return

            speak(f"Searching for {product_name}, please wait.")
            print(f"🔎 Searching for {product_name}, please wait...")

            results = []
            for scraper in [self.scraper_agent.scrape_amazon, self.scraper_agent.scrape_ebay]:
                try:
                    results.extend(scraper(product_name))
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Scraping error: {e}")

            if not results:
                speak(f"Sorry, no results found for {product_name}.")
                print(f"❌ No results found for {product_name}.")
                return

            compared_results = self.summary_agent.compare_prices(results)
            summary = self.summary_agent.generate_summary(product_name, compared_results)

            print("\n" + "=" * 60 + "\n")
            print(summary)

            if compared_results and compared_results[0]['price_num'] != float('inf'):
                speak(f"I found {len(compared_results)} results. Best deal is on {compared_results[0]['site']} for {compared_results[0]['price']}.")
            else:
                speak("Prices were not available for all items.")
        except Exception as e:
            self.logger.error(f"Agent run error: {e}")
            speak("Sorry, I encountered an error.")

    def terminate(self):
        self.logger.info("EcommerceAgent terminated")
        speak("Ecommerce agent is now terminating.")
        print("👋 Ecommerce agent is now terminating.")


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO)

    agent = EcommerceAgent()
    try:
        while True:
            agent.run()
            repeat = input("\n🔁 Would you like to search for another product? (yes/no): ").strip().lower()
            if repeat not in ["yes", "y"]:
                break
    except KeyboardInterrupt:
        pass
    finally:
        agent.terminate()
