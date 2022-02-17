# インポートするライブラリ
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    FollowEvent, MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, TemplateSendMessage,
    ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
)
import os

from twitter import authorize_url, authentication_final

# 軽量なウェブアプリケーションフレームワーク:Flask
app = Flask(__name__)

# 環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
# 環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/")
def hello_world():
    return "hello world!"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    sending_message = determine_to_send(event.message.text)

    if type(sending_message) == str:
        sending_message = TextSendMessage(text=sending_message)

    line_bot_api.reply_message(
        event.reply_token,
        sending_message
    )

authentication_in_process = False

def determine_to_send(user_message):
    global authentication_in_process
    if "ログイン" in user_message or "ろぐいん" in user_message:
        reply = [TextSendMessage(text="ここにアクセスして認証してください"), TextSendMessage(text=authorize_url()),TextSendMessage(text="承認番号を送ってください")]
        authentication_in_process = True;
    elif authentication_in_process: # add regex to make sure the format matches
        authentication_in_process = False
        reply = authentication_final(user_message)
    elif "登録" in user_message or "とうろく" in user_message:
        reply = "通知するワードを入力してください"
    elif "ひろむ" in user_message or "洸夢" in user_message:
        reply = "どうされましたか"
    elif "ささん" in user_message:
        reply = "呼びましたか?"
    elif "こんにちは" in user_message:
        reply = "こんにちは"
    else:
        reply = '「' + user_message + '」って何？'
    return reply


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
