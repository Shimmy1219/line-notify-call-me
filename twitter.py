import tweepy
import os
import psycopg2

CK = 'ctiRJV5FXu2uBm9rW3ltLe0z2'
CS = 'Gf2okVdVay66UO8MkQ18sTKTfvNMadJRuG5did1i5mRfLibHdw'

auth = tweepy.OAuthHandler(CK, CS)


DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

def is_exists(table,column_name,data): #コラムにデータがあるか確認する。あればTrueを返す
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
      "SELECT EXISTS (SELECT * FROM {} WHERE {} = '{}')".format(table,column_name,data))
    result = cur.fetchone()[0]
    print(result)
    return result #return True or False

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
    if is_exists('database','twitterid',user.id_str) == False: #もしデータベースにユーザーが存在しなかったら
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
      cur.close()
      conn.close()
      return '{}はログインされています'.format(user.screen_name)

  except tweepy.TweepError:
    return 'Error! Failed to get access token.'

def pushed_register_keyword(userid):
  DATABASE_URL = os.environ.get('DATABASE_URL')

  conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
  cur = conn.cursor()

  if is_exists('database','userid',userid) == True:
    cur.execute('SELECT * FROM database WHERE userid = %s',(userid,))
    res = cur.fetchall()
    cur.close()
    conn.close()
    if len(res) == 1:
      return "キーワードを送信してください。",res
    else:
      return "複数のアカウントでログインされています。キーワードを設定するアカウントを選択してください。", res
  else:
    res = []
    cur.close()
    conn.close()
    return "まずtwitterにログインしてください",res



def register_keyword(userid,screen_name,keyword):
  DATABASE_URL = os.environ.get('DATABASE_URL')

  conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
  cur = conn.cursor()
  cur.execute(
      "SELECT keyword FROM database WHERE userid = '{}' AND screen_name = '{}'".format(userid,screen_name))
  result = cur.fetchone()[0]
  print(result)
  if result == None:
    keyword_list = [keyword]
    cur.execute("UPDATE database SET keyword = ARRAY{}  WHERE userid = '{}' AND screen_name = '{}'".format(str(keyword_list),userid,screen_name))
    conn.commit()
  else:
    cur.execute("SELECT keyword FROM database WHERE userid = '{}' AND screen_name = '{}'".format(userid,screen_name))
    keyword_list = cur.fetchone()[0]
    keyword_list.append(keyword)
    cur.execute("UPDATE database SET keyword = ARRAY{}  WHERE userid = '{}' AND screen_name = '{}'".format(str(keyword_list),userid,screen_name))
    conn.commit()

def remove_keyword(userid,screen_name,keyword):
  DATABASE_URL = os.environ.get('DATABASE_URL')

  conn = psycopg2.connect(DATABASE_URL,options="-c search_path=public")
  cur = conn.cursor()
  cur.execute(
      "SELECT keyword FROM database WHERE userid = '{}' AND screen_name = '{}'".format(userid,screen_name))
  result = cur.fetchone()[0]
  print(result)
  if result == None:
    return "なにも登録されていません"
  else:
    cur.execute("SELECT keyword FROM database WHERE userid = '{}' AND screen_name = '{}'".format(userid,screen_name))
    keyword_list = cur.fetchone()[0]
    keyword_list.remove(keyword)
    cur.execute("UPDATE database SET keyword = ARRAY{}  WHERE userid = '{}' AND screen_name = '{}'".format(str(keyword_list),userid,screen_name))
    conn.commit()
    return keyword + "を削除しました"

  cur.close()
  conn.close()



