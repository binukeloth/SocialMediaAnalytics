'''
Created on Jan 4, 2017

@author: binu.k

account_id,tweet_text,tweet_id,tweet_favorite_count,retweet_count,user_id,user_screen_name,
user_location,tweet_created_at,tweet_language,tweet_location,tweet_source,original_tweet_id

References:
    1. Datetime formatting - https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    2.Reading CSV - http://pandas.pydata.org/pandas-docs/version/0.13.1/generated/pandas.io.parsers.read_csv.html
'''
from datetime import datetime
import pandas as pd
import numpy as np
import locale
from pprint import pprint
from com.subex.social.metric.TemporalTweet import TemporalTweet

locale.setlocale(locale.LC_NUMERIC, '')
class TweetBox(object):

    def __init__(self, screenName, tweets):
        self.name = screenName.lower()
        self.namePattern = '@' + self.name
        self.tweets = tweets;
 
        # Step 1 - Filter out records with invalid column
        #self.tweets = tweets[pd.notnull(tweets['tweet_created_at'])]
        #self.tweets = self.tweets.dropna(subset=['tweet_created_at'])
        #print(self.tweets.head())
        self.tweets = self.tweets[self.tweets['tweet_created_at'].str.len() == 24]
        #print(self.tweets.head(1))
        #print(self.tweets.dtypes)
      
        # 2. Date conversion  
        self.tweets.loc[ : ,'tweet_created_at'] = self.tweets['tweet_created_at']\
                .apply(lambda d: self.convert_date_string(d, '%a %b %d %H:%M:%S %Y'))
#         self.tweets['retweet_count'].replace(np.nan, 0);
#         self.tweets['tweet_favorite_count'].replace(np.nan, 0);
        
        # 3. Identify TweetType
        self.tweets.loc[ : ,'tweet_type'] = self.tweets.loc[:,['user_screen_name', 'original_tweet_id']]\
                .apply( lambda t:self.getTweetType(t), axis=1)
        self.orgTweets = self.tweets[(self.tweets['tweet_type'] == 'Self') | (self.tweets['tweet_type'] == 'Mention')]
        
        self.orgTweets.loc [ : ,'mention_count'] = self.orgTweets.loc[ :, 'tweet_type'].str.contains('Mention')
        self.orgTweets.loc[ : ,'activity_count'] = self.orgTweets['retweet_count'] + self.orgTweets['tweet_favorite_count']
        self.rowMean = self.orgTweets.loc[ : ,['retweet_count','tweet_favorite_count', 'mention_count']].mean()
        self.rowSum = self.orgTweets.loc[ : ,['retweet_count','tweet_favorite_count', 'mention_count']].sum()
        #print(self.rowSum, self.rowMean)
        
    def getTweetType(self, tweet):
        if(tweet[0].lower() == self.name):
            if(np.isnan(tweet[1])):
                return "Self"
            else:
                return "RT"
        else:
            if(np.isnan(tweet[1])):
                return "Mention"
            else:
                return "MentionRT"
    
    def getTweetCount(self, t='Org'):
        if(t == 'All'):
            return self.tweets.shape[0]
        elif(t == 'Org'):
            return self.orgTweets.shape[0]
        else:
            return (self.tweets['tweet_type'] == t).sum() 
        
    
    def getRTCount(self):
        return self.rowSum['retweet_count']
    
    def getRTAvg(self):
        return self.rowMean['retweet_count']
    
    def getFavCount(self):
        return self.rowSum['tweet_favorite_count']
    
    def getFavAvg(self):
        return self.rowMean['tweet_favorite_count']

    def getMentionCount(self):
        return self.rowSum['mention_count']
    
    def getMentionAvg(self):
        return self.rowMean['mention_count']
        
    def getEngagement(self):
        return (self.getFavCount() + self.getRTCount() + self.getMentionCount())
    
    def getImpression(self):
        return (self.getTweetCount() + self.getRTCount() + self.getMentionCount())
    
    def getEngPerc(self):
        return self.getEngagement() * 100 / self.getImpression()
    
    def convert_date_string(self, date_string, format):
        return (datetime.strptime(str(date_string).lstrip().rstrip(), format))
            
    def getMindate(self):
        return self.tweets['tweet_created_at'].min()

    def getMaxDate(self):
        return self.tweets['tweet_created_at'].max()
    
    def getTopN(self, by='Self', n=5):
        if(by == 'Self'):
            sortedTweets = self.orgTweets.sort_values(by = ['activity_count'], ascending=False)
        elif(by == 'Mention'):
            sortedTweets = self.orgTweets.loc[(self.orgTweets['tweet_type'] == 'Mention')]\
            .sort_values(by = ['activity_count'], ascending=False)
            
        return sortedTweets.iloc[range(n), :]\
            .loc[:,['tweet_text','retweet_count', 'tweet_favorite_count', 'user_screen_name']]
            
    def temporalAnalysis(self):
        temporalTweets = self.orgTweets.loc[(self.orgTweets['tweet_type'] == 'Self')]\
            .apply(lambda t: TemporalTweet(t, \
            self.orgTweets.loc[(self.orgTweets['original_tweet_id'] == t['tweet_id'])]), axis=1)
        
        print(temporalTweets.head())

    def printStats(self):
        print("********Stats***********")
        print("Number of tweets : " + self.getTweetCount().__str__())
        print("Number of Own tweets : " + self.getTweetCount('Self').__str__())
        print("Number of Unique tweets : " + self.getTweetCount().__str__())
        print("Tweets are from " + self.getMindate().__str__() 
              + ' to ' + self.getMaxDate().__str__())
        print("Count of Retweets " + self.getRTCount().__str__())
        print("Average of Retweets " + self.getRTAvg().__str__())
        print("Count of Mentions " + self.getMentionCount().__str__())
        print("Average of Mentions " + self.getMentionAvg().__str__())
        print("Count of Favorites " + self.getFavCount().__str__())
        print("Average of Favorites " + self.getFavAvg().__str__())
        
        print("Engagement " + self.getEngagement().__str__())
        print("Impression " + self.getImpression().__str__())
        print("Engagement(%) " + self.getEngPerc().__str__())
        
        print("Top Tweets ")
        print("--------------")
        pprint(self.getTopN(n=5, by = 'Mention'))
    
    # datetime.strptime(str('Sun, 2 Dec 2001'), '%a, %d %b %Y')
    # Wed Nov 30 14:19:38 +0000 2016
    # 11-30-2016 14:20:45
    