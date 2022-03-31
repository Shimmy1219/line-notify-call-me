from aiohttp import Payload
import tweepy
from pprint import pprint
import time
import psycopg2
from threading import Thread
from linebot import LineBotApi
from linebot.models import TextSendMessage,Sender
import datetime
import json
import os

CK = 'ctiRJV5FXu2uBm9rW3ltLe0z2'
CS = 'Gf2okVdVay66UO8MkQ18sTKTfvNMadJRuG5did1i5mRfLibHdw'

auth = tweepy.OAuthHandler(CK, CS)

DATABASE_URL = 'postgres://vsszkbimyldkmr:cfa2e2f3909965bf340fd61f95648e6311616a0feb10cbb05c39713878b2be2d@ec2-3-228-222-169.compute-1.amazonaws.com:5432/d35fogc38bmvng'

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

def push_message(userid,text,name,url,type="tweet"):
    #LINE_CHANNEL_ACCESS_TOKEN = 'sEsX2yDRvj454rjlxv8JQ4coXHyUTaAwOextJx0YvtkGh2eZUPwz6opSHz3HKj7erXf#+eMN5gXdFfwnTjsdMsChCBsMAeHbiNwfqEZZOBk5OSLlSLHeZVoFl5CXvyM0KKslYItAO/c9kwdpKvKQcegdB04t89/1O/w1cDnyilFU='
    LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    USER_ID = userid

    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    if type == "tweet":
      
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
    cur.execute("SELECT * FROM database ORDER BY id LIMIT {} OFFSET {} ".format(str(lim),str(offset))) #n番目からi人のIDを取得する
    database_list = [s for s in cur.fetchall() if s[7] != None]#もしキーワード登録欄が空欄ではなかったら、userリストに入れる

    for record in database_list:#ユーザーリストからレコードを取り出す
      AT = record[2]
      AS = record[3]
      auth.set_access_token(AT, AS)
      api = tweepy.API(auth)
      try:
        statuses = api.home_timeline(count=20)#最新のタイムラインを20個取得する
      except tweepy.error.RateLimitError:#もしタイムラインの取得に失敗したら
        print(str(record[6])+"ユーザーでRateLimitErrorが発生しました！")
        continue#次のユーザーに行く
      x = 0
      for status in statuses:#statusに取得したタイムライン20個を入れる
        last_time = record[8]#前回取得したツイートとしてlast_tweet_create_atに保存する
        if record[8] == None:#もし初回の取得なら
          last_time = datetime.datetime(2022,2,21,17,22,00)#前回のツイートとして登録する
        if (status.created_at - last_time).total_seconds() > 0:#もし今回取得したツイートから前回取得したツイートより最新だったら、
        #前回取得したものと同じ時間なら実行されない。
        #見映えのため区切る
          print('-------------------------------------------')
          print(record[6])
          #ユーザ名表示
          print('name:' + status.user.name)
          #内容表示
          print(status.text)
          if record[4] != status.user.id_str:#もし取得したツイートが自分のものではなかったら
            for keyword in record[7]:#キーワードリストからキーワードを取得
              if keyword in status.text:#もしキーワードリストのキーワードがツイートに含まれていたら
                try:
                  push_message(record[1],status.text,status.user.name,status.user.profile_image_url_https)#メッセージを送信する
                except:
                  print("ERROR! "+str(record[1])+"に送信出来ませんでした。")
                break #１回反応したらbreakする
          if x == 0:#もし取得した中で最新のツイートならば
            cur.execute("UPDATE database SET last_tweet_created_at = '{}'  WHERE id = '{}'".format(status.created_at,record[0]))
            conn.commit() #データベースのlast_tweet_create_atに登録
          x+=1#Xを増やす

def run_thread():
  STARTTIME = time.time() #開始時間
  cur.execute("SELECT id FROM database")#データベースから全ユーザーのIDリストを取得
  num = len(cur.fetchall())#何人いるかを変数に
  Thread_num = num // 250 + 1#必要なスレッドの数を取得
  interval = num // Thread_num + 1#一つのスレッドに何人分を取得するか
  for i in range(Thread_num):#必要なスレッドの数だけ繰り返す
    arg = i * interval#何番目の人を取得するか
    job = Thread(target=getTweet, args=(interval,arg))#何人分、何番目の情報を付けてスレッド化
    job.start()
  ENDTIME = time.time()#終わりの時間
  print(ENDTIME-STARTTIME)#終わりの時間から開始時間を引く。１分以内なら正常