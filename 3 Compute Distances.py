
# Imports
import pandas as pd
import numpy as np
import datetime


# Load first times and UN regions
times = pd.read_csv("country_first_cases.csv", keep_default_na=False, na_values=[''], parse_dates=['first_case_utc'])
# Format dates
times['first_case_utc'] = times['first_case_utc'].dt.strftime("%Y-%m-%d %H:%M:%S")
times['first_case_utc'] = pd.to_datetime(times['first_case_utc'], format='%Y-%m-%d %H:%M:%S')

# Load tweets
tweets = pd.read_pickle("Tweets_geocoded.pkl")
# Remove tweets from smaller countries where no COVID and distance info available.
tweets = tweets[~((tweets.country_code.isin(set(tweets.country_code.unique())-set(times.country_code.unique()))) | tweets.country_code.isnull())]
tweets.reset_index(drop=True, inplace=True)

# Load distances
distances = pd.read_csv("countries_distances to borders2.csv", keep_default_na=False, na_values=[''])
# Add for each tweet their continent, region and datetime their country got infected
cols = ['country_code', 'first_case_utc', 'Continent', 'Region']
tweets = tweets.merge(times[cols], how='left', on='country_code')


# Function to calculate distance from tweet's country to nearest COVID infected country

def countryDistance(tweet):
    # Tweets made at same time or after COVID hit their country will have a distance of -1
    if tweet.time>=tweet.first_case_utc:
        nearest_country = tweet.country_code
        nearest_country_distance = -1
    # But if their country is still not hit by COVID, then calculate distance to other countries
    else:
        # Create list of all countries infected before the tweet was made
        comparisons = times[times.first_case_utc <= tweet.time].country_code.tolist()
        # For each country in the list, get their distance to tweet's country and choose lowest distance one
        nearest = distances[(distances.country1_code==tweet.country_code) & (distances.country2_code.isin(comparisons))].dist.idxmin()
        nearest_country = distances.iloc[nearest].country2_code
        nearest_country_distance = distances.iloc[nearest].dist
    # Return the nearest COVID infected country + distance to it in km
    return nearest_country, nearest_country_distance

# Run function and save in 2 new columns
tweets[['nearest_infected_country', 'phys_dist_km']] = tweets.apply(countryDistance, axis=1, result_type="expand")


# Categorize into 5 distances

def distCat5(tweet):
    # Use km measure to find if in own country or bordering
    if tweet.phys_dist_km == -1:
        return 'Close' # COVID is within the same country as tweet
    elif tweet.phys_dist_km >= 0 and tweet.phys_dist_km <= 50:
        return 'Bordering' # COVID is bordering tweet's home country
    # If not, check if any other country in the same region is infected by COVID before tweet was made
    elif any(times[times.Region==tweet.Region].first_case_utc<=tweet.time):    
        return 'Regional'
    # If not, check if any other country in the same continent is infected before tweet was made
    elif any(times[times.Continent==tweet.Continent].first_case_utc<=tweet.time):    
        return 'Continental'
    # If not, it's outside the continent
    else:
        return 'Global'
    
tweets['phys_dist_5cat'] = tweets.apply(distCat5, axis=1)


# Save
tweets.to_pickle("Tweets_distances.pkl")

