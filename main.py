# インポートするライブラリ
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    FollowEvent, MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, TemplateSendMessage, URIAction, PostbackAction,MessageAction,
    ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
)
import os

from twitter import authorize_url, authentication_final,pushed_register_keyword,is_exists

import psycopg2

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
    print(event.message.text)
    sending_message = determine_to_send(event.message.text,event.source.user_id)

    if type(sending_message) == str:
        print(sending_message)
        sending_message = TextSendMessage(text=sending_message)

    line_bot_api.reply_message(
        event.reply_token,
        sending_message
    )

authentication_in_process = False #twittterの認証をするプロセス
register_keyword_process = False #キーワードを登録するprocess
select_account_process = False #アカウントを選択するprocess
selected_account = None

def make_button_template(text,title,buttons_list):
    message_template = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            text=text,
            title=title,
            actions=buttons_list
    )
    )
    return message_template

def record_session(exists,session,userid):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
    cur = conn.cursor()
    if exists == True:
        cur.execute("UPDATE session SET session_id = %s WHERE userid = %s",(session,userid))
        print("UPDATEしました")
    else:
        cur.execute("INSERT INTO session (session_id,userid) VALUES (%s,%s)",(session,userid))
        print("INSERTしました")
    conn.commit()

def determine_to_send(user_message,userid):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
    cur = conn.cursor()
    is_exists_user = is_exists('session','userid',userid)
    if is_exists_user:
        cur.execute('SELECT session_id FROM session WHERE userid = %s',(userid,))
        session = cur.fetchone()
        print(session)
    if "reset" in user_message:
        cur.execute("UPDATE session SET session = 'normal' WHERE userid = '{}'".format(userid))
    elif "ログイン" in user_message or "ろぐいん" in user_message:
        record_session(is_exists_user,'authentication_in_process',userid)
        reply = [TextSendMessage(text="ここにアクセスして認証してください"), TextSendMessage(text=authorize_url()),TextSendMessage(text="承認番号を送ってください")]
    elif is_exists_user == True and session == 'authentication_in_process':
        if user_message.isdecimal() == False:
            reply = "上記のURLにアクセスし、表示される7桁の番号を入力してください。キャンセルの場合はresetと入力してください。"
        else:
            reply = authentication_final(user_message,userid)
            cur.execute("DELETE FROM session WHERE userid = '{}'".format(userid))
            conn.commit()
    elif "登録" in user_message or "とうろく" in user_message:
        reply, account_list = pushed_register_keyword(userid)
        if len(account_list) > 1:
            record_session(is_exists_user,'select_account_process_to_register_word',userid)
            button_list = []
            for i in range (len(account_list)):
                button_obj = MessageAction(label=account_list[i][6],text=account_list[i][5])
                button_list.append(button_obj)
            reply = make_button_template("キーワードを登録するアカウントを選択してください","ログイン済のアカウント",button_list)
        if len(account_list) == 1:
            record_session(is_exists_user,'register_keyword_process',userid)
            reply = "キーワードを送信してください"
    elif is_exists_user == True and session == 'select_account_process_to_register_word':
        record_session(is_exists_user,'register_keyword_process',userid)
        reply = "キーワードを送信してください"
    elif register_keyword_process:
        if "exit" in user_message:
            reply = "登録ありがとうございました。"
            cur.execute("DELETE FROM session WHERE userid = '{}'".format(userid))
            conn.commit()
        else:

            reply = "登録しました。\n続けて登録したい場合は語彙を選択してください\n終了する場合はexitを入力してください。"

    else:
        reply = '「' + user_message + '」って何？'
    return reply


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
