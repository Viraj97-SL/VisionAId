
from agents.ecommerce_agent.product_capture_agent import ProductCaptureAgent
from agents.ecommerce_agent.web_search_agent import WebScraperAgent
from agents.ecommerce_agent.summary_agent import SummaryAgent
from agents.ecommerce_agent.comparison_engine import ComparisonEngine
from agents.ecommerce_agent.negotiation_agent import NegotiationAgent
from agents.ecommerce_agent.review_analyzer import ReviewAnalyzer
from core.utils import speak
import logging
import time
from typing import List, Dict
import speech_recognition as sr
import winsound


class EcommerceAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.product_agent = ProductCaptureAgent()
        self.scraper_agent = WebScraperAgent()
        self.summary_agent = SummaryAgent()
        self.comparison_engine = ComparisonEngine()
        self.negotiator = NegotiationAgent()
        self.review_analyzer = ReviewAnalyzer()

    def run(self):
        try:
            while True:  # Added main conversation loop here
                # Step 1: Product Identification
                product_name = self.product_agent.get_product_name()
                if not product_name:
                    if not self._ask_to_continue():
                        break
                    continue

                speak(f"Searching for {product_name}, please wait.")
                print(f"🔎 Searching for {product_name}, please wait...")

                # Step 2: Web Scraping
                results = self._scrape_multiple_sources(product_name)
                if not results:
                    speak(f"Sorry, no results found for {product_name}.")
                    print(f"❌ No results found for {product_name}.")
                    if not self._ask_to_continue():
                        break
                    continue

                # Step 3: Price Comparison
                compared_results = self.summary_agent.compare_prices(results)

                # Step 4: Get Reviews
                reviews = self._get_product_reviews(compared_results)

                # Step 5: Generate Enhanced Report
                summary = self._generate_comprehensive_report(product_name, compared_results, reviews)

                # Step 6: Present Results
                self._present_results(product_name, compared_results, summary)

                if not self._ask_to_continue():
                    break

        except Exception as e:
            self.logger.error(f"Agent run error: {e}")
            speak("Sorry, I encountered an error.")

    def _ask_to_continue(self) -> bool:
        """Voice-enabled continuation prompt with better reliability."""
        recognizer = sr.Recognizer()
        max_attempts = 3  # Limit retries before fallback

        for attempt in range(max_attempts):
            try:
                speak("Would you like to search for another product? Please say 'yes' or 'no'.")
                print("\n🔁 Listening for your response... (Say 'yes' or 'no')")

                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)  # Better noise handling
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)  # Shorter listening window

                response = recognizer.recognize_google(audio).lower()
                print(f"⏺️ You said: {response}")

                # Check for clear 'yes' or 'no' (with common variations)
                if any(word in response for word in ["no", "nope", "stop", "exit"]):
                    return False
                elif any(word in response for word in ["yes", "yeah", "yep", "continue"]):
                    return True
                else:
                    speak("Sorry, I didn't understand. Please say 'yes' or 'no' clearly.")

            except (sr.WaitTimeoutError, sr.UnknownValueError):
                speak("I didn't catch that. Please try again.")
            except Exception as e:
                self.logger.error(f"Voice input error: {e}")
                break  # Exit on unexpected errors

        # Fallback to keyboard input after max attempts
        speak("Switching to keyboard input. Please type 'yes' or 'no'.")
        user_input = input("(Voice failed) Type 'yes' or 'no': ").strip().lower()
        return user_input in ["yes", "y"]


    def _scrape_multiple_sources(self, product_name: str) -> List[Dict]:
        """Enhanced scraping with error handling"""
        results = []
        for scraper in [self.scraper_agent.scrape_amazon, self.scraper_agent.scrape_ebay]:
            try:
                results.extend(scraper(product_name))
                time.sleep(1)  # Be polite to servers
            except Exception as e:
                self.logger.error(f"Scraping error: {e}")
        return results

    def _get_product_reviews(self, products: List[Dict]) -> List[str]:
        """Get reviews for the top product"""
        if not products:
            return []
        try:
            review_data = self.scraper_agent.scrape_with_reviews(products[0]['link'])
            return review_data.get('reviews', [])
        except Exception as e:
            self.logger.error(f"Review collection error: {e}")
            return []

    def _generate_comprehensive_report(self, product_name: str,
                                       products: List[Dict],
                                       reviews: List[str]) -> str:
        """Generate report with all agentic features"""
        report = []
        report.append(self.summary_agent.generate_summary(product_name, products))
        report.append("\n" + self.comparison_engine.generate_comparison(products))

        # Get tips and include them in both report and spoken output
        self.tips = []  # Store tips as instance variable for voice output
        if products:
            self.tips = self.negotiator.get_negotiation_tips(products[0])
            report.append("\n💡 Shopping Tips:\n" + "\n".join(f"- {tip}" for tip in self.tips))

        if reviews:
            report.append("\n" + self.review_analyzer.generate_report(product_name, reviews))

        return "\n".join(report)

    def _present_results(self, product_name: str,
                         products: List[Dict],
                         summary: str):
        """Handle output presentation with full voice feedback"""
        print("\n" + "=" * 60 + "\n")
        print(summary)

        # Voice output now includes tips
        if products:
            best_deal = products[0]
            speak_output = [
                f"I found {len(products)} results for {product_name}.",
                f"The best deal is on {best_deal['site']} for {best_deal['price']}."
            ]

            if hasattr(self, 'tips') and self.tips:
                speak_output.append("Here are some shopping tips:")
                speak_output.extend(self.tips[:3])  # Speak top 3 tips

            if len(speak_output) > 2:  # If we have tips
                speak_output.append("You can see more details on screen, do you want to hear them.")

            speak(" ".join(speak_output))

    def terminate(self):
        """Clean shutdown"""
        self.logger.info("EcommerceAgent terminated")
        speak("Ecommerce agent is terminated.")
        print("👋 Ecommerce agent is now terminating.")


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO)
    agent = EcommerceAgent()
    try:
        agent.run()  # Simplified since loop is now in the class
    except KeyboardInterrupt:
        pass
    finally:
        agent.terminate()
