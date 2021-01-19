import tweepy
import time
import random
import urllib, json
from keys import *

# Authenticate to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
# We use this api object to talk to Twitter (to read data from Twitter and write data into Twitter)
# Create API object - The API class provides access to the entire twitter RESTful API methods.
api = tweepy.API(auth, wait_on_rate_limit=True)

FILE_NAME = 'last_seen_id.txt'

# Takes the file name and returns the last seen id
def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    # NOTE: We need to use tweet_mode='extended' below to show
    # all full tweets (with full_text). Without it, long tweets
    # would be cut off.
    mentions = api.mentions_timeline(
                        last_seen_id,
                        tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)

        # When it has #info
        if '#info' in mention.full_text.lower():
            print('found #info', flush=True)
            print('responding back...', flush=True)

            # Get the country 
            list_of_words = mention.full_text.lower().split()
            next_word = list_of_words[list_of_words.index("#info") + 1]
            print('The country: ' + next_word)

            # https://restcountries.eu/
            with urllib.request.urlopen("https://restcountries.eu/rest/v2/name/"+ next_word + "?fullText=true") as url:
                data = json.loads(url.read().decode())
                print(data)
                print(data[0]['name'])

            # Create a tweet
            api.update_status('@' + mention.user.screen_name 
                                + ' Country: ' + str(data[0]['name'])
                                + '\nCapital: ' + str(data[0]['capital'])
                                + '\nRegion: ' + str(data[0]['region'])
                                + '\nPopulation: ' + str(data[0]['population']), mention.id)

while True:
    reply_to_tweets()
    # Stops the process for 15 seconds and then restarts it
    time.sleep(15)