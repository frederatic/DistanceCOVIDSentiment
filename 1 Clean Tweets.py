# Imports
import pandas as pd
import re
import numpy as np
from datetime import datetime


# Load raw tweets file
tweets = pd.read_csv('Tweets_raw.csv')

# Basic info
print('Shape is', tweets.shape)
print('Number of columns:',len(tweets.columns))
print('Columns are', tweets.columns)

# How many are retweets, replies, have coordinates, etc.
print(tweets.isnull().sum())

# Most tweeted languages %
print((tweets.lang.value_counts()/len(tweets)*100)[:10])


# Main cleaning function
# Removes rows in most efficient order

def clean_data(df):    
    print('Total tweets before cleaning:', len(df))
    
    # Remove retweets and quote tweets
    # If retweet_screen_name exists = retweet or if retweet_id exists
    print(len(df[df['retweet_id'].notnull()]) / len(df)*100, '% of remaining are retweets')
    df = df[df['retweet_id'].isnull()]
    print('Retweets removed!')

    # Remove replies
    df = df[df.in_reply_to_status_id.isnull()]

    # Only use English tweets
    print(len(df[df.lang=='en']) / len(df)*100, '% of remaining are English')
    df = df[df.lang=='en']
    print('Non-English removed!')

    # Remove tweets with no user_location or place
    # print(len(df[(df.place.notnull()) | (df.user_location.notnull())]) / len(df)*100, '% of remaining have location info')
    # df = df.dropna(subset=['place', 'user_location'], how='all') # ignored 'coordinates' field
    # print('Non-Locations removed!')

    # Remove other sources than Twitter Mobile or Web
    source_list = ['<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>',
                    '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>',
                   '<a href="https://mobile.twitter.com" rel="nofollow">Twitter Web App</a>',
                   '<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>',
                   '<a href="http://twitter.com/#!/download/ipad" rel="nofollow">Twitter for iPad</a>',
                  '<a href="https://about.twitter.com/products/tweetdeck" rel="nofollow">TweetDeck</a>']
    df = df[df['source'].isin(source_list)]

    # Remove verified users
    df = df.drop(df[df.user_verified == True].index)

    # Remove users with more than 10k followers
    df = df.drop(df[df.user_followers_count > 10000].index)
    # And more than 10k followed
    df = df.drop(df[df.user_friends_count > 10000].index)

    # Clean tweet text
    def removeUrls(tweet):
        tweet = re.sub(r'\s\s+', " ", tweet) # Remove whitespace
        tweet = tweet.replace('\n', ' ')
        tweet = re.sub(r'([\s]|^)RT([\s]+|:|$)', " ", tweet) # Remove RT
        tweet = re.sub(r'#', "", tweet) # Remove hashtag symbol only
        tweet = re.sub("@[A-Za-z0-9_]+","", tweet) # Remove mentions
        tweet = re.sub(r"http\S+", "", tweet) # Remove link
        tweet = re.sub(r"www.\S+", "", tweet) # Remove link
        tweet = re.sub(r'\s\s+', " ", tweet) # Remove whitespace
        tweet = tweet.lstrip(' ') # Remove empty space at begin
        #tweet = tweet.lower()
        return tweet
    df['cleaned'] = df['text'].apply(removeUrls)
    print('Cleaned tweet text!')
    
    # Remove duplicates
    df = df.drop_duplicates(subset='text', keep=False)
    # Remove other retweets
    df = df[~df.text.str.contains('via @|vía @|Via @|China Daily| qua @|WATE 6 News|#OmmcomNews|Live updates @')]
    df = df[~((df.text.str.contains('RT @')) | (df.text.str.startswith('RT')))]
    # Fix ampersand
    df['cleaned'] = df['cleaned'].str.replace('&amp;',' and ')
    df['cleaned'] = df['cleaned'].str.replace(r'\s+', ' ', regex=True)
    # Remove shared news articles
    df["lowered"] = df["cleaned"].str.lower()
    df = df.drop_duplicates(subset='lowered', keep=False)
    # Remove short tweets less than 2 words
    mask = df['lowered'].str.strip().str.split(' ').str.len()
    df = df[mask>2]
    df = df[~df.lowered.str.startswith('breaking:')] 
    # Remove news accounts
    df = df[~df.user_screen_name.str.lower().str.contains('news|press')]

    # Add new Date column for day only
    def getDate(dtime):
        new_datetime = datetime.strftime(datetime.strptime(dtime,'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d') # %H:%M:%S')
        return new_datetime
    df['date'] = df['created_at'].apply(getDate)

    # Add Location column: place if exists, otherwise user_location
    df['location'] = np.where(df['place'].isnull(), df['user_location'], df['place'])

    # Remove redundant variables e.g. tweet type, verified/not, etc.
    redundant_vars = ['coordinates', 'media', 'urls',
                      'retweet_count','favorite_count',
                      'possibly_sensitive', 'quote_id', 'retweet_id',
                      'retweet_screen_name', 'source', 'tweet_url', 'user_created_at',
                      'user_id', 'user_default_profile_image', 'user_description',
                      'user_favourites_count', 'user_followers_count', 'user_friends_count',
                      'user_listed_count', 'user_name', 'user_statuses_count', 
                      'user_urls', 'user_verified','user_time_zone', 
                      'in_reply_to_screen_name', 'in_reply_to_status_id', 'in_reply_to_user_id']
    df.drop(redundant_vars, axis=1, inplace=True)

    # # Save final data set
    # #df.to_csv('Cleaned tweets.csv', index = False)
    print('Total tweets left after cleaning:', len(df))
    print('\n')
    df.reset_index(drop=True, inplace=True)
    return df


# Clean and save raw tweets
tweets = clean_data(tweets)
print('Total tweets left:', len(tweets))
tweets.to_csv('Tweets_cleaned.csv', index=False)
tweets.head(3)

