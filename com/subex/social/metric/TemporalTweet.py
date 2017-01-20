'''
Created on Jan 16, 2017

@author: binu.k
'''

class TemporalTweet(object):

    def __init__(self, tweet, retweets):
        sortedRT = retweets.sort_values.sort_values(by = ['tweet_created_at'], ascending=True)
        sortedRT.groupBy()