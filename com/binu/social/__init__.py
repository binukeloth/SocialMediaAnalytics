import pandas as pd
from com.binu.social.metric.EnrichedTweet import TweetBox
import numpy as np

if __name__ == '__main__':
    # Reference - http://pandas.pydata.org/pandas-docs/version/0.13.1/generated/pandas.io.parsers.read_csv.html
    dfTweets = pd.read_csv('resource/tweets_bsy_org.csv', dtype={'tweet_favorite_count':np.float64, 'original_tweet_id':np.float64},\
                           na_values = ['\N', 'N'], escapechar='\\')
#     , sep=',', 
#                     verbose=True, na_filter=True, na_values = ['\N'], 
    #dfTwSummary = pd.read_csv('resource/tweets-summary.csv', parse_dates=[3])
    
    er = TweetBox('bsybjp', dfTweets)
    er.printStats()
