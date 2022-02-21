from linebot import LineBotApi
from linebot.models import TextSendMessage,Sender
import os
import requests


def push_message(i):
    LINE_CHANNEL_ACCESS_TOKEN = 'sEsX2yDRvj454rjlxv8JQ4coXHyUTaAwOextJx0YvtkGh2eZUPwz6opSHz3HKj7erXf+eMN5gXdFfwnTjsdMsChCBsMAeHbiNwfqEZZOBk5OSLlSLHeZVoFl5CXvyM0KKslYItAO/c9kwdpKvKQcegdB04t89/1O/w1cDnyilFU='
    USER_ID = 'U039da9cf7fe9ea0875e633f69b7f8e2e'

    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    try:
        line_bot_api.push_message(
            USER_ID,
            TextSendMessage(
                text=i,
                sender=Sender(name="ひふな",icon_url="https://pbs.twimg.com/profile_images/1493962626287927300/TkJmniBD_normal.jpg")))
    except requests.exceptions.ReadTimeout:
        push_message(i)
