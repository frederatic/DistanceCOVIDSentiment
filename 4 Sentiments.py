
# Imports
import pandas as pd
import numpy as np


# Load data
tweets = pd.read_pickle('Tweets_distances.pkl')

# Get sentiment score for each tweet
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# from nltk.sentiment.vader import SentimentIntensityAnalyzer # ALTERNATIVE

vader_sentiment = SentimentIntensityAnalyzer()
tweets['VADER_sentiment'] = tweets['cleaned'].apply(lambda s: vader_sentiment.polarity_scores(s)['compound'])

# Categorize sentiment according to VADER's guidelines
# neutral sentiment: compound score is in between -0.05 and 0.05

def getAnalysis(score):
    if score > -0.05 and score < 0.05:
        return 'Neutral'
    elif score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'

tweets['VADER_polarity'] = tweets['VADER_sentiment'].apply(getAnalysis)


# Save data
tweets.to_pickle("Tweets_sentiments.pkl")
