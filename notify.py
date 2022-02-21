import tweepy
from pprint import pprint
import time
import os
import psycopg2
from threading import Thread
from linebot import LineBotApi
from linebot.models import TextSendMessage,Sender

CK = 'Bf75IpcBEdilBxemrqLjqsO4w'
CS = '4njUIUpTJtLfzKUTHZD1r9c0CHTTWY41IwHFpKNJ1If2EAZhab'

auth = tweepy.OAuthHandler(CK, CS)

DATABASE_URL = 'postgres://vsszkbimyldkmr:cfa2e2f3909965bf340fd61f95648e6311616a0feb10cbb05c39713878b2be2d@ec2-3-228-222-169.compute-1.amazonaws.com:5432/d35fogc38bmvng'

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

def push_message(userid,text,name,url):
    LINE_CHANNEL_ACCESS_TOKEN = 'sEsX2yDRvj454rjlxv8JQ4coXHyUTaAwOextJx0YvtkGh2eZUPwz6opSHz3HKj7erXf+eMN5gXdFfwnTjsdMsChCBsMAeHbiNwfqEZZOBk5OSLlSLHeZVoFl5CXvyM0KKslYItAO/c9kwdpKvKQcegdB04t89/1O/w1cDnyilFU='
    USER_ID = userid

    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

    line_bot_api.push_message(
        USER_ID,
        TextSendMessage(
            text=text,
            sender=Sender(name=name,icon_url=url)
            )
        )

class getTweet():
  def __init__(self,lim,offset):
    self.do(lim,offset)

  def do(e,lim,offset):
    cur.execute("SELECT * FROM database ORDER BY id LIMIT {} OFFSET {} ".format(str(lim),str(offset)))
    database_list = [s for s in cur.fetchall() if s[7] != None]

    for record in database_list:
      AT = record[2]
      AS = record[3]
      auth.set_access_token(AT, AS)
      api = tweepy.API(auth)

      for status in api.home_timeline(count=2):
      #見映えのため区切る
        print('-------------------------------------------')
        print(record[6])
        #ユーザ名表示
        print('name:' + status.user.name)
        #内容表示
        print(status.text)
        for keyword in record[7]:
          if keyword in status.text:
            print("Push Message!!")
        #print(status.id_str)
        #print(status.user.screen_name)
        #print(status.user.id_str)
        print(status.user.profile_image_url_https)
        #print(status.created_at)
        #pprint(status)

STARTTIME = time.time()
cur.execute("SELECT id FROM database")
num = len(cur.fetchall())
Thread_num = num // 250 + 1
interval = num // Thread_num + 1
for i in range(Thread_num):
  arg = i * interval
  job = Thread(target=getTweet, args=(interval,arg))
  job.start()
ENDTIME = time.time()
print(ENDTIME-STARTTIME)