import logging
from textblob import TextBlob
from collections import Counter
import re
from typing import List, Dict, Tuple
import random


class ReviewAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.review_highlights = []  # Store highlights for voice output
        self.summary_points = []  # Store summary points for voice output

    def analyze_sentiment(self, reviews: List[str]) -> Dict:
        """Enhanced quantitative sentiment analysis with more detailed metrics"""
        if not reviews:
            return {}

        sentiments = [TextBlob(review).sentiment.polarity for review in reviews]
        positive = [s for s in sentiments if s > 0.1]
        negative = [s for s in sentiments if s < -0.1]
        neutral = [s for s in sentiments if -0.1 <= s <= 0.1]

        return {
            'average': sum(sentiments) / len(sentiments),
            'positive': len(positive),
            'negative': len(negative),
            'neutral': len(neutral),
            'positive_percent': len(positive) / len(sentiments) * 100,
            'negative_percent': len(negative) / len(sentiments) * 100,
            'strongest_positive': max(sentiments, default=0),
            'strongest_negative': min(sentiments, default=0)
        }

    def extract_keywords(self, reviews: List[str], n=10) -> Tuple[List[str], Dict]:
        """Identify common terms with frequencies"""
        words = []
        for review in reviews:
            # Remove common stop words and short words
            cleaned = re.findall(r'\b[a-z]{4,}\b', review.lower())
            words.extend([w for w in cleaned if w not in ['this', 'that', 'they', 'with', 'have']])

        counter = Counter(words)
        return [word for word, count in counter.most_common(n)], dict(counter.most_common(n))

    def extract_representative_reviews(self, reviews: List[str], n=3) -> List[str]:
        """Find representative reviews (most positive, most negative, most detailed)"""
        if not reviews:
            return []

        # Get most positive
        positive = sorted(reviews, key=lambda x: TextBlob(x).sentiment.polarity, reverse=True)[:n]

        # Get most negative
        negative = sorted(reviews, key=lambda x: TextBlob(x).sentiment.polarity)[:n]

        # Get most detailed (longest with keywords)
        detailed = sorted(reviews, key=lambda x: len(x.split()), reverse=True)[:n]

        # Combine and dedupe
        combined = list(set(positive + negative + detailed))
        random.shuffle(combined)
        return combined[:n]

    def generate_report(self, product_name: str, reviews: List[str]) -> str:
        """Generate comprehensive review summary with voice-friendly highlights"""
        if not reviews:
            self.review_highlights = [f"No reviews found for {product_name}"]
            return f"No reviews found for {product_name}"

        # Reset voice output storage
        self.review_highlights = []
        self.summary_points = []

        sentiment = self.analyze_sentiment(reviews)
        keywords, keyword_counts = self.extract_keywords(reviews)
        representative_reviews = self.extract_representative_reviews(reviews)

        # Build text report
        report = f"📊 Detailed Review Analysis for {product_name}:\n\n"
        report += "⭐ Sentiment Analysis:\n"
        report += f"- Positive: {sentiment['positive']} reviews ({sentiment['positive_percent']:.1f}%)\n"
        report += f"- Negative: {sentiment['negative']} reviews ({sentiment['negative_percent']:.1f}%)\n"
        report += f"- Neutral: {sentiment['neutral']} reviews\n"
        report += f"- Average Sentiment: {sentiment['average']:.2f} (scale: -1 to 1)\n\n"

        report += "🔍 Key Themes:\n"
        for word, count in keyword_counts.items():
            report += f"- {word.capitalize()}: {count} mentions\n"
        report += "\n"

        report += "💬 Representative Reviews:\n"
        for i, review in enumerate(representative_reviews, 1):
            report += f"{i}. {review}\n\n"

        # Prepare voice output components
        self.summary_points.extend([
            f"Customers have mixed opinions about {product_name}.",
            f"{sentiment['positive_percent']:.0f} percent of reviews are positive.",
            f"The main topics mentioned are {', '.join(keywords[:3])}."
        ])

        self.review_highlights.extend([
            "Here's what some customers said:",
            *[f"Review {i + 1}: {review[:150]}{'...' if len(review) > 150 else ''}"
              for i, review in enumerate(representative_reviews)]
        ])

        return report

    def get_voice_summary(self) -> List[str]:
        """Get the review summary optimized for voice output"""
        return self.summary_points + self.review_highlights
