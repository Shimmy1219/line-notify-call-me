from linebot import LineBotApi
from linebot.models import TextSendMessage,Sender,FlexSendMessage
import os
import requests
import psycopg2
from ast import literal_eval
from pprint import pprint

with open("line-notify-call-me\payload2.json","r",encoding="utf-8") as f:
    payload = literal_eval(f.read())
pprint(payload)




def push_message(tweet,tweetID,name,icon_url):
    LINE_CHANNEL_ACCESS_TOKEN = 'sEsX2yDRvj454rjlxv8JQ4coXHyUTaAwOextJx0YvtkGh2eZUPwz6opSHz3HKj7erXf+eMN5gXdFfwnTjsdMsChCBsMAeHbiNwfqEZZOBk5OSLlSLHeZVoFl5CXvyM0KKslYItAO/c9kwdpKvKQcegdB04t89/1O/w1cDnyilFU='
    USER_ID = 'U039da9cf7fe9ea0875e633f69b7f8e2e'

    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    flex = FlexSendMessage(alt_text='alt_text',contents=payload,sender=Sender(name="ひふな",icon_url="https://pbs.twimg.com/profile_images/1493962626287927300/TkJmniBD_normal.jpg"))
    try:
        line_bot_api.push_message(
            USER_ID,messages=flex,
            #TextSendMessage(
            #    flex,
            )
    except requests.exceptions.ReadTimeout:
        #push_message()
        pass

#DATABASE_URL = 'postgres://vsszkbimyldkmr:cfa2e2f3909965bf340fd61f95648e6311616a0feb10cbb05c39713878b2be2d@ec2-3-228-222-169.compute-1.amazonaws.com:5432/d35fogc38bmvng'

#conn = psycopg2.connect(DATABASE_URL)
#cur = conn.cursor()
#cur.execute('SELECT keyword FROM database WHERE userid = %s',('U039da9cf7fe9ea0875e633f69b7f8e2e',))
#print(cur.fetchall())
"""LINE_CHANNEL_ACCESS_TOKEN = 'sEsX2yDRvj454rjlxv8JQ4coXHyUTaAwOextJx0YvtkGh2eZUPwz6opSHz3HKj7erXf#+eMN5gXdFfwnTjsdMsChCBsMAeHbiNwfqEZZOBk5OSLlSLHeZVoFl5CXvyM0KKslYItAO/c9kwdpKvKQcegdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
rich_menu = {
    'add_how':'richmenu-085de853cf35efb0ff72667940c0b689',
    'add_reg':'richmenu-c078890c117ca8e313d1d5f54735d9dc',
    'add_reg_del':'richmenu-0451994b328bb4d2525bf11584accbef'
    }


line_bot_api.link_rich_menu_to_user('Uaeebec1ac675eb11a35c285a83eab950', rich_menu["add_reg_del"])"""
push_message("test")