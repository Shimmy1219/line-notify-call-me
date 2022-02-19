import tweepy
import os
import psycopg2

CK = 'Bf75IpcBEdilBxemrqLjqsO4w'
CS = '4njUIUpTJtLfzKUTHZD1r9c0CHTTWY41IwHFpKNJ1If2EAZhab'

auth = tweepy.OAuthHandler(CK, CS)


DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

def is_exists(column_name,data): #コラムにデータがあるか確認する。あればTrueを返す
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
      "SELECT EXISTS (SELECT * FROM database WHERE {} = '{}')".format(column_name,data))
    print(cur.fetchone()[0])
    return cur.fetchone()[0] #return True or False

def authorize_url():  #Twitterの認証URLを返す
  try:
    redirect_url = auth.get_authorization_url()
    return redirect_url #return URL
  except tweepy.TweepError:
    return "Return authorization url is failed."

def authentication_final(user_verifier,userid): #Twitterの認証をしてユーザーをデータベースに登録
  global auth,api
  session =   {
      "request_token": auth.request_token,
  }

  auth = tweepy.OAuthHandler(CK, CS)
  token = session["request_token"]
  session.pop("request_token")
  auth.request_token = token

  conn = psycopg2.connect(DATABASE_URL)
  cur = conn.cursor()


  try:
    ts = auth.get_access_token(user_verifier) #TWitterのアクセストークンを取得
    token = ts[0]
    secret = ts[1]
    auth.set_access_token(token, secret)
    api = tweepy.API(auth)
    #api.update_status('test tweet!!!!!') # 認証が成功した時にツイートで確認したい方は使ってください
    try: #認証が有効か確認。twitterのユーザーデータを返す
      user = api.verify_credentials()
    except:
      return "The user credentials are invalid."

    if is_exists('twitterid',user.id_str) == False: #もしデータベースにユーザーが存在しなかったら
      try: #データベースにユーザーを登録
        cur.execute(
        "INSERT INTO database (\
          userid, access_token, acess_token_secret, twitterid, screen_name, name\
          ) VALUES(%s, %s, %s, %s, %s, %s)",
            (userid, token, secret, user.id_str, user.screen_name, user.name))
        conn.commit()

        cur.close()
        conn.close()
        return '認証成功\nこんにちは！{}さん\nメニューからキーワードを登録することができます。'.format(user.name)
      except:
        return 'Error! Failed to access the database.'
    else: #もし既にユーザーがデータベースにあったら
      conn.commit()

      cur.close()
      conn.close()
      return '{}はログインされています'.format(user.screen_name)

  except tweepy.TweepError:
    return 'Error! Failed to get access token.'

def pushed_register_keyword(userid):
  DATABASE_URL = os.environ.get('DATABASE_URL')

  conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
  cur = conn.cursor()

  cur.execute('SELECT * FROM database WHERE userid = %s',(userid,))
  res = cur.fetchall()

  cur.close()
  conn.close()
  if len(res) == 1:
    return "キーワードを送信してください。",res
  else:
    for account in res:
      account[6]
    return "複数のアカウントでログインされています。キーワードを設定するアカウントを選択してください。", res

def register_keyword(keyword):
  DATABASE_URL = os.environ.get('DATABASE_URL')

  conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
  cur = conn.cursor()

  cur.execute('INSERT INTO database ')

