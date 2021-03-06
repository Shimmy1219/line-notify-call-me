# インポートするライブラリ
from pprint import pprint
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    FollowEvent, MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, TemplateSendMessage, URIAction, PostbackAction,MessageAction,
    ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction,QuickReply,QuickReplyButton
)
import os

from twitter import authorize_url, authentication_final,pushed_register_keyword,is_exists,register_keyword,remove_keyword

import psycopg2

# 軽量なウェブアプリケーションフレームワーク:Flask
app = Flask(__name__)

# 環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
# 環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

rich_menu = {
    'add_how':'richmenu-085de853cf35efb0ff72667940c0b689',
    'add_reg':'richmenu-c078890c117ca8e313d1d5f54735d9dc',
    'add_reg_del':'richmenu-0451994b328bb4d2525bf11584accbef'}


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

def delete_from_session(userid):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
    cur = conn.cursor()
    cur.execute("DELETE FROM session WHERE userid = '{}'".format(userid))
    conn.commit()

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

def record_session(exists,session,userid,column_session='session_id'):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
    cur = conn.cursor()
    if exists == True:
        cur.execute("UPDATE session SET {} = %s WHERE userid = %s".format(column_session),(session,userid))
        print("セッションを"+session+"に更新しました")
    else:
        cur.execute("INSERT INTO session ({},userid) VALUES (%s,%s)".format(column_session),(session,userid))
        print("新規にセッションを"+session+"で登録しました")
    conn.commit()

def determine_to_send(user_message,userid):
    DATABASE_URL = os.environ.get('DATABASE_URL')

    conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
    cur = conn.cursor()
    is_exists_user = is_exists('session','userid',userid) #セッションにいるかどうか
    if is_exists_user: #セッションにユーザーがいるかどうか
        cur.execute('SELECT session_id FROM session WHERE userid = %s',(userid,))
        session = cur.fetchone()[0]
        print("現在のセッションは"+ session+"です")
    if "reset" in user_message: #resetが入力されたらセッション情報を削除する
        delete_from_session(userid)
        reply = "キャンセルしました。"
    elif "How to use" in user_message:
        reply = "これは登録したキーワードがTwitterのタイムラインに出てくると通知するサービスです\nLogin for TwitterのボタンでTwitterにログインし、その後表示されるキーワード登録ボタンで通知してほしいキーワードを登録してください。"
    elif "ログイン" in user_message or "ろぐいん" in user_message: #ログインと入力されたら
        if is_exists_user == False:
            record_session(is_exists_user,'authentication_in_process',userid)
            reply = [TextSendMessage(text="ここにアクセスして認証してください"), TextSendMessage(text=authorize_url()),TextSendMessage(text="承認番号を送ってください")]
        elif is_exists_user == True and session == 'authentication_in_process':
            reply = "上記のURLにアクセスして承認番号を送信してください。操作をリセットする場合はresetを入力してください"
        else:
            quick_reply_list = ["reset","continue"]
            items = [QuickReplyButton(action=MessageAction(label=f"{word}", text=f"/{word}")) for word in quick_reply_list]
            reply = TextSendMessage(text= "操作が異なります。\nresetボタンを押すと通常状態に戻ります",
                               quick_reply=QuickReply(items=items))
    elif is_exists_user == True and session == 'authentication_in_process': #ログインする処理
        reply = authentication_final(user_message,userid)
        delete_from_session(userid)
    elif "登録" in user_message or "とうろく" in user_message: #キーワード登録したい
        if is_exists_user == False: #もしセッションにいなかったら
            reply, account_list = pushed_register_keyword(userid) #ログインしている垢の数を取得
            if len(account_list) > 1: #もしログイン済みの垢が複数あったら
                record_session(is_exists_user,'select_account_process_to_register_word',userid) #セッション名を登録
                button_list = [] #ボタンのリストを作る
                for i in range (len(account_list)):
                    button_obj = MessageAction(label=account_list[i][6],text=account_list[i][5])
                    button_list.append(button_obj)
                reply = make_button_template("キーワードを登録するアカウントを選択してください","ログイン済のアカウント",button_list)
            if len(account_list) == 1: #もしログインしてる垢が１つなら
                pprint(account_list)
                record_session(is_exists_user,'register_keyword_process',userid) #セッション名を登録
                record_session(True,account_list[0][5],userid,'logined_twitterid') #ログインしている垢を登録
                reply = "キーワードを送信してください"
        elif is_exists_user == True and session == 'register_keyword_process' or session == 'register_keyword_process':
            reply = "キーワードを送信してください"
        else:
            quick_reply_list = ["reset","continue"]
            items = [QuickReplyButton(action=MessageAction(label=f"{word}", text=f"/{word}")) for word in quick_reply_list]
            reply = TextSendMessage(text= "操作が異なります。\nresetボタンを押すと通常状態に戻ります",
                               quick_reply=QuickReply(items=items))
    elif is_exists_user == True and session == 'select_account_process_to_register_word': #セッションが垢選択セッションなら
        record_session(is_exists_user,'register_keyword_process',userid) #セッション名を登録
        record_session(is_exists_user,user_message,userid,'logined_twitterid') #ログインしている垢を登録
        reply = "キーワードを送信してください"
    elif is_exists_user == True and session == 'register_keyword_process': #セッションが登録プロセスなら
        cur.execute("SELECT keyword FROM database WHERE userid = '{}'".format(userid))
        user_keyword_list = cur.fetchall()
        print("user_keyword_listは" + str(user_keyword_list))
        first_register = True
        for keyword_list in user_keyword_list:
            for keyword in keyword_list:
                if type(keyword) == list:
                    first_register = False
                    break
        print(first_register)
        if "/exit" in user_message: #もしexitが入力されたら
            reply = "登録ありがとうございました。"
            cur.execute("DELETE FROM session WHERE userid = '{}'".format(userid)) #セッションから削除
            conn.commit()
        elif "/continue" in user_message:
            reply = "登録したいキーワードを選択してください。"
        else: #登録する
            cur.execute("SELECT logined_twitterid FROM session WHERE userid = '{}' AND session_id = '{}'".format(userid,session))
            screen_name = cur.fetchone()[0] #ログインしている垢を取得
            register_keyword(userid,screen_name,user_message) #キーワードを登録
            quick_reply_list = ["exit","continue"]
            items = [QuickReplyButton(action=MessageAction(label=f"{word}", text=f"/{word}")) for word in quick_reply_list]
            reply = TextSendMessage(text= "登録しました。\n続けて登録したい場合はキーワードを送信してください\n終了する場合はexitを入力してください。",
                               quick_reply=QuickReply(items=items))
        if first_register == True:
            line_bot_api.link_rich_menu_to_user(userid, rich_menu["add_reg_del"])

    elif "キーワード削除" in user_message: #キーワードを削除したかったら
        if is_exists_user == False: #もしセッションにいなかったら
            reply, account_list = pushed_register_keyword(userid) #ログインしている垢を取得
            if len(account_list) > 1: #もしログイン済みの垢が複数あったら
                record_session(is_exists_user,'select_account_process_to_remove_word',userid) #セッションを垢選択プロセスにする
                button_list = [] #垢リストを作成
                for i in range (len(account_list)):
                    button_obj = MessageAction(label=account_list[i][6],text=account_list[i][5])
                    button_list.append(button_obj)
                reply = make_button_template("キーワードを削除するアカウントを選択してください","ログイン済のアカウント",button_list)
            if len(account_list) == 1: #もしログインしてる垢が１つなら
                record_session(is_exists_user,'remove_keyword_process',userid) #セッションを削除プロセスに移動
                record_session(True,account_list[0][5],userid,'logined_twitterid') #ログイン済の垢をセッションに登録
                cur.execute("SELECT keyword FROM database WHERE userid = '{}' AND screen_name = '{}'".format(userid,user_message))
                keyword_list = cur.fetchone()[0] #登録されているキーワードをリストで取得
                print("登録されているキーワードは" + str(keyword_list))
                button_list = [] #ボタンのリストを作る
                for i in range (len(keyword_list)):
                    button_obj = MessageAction(label=keyword_list[i],text=keyword_list[i])
                    button_list.append(button_obj)
                reply = make_button_template("削除するキーワードを選択してください","登録済みのキーワード",button_list)
        else:
            quick_reply_list = ["reset","continue"]
            items = [QuickReplyButton(action=MessageAction(label=f"{word}", text=f"/{word}")) for word in quick_reply_list]
            reply = TextSendMessage(text= "操作が異なります。\nresetボタンを押すと通常状態に戻ります",
                               quick_reply=QuickReply(items=items))
    elif is_exists_user == True and session == 'select_account_process_to_remove_word': #もしセッション選択プロセスなら
        record_session(is_exists_user,user_message,userid,'logined_twitterid') #ユーザーが送信したIDを登録する
        cur.execute("SELECT keyword FROM database WHERE userid = '{}' AND screen_name = '{}'".format(userid,user_message))
        keyword_list = cur.fetchone()[0] #登録されているキーワードリストを取得
        if keyword_list == None or len(keyword_list) == 0:
            reply = "キーワードは登録されていません"
        else:
            record_session(is_exists_user,'remove_keyword_process',userid) #セッションを削除プロセスに移動
            print("登録されているキーワードは" + str(keyword_list))
            button_list = [] #ボタンのリストを作る
            for i in range (len(keyword_list)):
                button_obj = MessageAction(label=keyword_list[i],text=keyword_list[i])
                button_list.append(button_obj)
            reply = make_button_template("削除するキーワードを選択してください","登録済みのキーワード",button_list)
    elif is_exists_user == True and session == 'remove_keyword_process': #もし
        if "/exit" in user_message:
            reply = "ありがとうございました。"
            cur.execute("DELETE FROM session WHERE userid = '{}'".format(userid))
            conn.commit()
        else:
            cur.execute("SELECT logined_twitterid FROM session WHERE userid = '{}' AND session_id = '{}'".format(userid,session))
            screen_name = cur.fetchone()[0] #登録しているリストを取得
            reply = remove_keyword(userid,screen_name,user_message) #キーワードを削除する
            cur.execute("DELETE FROM session WHERE userid = '{}'".format(userid))
            conn.commit()

    else:
        reply = '「' + user_message + '」って何？'
    return reply


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
