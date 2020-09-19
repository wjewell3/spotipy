# https://stackoverflow.com/questions/57580411/storing-spotify-token-in-flask-session-using-spotipy
from flask import Flask, render_template, redirect, request, session, make_response, session, Response, stream_with_context
import spotipy
import spotipy.util as util
#from credentz import *
import requests
import os
#from create_playlist import *
import sys
#import uwsgi
import logging
from flask_cors import CORS
import time
import subprocess
import signal
import io

def default_sigpipe():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

logging.basicConfig(filename='demo.log',level=logging.DEBUG)
application = Flask(__name__)
cors = CORS(application, resources={r"/api/*": {"origins": "*"}})

application.secret_key = 'blah'

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

# Set this to True for testing but you probably want it set to False in production.
SHOW_DIALOG = True

# authorization-code-flow Step 1. Have your application request authorization; 
# the user logs in and authorizes access
@application.route("/")
def verify():
    auth_url = f'{API_BASE}/authorize?client_id={CLI_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}&show_dialog={SHOW_DIALOG}'
    print(auth_url)
    return redirect(auth_url)

# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@application.route("/api_callback")
def api_callback():
    session.clear()
    code = request.args.get('code')

    auth_token_url = f"{API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":"http://127.0.0.1:5000/api_callback",
        "client_id":CLI_ID,
        "client_secret":CLI_SEC
        })

    res_body = res.json()
    print(res.json())
    session["toke"] = res_body.get("access_token")
    return redirect("user_input")

@application.route("/user_input")
def user_input():
    return render_template("base.html")
    # return """
    #      <html><body>
    #          <h2>Welcome to Will Jewell's Spotipy Playlist Creator</h2>
    #          <form action="/create_playlist_">
    #              <p>What's do you want to call your new playlist?</p>
    #              <input type='text' name='playlist_name'><br>
    #              <p>What genre score threshold do you want to use (default 20)?\n
    #              The higher the threshold score, the fewer songs you will get but the songs will be more relevant. </p>
    #              <input type='text' name='genre_score_thresh'><br>
    #              <input type='submit' value='Continue'>
    #          </form>
    #      </body></html>
    #      """ 
         

@application.route('/create_playlist_')
def create_playlist_():
    playlist_name = request.args.get('playlist_name')
    genre_score_thresh = request.args['genre_score_thresh']
    #session['playlist_name'] = playlist_name
    #session['genre_score_thresh'] = genre_score_thresh
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
        def inner():
            proc = subprocess.Popen(
                f'python test.py {playlist_name} {genre_score_thresh}'
                ,shell=True
                ,stdout=subprocess.PIPE
                ,universal_newlines=True
                ,bufsize=-1
                ,preexec_fn=default_sigpipe
            )
            for line in iter(proc.stdout.readline,''):
                yield line.rstrip() + '<br/>\n'
                proc.stdout.flush()

        return Response(inner(), mimetype='text/html') 
        #"""
        #<html><body>
            #<h2>Thank You!</h2>
            #<h3>Playlist Name {0}</h3>
            #<p>Genre Score Threshold {1}</p>
        #</body></html>
        #""".format(playlist_name, genre_score_thresh)
        #def inner():
            #cmd = ['python create_playlist.py', f"{playlist_name}", f"{genre_score_thresh}"]
            #print(cmd)
            #env = {**os.environ}
            #proc = subprocess.Popen(
                #cmd,
                ##['ls','-l'],         
                #shell=True,
                ##env=env,
                #stdout=subprocess.PIPE)
            #for line in iter(proc.stdout.readline,''):
                ##time.sleep(1)                          
                #yield str(line.rstrip()) + '<br/>\n'

    #return Response(inner(), mimetype='text/html') 
    #return redirect("yield")

@application.route('/yield')
def index():
    def inner():
        #cmd = f"['python create_playlist.py '{session['playlist_name']}', '{session['genre_score_thresh']'}']"
        #print(cmd)
        env = {**os.environ}
        proc = subprocess.Popen(
            #cmd,
            ['ls','-l'],         
            shell=True,
            #env=env,
            stdout=subprocess.PIPE)
        for line in iter(proc.stdout.readline,''):
            #time.sleep(1)                          
            yield str(line.rstrip()) + '<br/>\n'

    return Response(inner(), mimetype='text/html') 

if __name__ == "__main__":
    application.run(debug=True,threaded=True)