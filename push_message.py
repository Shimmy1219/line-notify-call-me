from linebot import LineBotApi
from linebot.models import TextSendMessage
import os

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
USER_ID = 'U039da9cf7fe9ea0875e633f69b7f8e2e'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

line_bot_api.push_message(
    USER_ID,
    TextSendMessage(text='ぷっしゅめっせーじです。やあ!'))
