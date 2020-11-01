# -*- coding: utf-8 -*-
import requests
import json
from json import JSONDecodeError
import re
import datetime
from datetime import date, timedelta
import time
import sys

def printToFile(linesOfData):
    with open('ZMSentiment.csv','w') as file:
        for line in linesOfData:
            file.write(line)
            file.write('\n')

def clean_tweet(tweet):
    
    tweet = tweet.replace('\n',' ').replace('\r',' ')
    tweet = re.sub("\$[A-Z]*","<SYM>", tweet)
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


# specify symbol to scrape
symbol = "ZM"
linesOfData = []
i = 0
bulls = 0
bears = 0
page = 1
totalTweets = 0; 


''' getting first page via IP rotation
headers = {"apikey": "bf892dc0-ba87-11ea-aa7d-4f92d4ba4d88"}
params = (("url","https://api.stocktwits.com/api/2/streams/symbol/"+symbol+".json"),);
r = requests.get('https://app.zenscrape.com/api/v1/get', headers=headers, params=params);
'''

# getting first page without ip rotation.
r = requests.get('https://api.stocktwits.com/api/2/streams/symbol/'+symbol+".json");

jsonText = json.dumps(r.json())
dictionary = json.loads(jsonText)
maxi = dictionary['cursor']['max']
length = len(dictionary['messages'])

# number of tweets on the first page. 
# if 30 then it works well
print(length)

# master while loop can be configured 
# either total labelled tweets or totalpages to scrape

while totalTweets < 2000: 
        
    while i < length:
        
        isBull = 0; 
        isBear = 0; 
        isNull = 0; 
        
        message = dictionary['messages'][i]
        
        x = message['body'].replace("&#39;", "'").replace("&quot;","")
        
        x = clean_tweet(x)
        
        # dealing with the time the comment was posted. 
        strTime = message['created_at'].replace("T"," ").replace("Z","")
        dateTime = datetime.datetime.strptime(strTime, '%Y-%m-%d %H:%M:%S')
    
       
        if(str(dictionary['messages'][i]['entities']['sentiment']) == "None"):
            isNull = 0; 
    
        else:
            if str(dictionary['messages'][i]['entities']['sentiment']['basic']) == "Bullish":
                    bulls += 1
                    isBull = 1
                    totalTweets += 1
                                        
            if str(dictionary['messages'][i]['entities']['sentiment']['basic']) == "Bearish":
                    bears += 1        
                    isBear = 1 
                    totalTweets += 1
    
    
        if(isBull and len(x) > 0):
            print(" ---------- "+str(totalTweets)+" | Page # "+str(page)+" | Tweet # "+str(i)+" | "+strTime+" | "+message['user']['username']+" | Bullish ---------- ")
            print(x+"\n\n")
            linesOfData.append(x+",Bullish")
        
        if(isBear and len(x) > 0):
            print(" ---------- "+str(totalTweets)+" | Page # "+str(page)+" | Tweet # "+str(i)+" | "+strTime+" | "+message['user']['username']+" | Bearish ----------")
            print(x+"\n\n")
            linesOfData.append(x+",Bearish")
        
        
        
        i += 1
    
    suc = 0
    while suc < 1:
        try:
            
            # wait time for call in seconds. 
            time.sleep(0.5)
            
            ''' using the IP rotating proxy 
            headers = {"apikey": "bf892dc0-ba87-11ea-aa7d-4f92d4ba4d88"}
            params = (("url","https://api.stocktwits.com/api/2/streams/symbol/"+symbol+".json?max="+str(maxi)),);
            r = requests.get('https://app.zenscrape.com/api/v1/get', headers=headers, params=params);
            '''
            
            # call without ip rotation. 
            r = requests.get("https://api.stocktwits.com/api/2/streams/symbol/"+symbol+".json?max="+str(maxi));
            
            
            jsonText = json.dumps(r.json())
            
            dictionary = json.loads(jsonText)
            
            maxi = dictionary['cursor']['max']
            
            length = len(dictionary['messages'])
            
            i = 0
            
            suc = 1
            
        except JSONDecodeError:
            for x in sys.exc_info(): 
                print("Unexpected error:", x)

            suc -= 3
            print("Retrying in "+str(suc*-1)+"s...")
            time.sleep(suc*-1)

        except KeyError:
            for x in sys.exc_info(): 
                print("Unexpected error:", x)

            suc -= 3
            print("Retrying in "+str(suc*-1)+"s...")
            time.sleep(suc*-1)
                                    
        except:
            for x in sys.exc_info(): 
                print("Unexpected error:", x)

            suc -= 3
            print("Retrying in "+str(suc*-1)+"s...")
            time.sleep(suc*-1)
        
    page += 1
    
print("Printing to File")
printToFile(linesOfData)
print("Completed.")
