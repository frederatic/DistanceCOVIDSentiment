# DistanceCOVIDSentiment
Code and data used in the study *Impact of Spatial Distance on Public Attention and Sentiment during the Spread of COVID-19*

The codes are numbered in order:
1. Cleans the tweets as described in the paper
2. 
    1. Geotags tweets from [COVID-19](https://github.com/echen102/COVID-19-TweetIDs) with location info from the [GeoNames](http://www.geonames.org/) database
    2. Geotags tweets from [GeoCov19](https://ieee-dataport.org/open-access/geocov19-dataset-hundreds-millions-multilingual-covid-19-tweets-location-information) with location info from GeoCov19 itself (Feb 1 to March 19 2020)
    3. Merge and organize the 2 datasets
6. Compute the spatial distance of each tweet to the nearest country infected by COVID
7. Compute the sentiment of each tweet using the VADER package
8. Add the total worldwide cases at the time to each tweet
9. Statistical Analysis + data visualization

Twitter does not allow the sharing of data, thus only IDs can be shared. *Final_Tweet_IDs.csv* contains the full list of tweets the final study ended up with after all the steps. The IDs can be hydrated either using Twarc in Python or DocNow's [Hydrator tool](https://github.com/DocNow/hydrator). Remaining files are data needed for the different pieces of code to run.

The code in this repository can then be run on the acquired Twitter data to obtain the needed variables for analysis. Note that the code has been streamlined and turned into generic functions so they can also be used for other studies.

For more details, please refer to the freely available published paper:

Atilla, F., & Zwaan, R. A. (2024). Impact of spatial distance on public attention and sentiment during the spread of COVID-19. *Informatics in Medicine Unlocked*, 101463. https://doi.org/10.1016/j.imu.2024.101463
