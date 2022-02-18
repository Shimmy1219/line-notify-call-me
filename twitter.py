import tweepy
import os
import psycopg2

CK = 'Bf75IpcBEdilBxemrqLjqsO4w'
CS = '4njUIUpTJtLfzKUTHZD1r9c0CHTTWY41IwHFpKNJ1If2EAZhab'

auth = tweepy.OAuthHandler(CK, CS)

def authorize_url():
  try:
    redirect_url = auth.get_authorization_url()
    return redirect_url
  except tweepy.TweepError:
    return "Return authorization url is failed."

def authentication_final(user_verifier,userid):
  global auth,api
  session =   {
      "request_token": auth.request_token,
  }


  # verifier = user_verifier
  # Let's say this is a web app, so we need to re-build the auth handler
  # first...
  auth = tweepy.OAuthHandler(CK, CS)
  token = session["request_token"]
  session.pop("request_token")
  auth.request_token = token

  DATABASE_URL = os.environ.get('DATABASE_URL')

  conn = psycopg2.connect(DATABASE_URL)
  cur = conn.cursor()

  #try:
  ts = auth.get_access_token(user_verifier)
  token = ts[0]
  secret = ts[1]
  auth.set_access_token(token, secret)
  api = tweepy.API(auth)
  #api.update_status('test tweet!!!!!') # 認証が成功した時にツイートで確認したい方は使ってください
  try:
    user = api.verify_credentials()
  except:
    return "The user credentials are invalid."
  cur.execute(
  "INSERT INTO database (\
    userid, access_token, acess_token_secret, twitterid, screen_name, name\
    ) VALUES(%s, %s, %s, %s, %s, %s)",
      (userid, token, secret, user.id_str, user.screen_name, user.name))
  conn.commit()

  cur.close()
  conn.close()
  return '認証成功'
  #except tweepy.TweepError:
    #return 'Error! Failed to get access token.'