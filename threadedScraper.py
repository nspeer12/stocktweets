# Multithreaded StockTwitsScraper
# Team: Stock Market Sentiment Analysis
# Danish Siddiqui & Stepthen Speer

from threading import *
import requests
import json
from json import JSONDecodeError
import re
import time
import sys
import subprocess
import pymysql

class insert(Thread):
    
    def __init__(self,query):
        Thread.__init__(self)
        self.query = query
    
    def run(self):
        self.conn = pymysql.connect(user='admin_admin', password='E8Mv0oVq2f',host='35.211.184.200',database='admin_nlp_tweets')
        self.db = self.conn.cursor()
        self.db.execute(self.query)
        self.conn.commit()

class instance(Thread):
    
    def __init__(self, thread):
        
        Thread.__init__(self)
        self.thread = thread
        self.page = 1
        self.maxi = 0
        self.tweets = 0
        self.goal = 1
        self.symbol = ''
        self.tickerTweets = 0
        
        # connects to database and fetches all tickers to scrape
        # stores info in array
        
        self.conn = pymysql.connect(user='admin_admin', password='E8Mv0oVq2f',host='35.211.184.200',database='admin_nlp_tweets')
        self.db = self.conn.cursor()
        self.db.execute("select * from tickers where id<4 order by watchers asc")
        self.rs = self.db.fetchall(); 
        
    def proxyChange(self):
        
        # function access's computer's shell to refresh proxy connection
        # wait times are important due to network changing. 
        
        print("disconnecting...")
        subprocess.Popen("\"C:\Program Files\Private Internet Access\piactl.exe\" disconnect",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
        time.sleep(2)
    
        subprocess.Popen("pia-service.exe",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print("sleeping 30 seconds then reconnecting")
    
        time.sleep(30)
    
        subprocess.Popen("\"C:\Program Files\Private Internet Access\piactl.exe\" connect",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print("connected.")
    
        time.sleep(15)    
        
    def clean_tweet(self, tweet):
        
        # function deletes special characters 
        # deletes emoji's
        
        tweet = tweet.replace('\n',' ').replace('\r',' ') 
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def getTweetPage(self, initial=True):
        
        global pause
        
        while pause == True:
            
            print("Thread "+str(self.thread)+" is waiting for proxy change...")
            time.sleep(1)
        
        suc = 0
        
        while suc < 1:
            try:
                if initial==True:
                    r = requests.get('https://api.stocktwits.com/api/2/streams/symbol/'+self.symbol+".json");
                else:
                    r = requests.get("https://api.stocktwits.com/api/2/streams/symbol/"+self.symbol+".json?max="+str(self.maxi));
                    
                jsonText = json.dumps(r.json())
                
                self.dictionary = json.loads(jsonText)
                self.maxi = self.dictionary['cursor']['max']
                    
                self.length = len(self.dictionary['messages'])
                    
                self.i = 0
                    
                suc = 1
                pause = False
            
            # deal with exceptions that may occur
            # print out all exceptions for easier debugging
            
            except JSONDecodeError:
                for x in sys.exc_info(): 
                    print("Unexpected error:", x)
        
                suc -= 3
                print("Retrying in "+str(suc*-1)+"s...")
                time.sleep(suc*-1)
            
            # generally the key error results from stocktwits API blocking calls
            # requires reconnection to proxy
            
            except KeyError:
                for x in sys.exc_info(): 
                    print("Unexpected error:", x)

                suc -= 10
                print("Retrying in "+str(suc*-1)+"s...")
                time.sleep(suc*-1)
                
                if suc < 0 or totalPages % 200 == 0:
                    
                    pause = True
                    
                    print("Pausing initiated by Thread: ",self.thread)
                    print("Changing Proxy...")
                    
                    self.proxyChange()
            except:
                for x in sys.exc_info(): 
                    print("Unexpected error:", x)
        
                suc -= 3
                print("Retrying in "+str(suc*-1)+"s...")
                time.sleep(suc*-1)
        
    def processData(self):
        
        # provide access to globals
        
        global totalPages
        global pause
        global totalTweets
        global start
        
        self.tickerTweets  = 0
        
        self.getTweetPage()
        
        # get the amount of tweets for this particular symbol
        while self.tickerTweets < self.goal:
            
            # get the amount of tweets for this page
            while self.i < self.length:
                
                message = self.dictionary['messages'][self.i]
            
                x = message['body'].replace("&#39;", "'").replace("&quot;","")
                x = self.clean_tweet(x)
                
                if(str(self.dictionary['messages'][self.i]['entities']['sentiment']) == "None"):
                    isNull = 0;
                    
                else:                     
                    if str(self.dictionary['messages'][self.i]['entities']['sentiment']['basic']) == "Bullish":
                        
                            totalTweets += 1
                            self.tweets += 1
                            self.tickerTweets += 1 
                            
                            print(str(round((time.time() - start)/totalTweets,3))+"s per tweet "+self.symbol+" | "+str(totalTweets)+" | "+str(self.tickerTweets)+"/"+str(self.goal)+" | Page # "+str(totalPages)+" | Page # "+str(self.page)+" | Tweet # "+str(self.i)+" | "+message['user']['username']+" | Bullish : "+str(self.thread))
                            
                            # insert bullish comment to database
                            if(len(x) > 0):
                                a = insert("insert into testing (ticker,tweet,sentiment,page) values ('"+self.symbol+"','"+x+"','Bullish','"+str(self.page)+"')")
                                a.start()
                                
                    if str(self.dictionary['messages'][self.i]['entities']['sentiment']['basic']) == "Bearish":
                        
                            totalTweets += 1
                            self.tweets += 1
                            self.tickerTweets += 1 
                            
                            print(str(round((time.time() - start)/totalTweets,3))+"s per tweet "+self.symbol+" | "+str(totalTweets)+" | "+str(self.tickerTweets)+"/"+str(self.goal)+" | Page # "+str(totalPages)+" | Page # "+str(self.page)+" | Tweet # "+str(self.i)+" | "+message['user']['username']+" | Bearish : "+str(self.thread))
                            
                            # insert bearish comment to database
                            if(len(x) > 0):
                                a = insert("insert into testing (ticker,tweet,sentiment,page) values ('"+self.symbol+"','"+x+"','Bearish','"+str(self.page)+"')")
                                a.start()
                                
                # increment position of the tweet on the page
                self.i += 1
            
            # get the next page of tweets until goal is met
            self.getTweetPage(False)
            
            # increment the number of pages
            self.page += 1
            totalPages += 1
    
    def run(self):
        
        # run three threads
        # split up the tickers based on thread number
        
        i = 0
        for row in self.rs: 
           i += 1
           
           if(self.thread == i and i == 1):
               print("Thread "+str(self.thread)+" will be running "+str(row[0])+" Symbol: "+row[1])
               self.symbol = row[1]
               self.goal = int(row[2]*0.1)
               self.processData()
               
           if(self.thread == i and i == 2):
               print("Thread "+str(self.thread)+" will be running "+str(row[0])+" Symbol: "+row[1])
               self.symbol = row[1]
               self.goal = int(row[2]*0.1)
               self.processData()
               
           if(self.thread == i and i == 3):
               print("Thread "+str(self.thread)+" will be running "+str(row[0])+" Symbol: "+row[1])
               self.symbol = row[1]
               self.goal = int(row[2]*0.1)
               self.processData()
               
           if(i == 3):
               i = 0

# Declare Global Variables 
start = time.time()
totalPages = 1
totalTweets = 0
pause = False

# initialize threads
t1 = instance(1)
t2 = instance(2)
t3 = instance(3)

# start threads
t1.start()
t2.start()
t3.start()
