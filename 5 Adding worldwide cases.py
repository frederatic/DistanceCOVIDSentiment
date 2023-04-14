
# Imports
import pandas as pd

# Load tweets
tweets = pd.read_pickle("Tweets_sentiments.pkl")

# Load worldwide cases
worldwide_info = pd.read_csv("worldwide-total by day.csv")

# Rename columns in preparation for merging with main tweets dataframe
worldwide_info.rename(columns = {'Date':'date', 'Confirmed':'world_cases', 'Deaths':'world_deaths', 'Recovered':'world_recovered'}, inplace = True)

# Datetime the dates
worldwide_info.date = pd.to_datetime(worldwide_info.date, format="%d-%m-%y")
worldwide_info['date'] = worldwide_info['date'].dt.strftime('%Y-%m-%d')
worldwide_info.date = pd.to_datetime(worldwide_info.date, format="%Y-%m-%d")

# Add number of cases worldwide to each tweet
tweets = tweets.merge(worldwide_info[['date', 'world_cases']], how='left', on=['date'])

# Save
tweets.to_csv('Tweets_final.csv', index=False)
# Save final IDs for sharing
tweets.id.to_csv('Final_Tweet_IDs.csv', index=False, header=None)

# Final look at the data
tweets.head(5)
