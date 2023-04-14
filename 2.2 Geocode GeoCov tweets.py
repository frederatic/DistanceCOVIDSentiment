# Imports
import pandas as pd
import re
import numpy as np
import json
import ast


# Function to geotag GeoCov tweets by adding the locations from the accompanying JSON files
def geotagGeoCov(filename):
    # Load tweets
    tweets = pd.read_csv(filename + '.csv')

    # Geotag
    print('Geotagging...', len(tweets), 'tweets')
    # Create list to store dataframes
    merged_dfs = [] 
    # Load locations in chunks as they are large files with info of tweets that are removed at this point
    chunks = pd.read_json('GeoCov locs' + '.json', lines=True, chunksize = 100000) # Load locations file, part of GeoCov. Recommended to load this and the tweets by day.
    for c in chunks:
        print('Next chunk started...')
        c.rename(columns={'tweet_id':'id', 'user_location':'user_location_geocov', 'place':'place_geocov', 'tweet_locations':'mentioned_locs'}, inplace=True)
        c.drop(['created_at', 'user_id'], axis=1, inplace=True)
        # Merge tweets with their locations and save in list
        merged_dfs.append(tweets.merge(c, how='inner', on='id'))
    # Merge all dataframes in list
    geotagged = pd.concat(merged_dfs)
    
    # Remove tweets that had multiple GeoCov locations as they are unreliable
    geotagged = geotagged.drop_duplicates(subset=['id'], keep=False).reset_index(drop=True)

    # Finish
    print('Tweets tagged:', geotagged.user_location_geocov.notnull().sum())  
    return geotagged
    
tweets = geotagGeoCov('Tweets_cleaned')


# # Extract country_code from new location columns


# Turn locations into actual dictionaries just in case they were loaded as strings
def turnDic(loc):
    try:
        dicloc = ast.literal_eval(loc)
    except:
        dicloc = loc
    return dicloc

tweets['user_loc_dic'] = tweets.user_location_geocov.apply(turnDic)
tweets['geo_loc_dic'] = tweets.geo.apply(turnDic)
tweets['place_loc_dic'] = tweets.place_geocov.apply(turnDic)

# Function
def extract_country(tweet):
    # Geo first
    if "country_code" in tweet['geo_loc_dic']:
        return tweet['geo_loc_dic']['country_code'].upper()
    # Then place
    elif "country_code" in tweet['place_loc_dic']:
        return tweet['place_loc_dic']['country_code'].upper()
    # Then location
    elif "country_code" in tweet['user_loc_dic']:
        return tweet['user_loc_dic']['country_code'].upper()
    
# Apply
tweets['country_code'] = tweets.apply(extract_country, axis=1)

# Remove tweets without a country code (mostly those with only mentioned locations in tweet_text)
tweets = tweets[tweets.country_code.notnull()].reset_index(drop=True)

# Save
tweets.to_csv('Tweets_geocoded_GeoCov.csv', index=False)
tweets.head(5)
