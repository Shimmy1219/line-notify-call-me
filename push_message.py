from linebot import LineBotApi
from linebot.models import TextSendMessage
import os


def push_message():
    LINE_CHANNEL_ACCESS_TOKEN = 'sEsX2yDRvj454rjlxv8JQ4coXHyUTaAwOextJx0YvtkGh2eZUPwz6opSHz3HKj7erXf+eMN5gXdFfwnTjsdMsChCBsMAeHbiNwfqEZZOBk5OSLlSLHeZVoFl5CXvyM0KKslYItAO/c9kwdpKvKQcegdB04t89/1O/w1cDnyilFU='
    USER_ID = 'U039da9cf7fe9ea0875e633f69b7f8e2e'

    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

    line_bot_api.push_message(
        USER_ID,
        TextSendMessage(text='よろしく'))

print(3//2)
