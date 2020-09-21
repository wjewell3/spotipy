from flask import Flask, render_template, redirect, request, session, make_response, session, Response, stream_with_context
import spotipy
import spotipy.util as util
import requests
import os
import sys
import logging
from flask_cors import CORS
import time
import subprocess
import signal
import io
import webbrowser

def default_sigpipe():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

app = Flask(__name__)
#cors = CORS(application, resources={r"/api/*": {"origins": "*"}})

app.secret_key = 'blah'

API_BASE = 'https://accounts.spotify.com'

CLI_ID = os.environ['SPOTIPY_CLIENT_ID']
CLI_SEC = os.environ['SPOTIPY_CLIENT_SECRET']
SCOPE = '''
    playlist-modify-private, 
    playlist-modify-public,
    playlist-read-collaborative,
    playlist-read-private,
    user-follow-modify,
    user-follow-read,
    user-library-modify,
    user-library-read,
    user-modify-playback-state, 
    user-read-currently-playing, 
    user-read-email,
    user-read-playback-state, 
    user-read-private,
    user-read-recently-played, 
    user-top-read'''

# Make sure you add this to Redirect URIs in the setting of the application dashboard
REDIRECT_URI = "http://127.0.0.1:5000/api_callback"
#"http://localhost:8888/api_callback"
#http://127.0.0.1:5000/api_callback
# Set this to True for testing but you probably want it set to False in production.
SHOW_DIALOG = True

# authorization-code-flow Step 1. Have your application request authorization; 
# the user logs in and authorizes access
@app.route("/")
def verify():
    global auth_url
    auth_url = f'{API_BASE}/authorize?client_id={CLI_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}&show_dialog={SHOW_DIALOG}'
    print(auth_url)
    return redirect(auth_url)
    #time.sleep(1)
    

# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/api_callback")
def api_callback():
    session.clear()
    code = request.args.get('code')

    auth_token_url = f"{API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":REDIRECT_URI,
        "client_id":CLI_ID,
        "client_secret":CLI_SEC
        })

    res_body = res.json()
    print(res.json())
    session["toke"] = res_body.get("access_token")
    return redirect("user_input")


@app.route("/user_input")
def user_input():
    return render_template("base.html")         

@app.route('/create_playlist_')
def create_playlist_():
    playlist_name = request.args.get('playlist_name')
    genre_score_thresh = request.args['genre_score_thresh']
    if float(genre_score_thresh) <= 0:
        return """
        <html><body>
        <form action="/create_playlist">
                Please select a genre score threshold > 0
                What genre score threshold do you want to use (default 20)? 
                The higher the threshold score, the fewer songs you will get but the songs will be more relevant. 
                <input type='text' name='genre_score_thresh'><br>
                <input type='submit' value='Continue'>
        </form>
        </body></html>"""
    else: 
        subprocess.Popen(f"pyxtermjs -p 5001 --command python --cmd-args='create_playlist.py '{playlist_name}' '{genre_score_thresh}''"
        ,shell=True
        )
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:5001/',new=0)
        #subprocess.run('open localhost:5001/', shell=True)
    return 

if __name__ == '__main__':
    app.run()