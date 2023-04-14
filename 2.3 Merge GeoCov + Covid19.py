# Imports
import pandas as pd
import re
import numpy as np
import json
from datetime import datetime


# Load tweets
geocov_tweets = pd.read_csv("Tweets_geocoded_GeoCov.csv", keep_default_na=False, na_values=['']) # Namibia ISO2 = NA
covid19_tweets = pd.read_csv("Tweets_geocoded_Covid19.csv", keep_default_na=False, na_values=[''])

# Check columns
print(geocov_tweets.columns, '\n')
print(covid19_tweets.columns)

# Only grab needed columns so dataframes match
keep = ['created_at', 'hashtags', 'id', 'lang', 'place', 'text',
       'user_location', 'user_screen_name', 'cleaned', 'lowered', 'date',
       'location', 'geo_source', 'country_code']

# Merge
tweets = pd.concat([geocov_tweets[keep], covid19_tweets[keep]], ignore_index=True)

# Remove duplicates last time now that all data sets are merged
tweets = tweets.drop_duplicates(subset='lowered', keep=False)
tweets = tweets.drop_duplicates(subset='id', keep=False)
tweets = tweets.drop_duplicates(subset='text', keep=False).reset_index(drop=True)

# Add new Time column for exact time
def getTime(dtime):
    new_datetime = datetime.strftime(datetime.strptime(dtime,'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S')
    return new_datetime
tweets['time'] = tweets['created_at'].apply(getTime)
tweets['time'] = pd.to_datetime(tweets['time'], format='%Y-%m-%d %H:%M:%S')   

# Sort by date
tweets = tweets.sort_values(by='time', ascending=True).reset_index(drop=True)

# Create days into pandemic column
tweets['date'] = pd.to_datetime(tweets['date'], format='%Y-%m-%d')   
tweets['day'] = (tweets['date'] - tweets['date'].min())  / np.timedelta64(1,'D')

# Save as pickle to preserve datetimes for next steps
tweets.to_pickle("Tweets_geocoded.pkl")

