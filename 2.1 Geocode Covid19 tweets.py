# Imports
import pandas as pd
import re
import numpy as np


# Geoname Columns
columns = {
    'geonameid': float,
    'city': str,
    'city_ascii': str,
    'alternatenames': str,
    'lat': float,
    'lng': float,
    'featureclass': str,
    'featurecode': str,
    'iso2': str,
    'countrycode2': str,
    'admin1code': str,
    'admin2code': str,
    'admin3code': str,
    'admin4code': str,
    'population': float,
    'elevation': float,
    'dem': float,  # dem (digital elevation model)
    'timezone': str,
    'modificationdate': str
}



# Load the Geonames cities file
cities = pd.read_csv('cities15000.txt', sep='\t', header=None)
cities.columns = list(columns.keys())
# Remove redundant variables
redundant_vars = ['featureclass', 'featurecode','elevation',
       'dem', 'timezone', 'modificationdate']
cities.drop(redundant_vars, axis=1, inplace=True)

# Load country names and add them to cities dataframe
countryInfo = pd.read_csv('countryInfo.txt', sep='\t', header=None)
countryInfo2 = countryInfo.iloc[:, [0, 4]]
countryInfo2.columns = ['iso2', 'country']
cities = pd.merge(cities,countryInfo2,on='iso2',how='left')

# For duplicate cities, only keep most populous
cities = cities.sort_values(by='population', ascending=False).drop_duplicates(subset='city_ascii', keep="first").sort_index()

# Make new column that is iso2+admin1code and merge on that
cities = cities.astype({"iso2": str, "admin1code": str, "admin2code": str, "admin3code": str})
cities['admin1_complete'] = cities[['iso2', 'admin1code']].agg('.'.join, axis=1)
# Make new column that is iso2+admin1code+admin2code and merge on that
cities['admin2_complete'] = cities[['iso2', 'admin1code', 'admin2code']].agg('.'.join, axis=1)

# Load first-level and second-level administrative info
admin1txt = pd.read_csv('admin1CodesASCII.txt', sep='\t', header=None)
admin1txt = admin1txt.iloc[:, [0,1,2]]
admin1txt.columns = ['admin1_complete', 'admin1', 'admin1_ascii']

admin2txt = pd.read_csv('admin2Codes.txt', sep='\t', header=None)
admin2txt = admin2txt.iloc[:, [0,1,2]]
admin2txt.columns = ['admin2_complete', 'admin2', 'admin2_ascii']

# Merge administrative info
cities = pd.merge(cities, admin1txt, on='admin1_complete', how='left')
cities = pd.merge(cities, admin2txt, on='admin2_complete', how='left')

# Drop some variables
redundant_vars = ['countrycode2', 'admin1code','admin2code','admin3code',
       'admin4code', 'admin1_complete', 'admin2_complete']
cities.drop(redundant_vars, axis=1, inplace=True)

# Exclude cities named after other higher level regions
cities['city_ascii_l'] = cities['city_ascii'].str.lower()
cities['admin1_l'] = cities['admin1'].str.lower()
cities['country_l'] = cities['country'].str.lower()
cities = cities[~(cities['city_ascii_l'] == 'victoria')]
cities = cities[~(cities['city_ascii_l'].isin(cities['country_l'].values.tolist())) | (cities['city_ascii_l']==cities['country_l'])]
cities = cities[~(cities['city_ascii_l'].isin(cities['admin1_l'].values.tolist())) | (cities['city_ascii_l']==cities['admin1_l'])]
cities.reset_index(drop=True, inplace=True)


# # Geo-coding Tweet Locations
# The code from here on was adapted from user akhilram7 on Kaggle at: https://www.kaggle.com/code/akhilram7/geospatial-and-temporal-distribution-of-tweets/notebook
# 
# This is a manual method using lookup tables to assign clean, formatted locations to tweets. It is a free alternative to geocoding services which have rate limits and are costly.
# 
# The code does the following
# 1. Each tweet's location is a string that can contain toponyms such as the name of a city, state/province, country.
# 2. This string of words is split by a comma as most locations are formatted that way. 
# 3. Each of these split parts is compared to our GeoNames database of 25000 city names, state/province names, country names and codes.
# 4. If a match is found, that location is assigned to the tweet including any higher level information such as state and country.
# 
# This method does result in a loss of tweets, but that can be compensated for by starting out with a lot of raw data. This method also removes duplicate city names and only keeps the most populous, but this was negligible when we tested the same method but accounting for duplicate cities. If you plan to account for duplicate cities, my suggestion is to not only check for a city name, but also whether a tweet's location contains a state or country name. Only if both parts match, do you assign a city to the tweet.
# 



# Create lists for look up

# Alpha 2 codes  
world_city_iso2 = []
for c in cities['iso2'].str.lower().str.strip().values.tolist():
    if c not in world_city_iso2:
        world_city_iso2.append(c)
        
# Countries        
world_city_country = []
for c in cities['country'].str.lower().str.strip().values.tolist():
    if c not in world_city_country:
        world_city_country.append(c)

# Add USA as it's commonly used
world_city_iso2.append('usa')
world_city_country.append('united states')

# States and provinces
world_states = []
for c in cities['admin1'].str.lower().str.strip().tolist():
    world_states.append(c)

# Cities
world_city = cities['city'].fillna(value = '').str.lower().str.strip().values.tolist()
world_city_ascii = cities['city_ascii'].fillna(value = '').str.lower().str.strip().values.tolist()


# Load tweets file
tweets = pd.read_csv('Tweets_cleaned.csv')    

# Use only the tweets location column
user_location = tweets['location'].fillna(value='').str.split(',')

# Empty Columns are added in Tweets Dataset with values set to NaN, these will be filled in the loop
tweets["city"] = np.NaN
tweets["city_nonascii"] = np.NaN
tweets["admin1"] = np.NaN
tweets["admin2"] = np.NaN
tweets["country"] = np.NaN
tweets["country_code"] = np.NaN

# Loop over each tweet and add its location information
for each_loc in range(len(user_location)):
    # Get index of tweet
    ind = each_loc
    # Check if any of the words in the tweet's location matches either a city name, state name, country name or code
    # If they do, save that index
    order = [False,False,False,False]
    each_loc = user_location[each_loc]
    for each in each_loc:
        each = each.lower().strip()
        if each in world_city:
            order[0] = world_city.index(each)
        if each in world_city_ascii:
            order[0] = world_city_ascii.index(each)
        if each in world_states:
            order[1] = world_states.index(each)
        if each in world_city_country:
            order[2] = world_city_country.index(each)
        if each in world_city_iso2:
            order[3] = world_city_iso2.index(each)
    # Use the order list to retrieve the information and replace the NaN values of the tweet
    if order[0]:
        tweets["city_nonascii"][ind] = cities['city'][order[0]]
        tweets["city"][ind] = cities['city_ascii'][order[0]]
        tweets["admin2"][ind] = cities['admin2'][order[0]]
        tweets["admin1"][ind] = cities['admin1'][order[0]]
        tweets["country"][ind] = cities['country'][order[0]]
        tweets["country_code"][ind] = cities['iso2'][order[0]]
        # Continue to next iteration of loop, skipping rest of code, because we want to keep the most precise information
        continue
    if order[1]:
        tweets["admin1"][ind] = cities['admin1'][order[1]]
        tweets["country"][ind] = cities['country'][order[1]]
        tweets["country_code"][ind] = cities['iso2'][order[1]]
        continue
    if order[2]:
        try:
            tweets["country"][ind] = world_city_country[order[2]]
            tweets["country_code"][ind] = world_city_iso2[order[2]]
        except:
            pass
        continue
    if order[3]:
        tweets["country"][ind] = world_city_country[order[3]]
        tweets["country_code"][ind] = world_city_iso2[order[3]]
    continue
print('Geocoding done!')
    
# Format country columns    
tweets['country_code'] = tweets['country_code'].str.upper()
tweets['country'] = tweets['country'].str.title()

# Change USA code to US
tweets.loc[tweets.country_code=='USA', 'country_code'] = 'US'

# # Remove tweets without at least their country found
tweets = tweets[tweets['country'].notnull()].reset_index(drop=True)

# Add source col to identify them later from GeoCov
tweets['geo_source'] = 'GeoNames'

# Save final data set
tweets.to_csv('Tweets_geocoded_Covid19.csv', index = False)
print('Total tweets geocoded:', len(tweets))
tweets.head(3)
