import eventlet
eventlet.monkey_patch(
    thread=False
    # ,select=True
    ,socket=False
)

from flask import Flask, render_template, redirect, request, session, make_response, session, Response, stream_with_context, jsonify
import spotipy
import spotipy.util as util
import requests
import os
import sys
import logging
#from flask_cors import CORS
import time
import subprocess
#import signal
import io
import webbrowser
from config import CONFIG
#import create_playlist
from flask_socketio import SocketIO, emit

API_BASE = 'https://accounts.spotify.com'

CLI_ID = CONFIG["env_variables"]['SPOTIPY_CLIENT_ID']
CLI_SEC = CONFIG["env_variables"]['SPOTIPY_CLIENT_SECRET']
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
REDIRECT_URI = CONFIG["env_variables"]['SPOTIPY_REDIRECT_URI']
#"http://localhost:8888/api_callback"
#http://0.0.0.0:5000/api_callback
# Set this to True for testing but you probably want it set to False in production.
SHOW_DIALOG = True

#async_mode = 'eventlet'

# def default_sigpipe():
#     signal.signal(signal.SIGPIPE, signal.SIG_DFL)

app = Flask(__name__)#, instance_relative_config=True)
app.secret_key = 'blah'
#cors = CORS(application, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, 
transports=['polling', 'websocket'], 
async_mode=None, 
#async_handlers=True, 
engineio_logger=True 
#manage_session=True
)
#previously async_mode='threading', also tempting to use 'eventlet'


    

import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
import requests
import math
import time
import pandas as pd
from IPython.display import display
from pandas.io.json import json_normalize
import numpy as np 
#import matplotlib.pyplot as plt  
import inspect
import pickle
from datetime import datetime, timedelta
import subprocess
#from flask import Flask, render_template, redirect, request, session, make_response, session, Response, stream_with_context
#from flask_socketio import SocketIO, emit



def define_scope():
    global username, scope, token, sp, user, headers
    username = CONFIG["env_variables"]['SPOTIPY_USERNAME']
    client_id = CONFIG["env_variables"]['SPOTIPY_CLIENT_ID']
    client_secret = CONFIG["env_variables"]['SPOTIPY_CLIENT_SECRET']
    redirect_uri = CONFIG["env_variables"]['SPOTIPY_REDIRECT_URI']
    scope = '''
    playlist-modify-private 
    playlist-modify-public 
    playlist-read-collaborative 
    playlist-read-private
    user-follow-modify 
    user-follow-read 
    user-library-modify 
    user-library-read 
    user-modify-playback-state 
    user-read-currently-playing 
    user-read-email 
    user-read-playback-state 
    user-read-private 
    user-read-recently-played 
    user-top-read'''
    try:
        token = util.prompt_for_user_token(username=username, 
                                        scope=scope, 
                                        client_id=client_id, 
                                        client_secret=client_secret, 
                                        redirect_uri=redirect_uri,
                                        cache_path=f".cache-{username}")
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username=username, 
                                        scope=scope, 
                                        client_id=client_id, 
                                        client_secret=client_secret, 
                                        redirect_uri=redirect_uri,
                                        cache_path=f".cache-{username}")
    sp = spotipy.Spotify(auth=token)
    user = sp.current_user()
    headers = {'Authorization': "Bearer {}".format(token)}
    return 'OK'

# 2. Get raw Spotify data of Liked (i.e. Hearted) songs into a dataframe
# 2a. Get raw data of liked songs into a list
def req(url,headers):
    r = requests.get(url, headers=headers)
    return json.loads(r.text)

def get_raw_liked_song_list():
    printio('Get_raw_liked_song_list')
    offset = 0
    url = f"https://api.spotify.com/v1/me/tracks?limit=50&offset={offset}"

    liked_song_count = req(url,headers=headers)["total"]
    printio(f"Liked song count: {liked_song_count}")

    raw_liked_songs = []
    for i in range(int(math.ceil(liked_song_count/50.0))):
        offset = 50*i
        raw_liked_songs.extend(req(f"https://api.spotify.com/v1/me/tracks?limit=50&offset={offset}",headers=headers)["items"])

    printio(f">> raw liked songs['0'] >> {raw_liked_songs[0]}")
    return raw_liked_songs

# 2b. transform liked song raw data list into df
# parse out data from Liked Songs' raw data
def song_metadata_to_df(raw_songs):
    printio('Transforming song raw data list into df')
    define_scope()
    # create empty df
    df = pd.DataFrame(columns = [
        'album', 
        'artist_uri', 
        'artist',
        'track',
        'url',
        'popularity',
        'added_at',
        'release_date',
        'release_year',
        'uri'
        ])
    # parse out songs 100 at a time
    for i in range(0, len(raw_songs)):
        if (i/100).is_integer():
            printio(f"{i}/{len(raw_songs)} parsed")
        try:
            album = raw_songs[i]['track']['album']['name']
            artist_uri = raw_songs[i]['track']['artists'][0]['uri'].split(':')[2]
            artist = raw_songs[i]['track']['album']['artists'][0]['name']
            track = raw_songs[i]['track']['name']
            url = raw_songs[i]['track']['external_urls']['spotify']
            popularity = raw_songs[i]['track']['popularity']
            added_at = raw_songs[i]['added_at']
            release_date = raw_songs[i]['track']['album']['release_date']
            release_year = release_date.split('-')[0]
            uri = raw_songs[i]['track']['uri']
            df = df.append(pd.DataFrame([[
                album, 
                artist_uri,
                artist, 
                track, 
                url, 
                popularity, 
                added_at, 
                release_date, 
                release_year,
                uri
                ]], columns = [
                'album', 
                'artist_uri', 
                'artist',
                'track',
                'url',
                'popularity',
                'added_at',
                'release_date',
                'release_year',
                'uri'
                ]))
        except:
            pass
    df.set_index('uri', inplace=True)
    display(df.head())
    return df

#3. Add audio features 
# Combine liked song df with audio feature df
def add_audio_feats(df):
    printio('Combining song_df with audio_feature_df')
    # get list of song uris
    song_uri_list = df.index.to_list()
    audio_feature_df = pd.DataFrame()
    for i in range(0,math.ceil(len(song_uri_list)/100)):
        define_scope()
        features = sp.audio_features(song_uri_list[(i)*100:100*(i+1)])
        audio_feature_df = audio_feature_df.append(pd.DataFrame(features))
    audio_feature_df.set_index('uri', inplace=True)
    # merge this 
    liked_song_df = df.merge(audio_feature_df, on = 'uri')
    display(liked_song_df.head())
    return liked_song_df.drop_duplicates()

#4. Add genre data
# 4a. Get artist_uris -> get genres
def get_genres(df):
    printio('Getting genres')
    g = []
    artist_uris = df['artist_uri'].unique()
    printio(f"{len(artist_uris)} distinct artists")
    for i in range(0, len(artist_uris)):
        if (i/100).is_integer():
            printio(f"{i}/{len(artist_uris)} parsed")
        try:
            g.append(req(url = f"https://api.spotify.com/v1/artists/{artist_uris[i]}",headers=headers)['genres'])
        except:
            define_scope()
            try:
                g.append(req(url = f"https://api.spotify.com/v1/artists/{artist_uris[i]}",headers=headers)['genres'])
            except:
                pass
    # genres_df's artist_uri column stores a list of genres per artist uri
    genres_df = pd.DataFrame({'artist_uri': artist_uris, 'genre list': g})
    
    printio('genre_df')
    display(genres_df.head())
    return genres_df

# There is a list of genres for one artist that must be broken out
def explode_genres(df):
    genre_exploded_df = df.explode('genre list')
    
    printio('genre_exploded_df')
    display(genre_exploded_df.head())
    return genre_exploded_df

# Add these genres back to the df for each song
def add_genres(df, genre_exploded_df):
    # the following does not work oddly enough
    # liked_song_df.reset_index().merge(genre_exploded_df, on = 'artist_uri', how = 'left').set_index('uri', inplace = True)
    df = df.reset_index().merge(genre_exploded_df, on = 'artist_uri', how = 'left').set_index('uri')
    df.rename(columns={'genre list': 'genre'}, inplace=True)
    
    printio('Merging genres into song_df')
    display(df.head())
    return df

#5. Create Genre Score

# Get genre counts for liked songs - the higher the count, the higher the score
def get_genre_counts(genre_exploded_df):
    printio('Getting genre counts')
    # establish genre counts (which will determine score)
    genre_count_df = pd.DataFrame(genre_exploded_df['genre list'].value_counts()).reset_index()
    genre_count_df.columns = ['genre','genre count']
    printio('genre_count_df.head()')
    display(genre_count_df.head())
    return genre_count_df

# Merge the genre counts with the song df and sum the genre column
def establish_genre_score(genre_count_df, df):
    printio('Merging genre counts with song_df')
    df = df.reset_index().merge(genre_count_df , on = 'genre',how = 'left')
    df.drop(columns=['genre'], inplace=True)
    display(df.head())

    groupby_cols = df.columns.to_list()[:-1]
    
    printio('Summing genre column')
    df = df.groupby(groupby_cols).sum().sort_values('genre count', ascending=False)
    df = df.rename({'genre count': 'genre score'}, axis=1).reset_index() 
    # reset index after summing - otherwise everything prior to sum will become index
    df.set_index('uri', inplace=True)
    display(df.head())
    return df

# 6. Create playlist df (to access disliked playlist)
# get playlist raw data (for dislikes)
def get_playlist_uris(playlists_raw):
    df = pd.DataFrame()
    for i in range(0, len(playlists_raw)):
        try:
            playlist = playlists_raw[i]['name']
        except:
            playlist = ''
        try:
            playlist_uri = playlists_raw[i]['uri']
        except:
            playlist_uri = ''
        try:
            song_count = playlists_raw[i]['tracks']['total']
        except:
            song_count = 0
        df = df.append(pd.DataFrame([[playlist, playlist_uri, song_count]], columns = ['playlist','playlist_uri','song_count']))
    df.set_index(['playlist'], inplace=True)
    printio('playlist_df')
    display(df)
    return df

def get_raw_disliked_song_list():
    playlists_raw = sp.current_user_playlists()['items']
    playlists_df = get_playlist_uris(playlists_raw)
    display(playlists_df)
    uri = playlists_df.loc['Dislikes']['playlist_uri']
    song_count = playlists_df.loc['Dislikes']['song_count']
    # extract data from Disliked songs
    dislike_raw_list = []
    for i in range(int(math.ceil(song_count/100.0))):
        dislike_raw_list.extend(sp.user_playlist_tracks(uri.split(':')[1], uri.split(':')[2], offset=i*100)['items'])
    printio('Getting raw disliked song list')
    return dislike_raw_list

# 7. Combine liked and disliked songs into my_songs dataframe with "Liked" flag
def combine_dfs_to_create_my_songs_df(df1,df2, save_destination):
    printio('Combining dfs to create my_songs_df and storing as pickle file')
    df1['Liked'] = 1
    df2['Liked'] = 0
    my_songs_df = pd.concat([df1,df2])
    #my_songs_df.to_:w(f"{save_destination}/my_songs.csv")
    #my_songs_df.to_pickle(f"{save_destination}/my_songs.pkl")
    display(my_songs_df.head())
    printio('successfully saved to .csv and .pkl files in save_destination')
    return 'OK'

# 7. Combine liked and disliked songs into my_songs dataframe with "Liked" flag
# 8. Get featured playlist uris so we can get their associated songs
def get_featured_playlist_uris(country, timestamp):
    printio('Getting raw_featured_playlist_df')
    url = f"https://api.spotify.com/v1/browse/featured-playlists?limit=50&offset=0&country={country}&timestamp={timestamp}"
    featured_playlist_count = req(url,headers=headers)['playlists']['total']
    df = pd.DataFrame()
    for i in range(0,featured_playlist_count):
        raw_featured_playlist = req(url,headers=headers)['playlists']['items']
        playlist = raw_featured_playlist[i]['name']
        playlist_uri = raw_featured_playlist[i]['uri']
        song_count = raw_featured_playlist[i]['tracks']['total']
        df = df.append(pd.DataFrame([[playlist, playlist_uri, song_count]], columns = ['playlist','playlist_uri','song_count']))
    df.set_index(['playlist'], inplace=True)
    display(df)
    return df

# 7. Combine liked and disliked songs into my_songs dataframe with "Liked" flag
# 8. Get featured playlist uris so we can get their associated songs
# 9. Get raw data from the songs
def get_raw_featured_playlist_song_list(df):
    raw_featured_songs = []
    for uri in df.loc[:,'playlist_uri'].to_list():
        song_count = df.loc[df['playlist_uri']==uri,'song_count'][0]
        offset = 0
        url = f"https://api.spotify.com/v1/playlists/{uri.split(':')[2]}/tracks?limit=50&offset={offset}"
        for i in range(int(math.ceil(song_count/100.0))):
            offset = 100*i
            raw_featured_songs.extend(req(url,headers=headers)['items'])

    return raw_featured_songs

def create_playlist(pred_like_playlist_name, df, genre_score_threshold):
    # create playlist
    define_scope()
    payload = {"name": pred_like_playlist_name}
    result = requests.post(url = f'https://api.spotify.com/v1/users/{username}/playlists'
                    , headers = headers
                    , data = json.dumps(payload)
                    )
    #printio(result)
    playlists_raw = sp.current_user_playlists()['items']
    playlists_df = get_playlist_uris(playlists_raw)
    playlist_uri = get_playlist_uris(playlists_raw).loc[playlists_df.index == pred_like_playlist_name,'playlist_uri'][0].split(':')[2]
    uri_list = df.loc[df['genre score']>= int(genre_score_threshold)].reset_index()['uri'].to_list()
    num_songs_to_add = len(uri_list)
    # add songs
    for i in range(int(math.ceil(num_songs_to_add/100.0))):
        url = f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks?uris={','.join(uri_list[i*100:(i+1)*100])}"
        requests.post(url, headers=headers)
    return 'OK'

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
def user_input(methods=['GET', 'POST']):
    return render_template("base.html")#, async_mode=socketio.async_mode)         

# @socketio.on('my event')
# def handle_my_custom_event(json, methods=['GET', 'POST']):
#     print('received my event: ' + str(json))
#     socketio.emit('my response', json, callback=messageReceived)

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

#@socketio.on('message', namespace='create_playlist_')#, namespace='/create_playlist_'
def printio(statement, methods=['GET', 'POST']):
    return socketio.emit('my response', {'data': str(statement)}, callback=messageReceived, broadcast=True)#, namespace='/create_playlist_'

#@app.route("/create_playlist_")
#@socketio.on('create playlist')#, namespace='/test')
@socketio.on('my event')
def create_playlist_(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    playlist_name = json['user_name'] #request.args.get('playlist_name')
    genre_score_thresh = json['message'] #request.args['genre_score_thresh']
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
        #return 'ok'
        define_scope()
        try:
            pred_like_playlist_name = playlist_name
            genre_threshold = genre_score_thresh
        except:
            pred_like_playlist_name = 'test'
            genre_threshold = 20
        printio(f"pred_like_playlist_name = {pred_like_playlist_name}")
        printio(f"genre threshold = {genre_threshold}")
        printio('Scope defined')
        printio('****PART 1: Get Liked Songs Dataframe****')
        raw_liked_song_list = get_raw_liked_song_list()
        liked_song_df = song_metadata_to_df(raw_liked_song_list)
        liked_song_df = add_audio_feats(liked_song_df)
        genre_df = get_genres(liked_song_df)
        genre_exploded_df = explode_genres(genre_df)
        liked_song_df = add_genres(liked_song_df, genre_exploded_df)
        liked_genre_count_df = get_genre_counts(genre_exploded_df)
        liked_song_df = establish_genre_score(liked_genre_count_df, liked_song_df)
        printio('****PART 2: Get Disliked Songs Dataframe****')
        define_scope()
        raw_disliked_song_list = get_raw_disliked_song_list()
        disliked_song_df = song_metadata_to_df(raw_disliked_song_list)
        disliked_song_df = add_audio_feats(disliked_song_df)
        genre_df = get_genres(disliked_song_df)
        genre_exploded_df = explode_genres(genre_df)
        disliked_song_df = add_genres(disliked_song_df, genre_exploded_df)
        disliked_genre_count_df = get_genre_counts(genre_exploded_df)
        disliked_genre_count_df['genre count'] = disliked_genre_count_df['genre count'] * -1
        disliked_song_df = establish_genre_score(disliked_genre_count_df, disliked_song_df)
        printio('****PART 3: Combine liked and disliked songs into my_songs df and genre_count_df and save***')
        my_songs_df = combine_dfs_to_create_my_songs_df(liked_song_df,disliked_song_df,'.')
        genre_count_df = pd.concat([liked_genre_count_df, disliked_genre_count_df])
        #my_songs_df = pd.read_pickle("./my_songs.pkl")
        printio('****PART 4: Get songs from featured playlists and score them based on genre****')
        playlist_df = get_featured_playlist_uris('US',(pd.Timestamp.now()-timedelta(days=0)).strftime('%Y-%m-%dT%H:%M:%S.%Z'))
        raw_featured_playlist_songs_list = get_raw_featured_playlist_song_list(playlist_df)
        featured_playlist_song_df = song_metadata_to_df(raw_featured_playlist_songs_list)
        featured_playlist_song_df
        #featured_playlist_song_df = add_audio_feats(featured_playlist_song_df)
        genre_df = get_genres(featured_playlist_song_df)
        genre_exploded_df = explode_genres(genre_df)
        featured_playlist_song_df = add_genres(featured_playlist_song_df, genre_exploded_df)
        featured_playlist_song_df = establish_genre_score(genre_count_df, featured_playlist_song_df)
        create_playlist(pred_like_playlist_name, featured_playlist_song_df, genre_threshold)
        printio('Complete! Check Spotify to see if playlist was filled with songs.')


        #subprocess.Popen(f"pyxtermjs -p 5001 --command python --cmd-args='create_playlist.py '{playlist_name}' '{genre_score_thresh}''", shell=True)
        # subprocess.run(f"python create_playlist.py '{playlist_name}' '{genre_score_thresh}'"
        #         ,shell=True
        #         ,stdout=subprocess.PIPE
        #         ,universal_newlines=True
        #         )
        # def inner():
        #         proc = subprocess.Popen(f"python -u create_playlist.py '{playlist_name}' '{genre_score_thresh}'"
        #         ,shell=True
        #         ,stdout=subprocess.PIPE
        #         ,universal_newlines=True
        #         )
        #         for line in iter(proc.stdout.readline,''):
        #             yield line.rstrip() + '<br/>\n'

        #     return Response(inner(), mimetype='text/html')
        
        
        # return 'ok'


    # define_scope()
    # try:
    #     pred_like_playlist_name = sys.argv[1]
    #     genre_threshold = sys.argv[2]
    # except:
    #     pred_like_playlist_name = 'test'
    #     genre_threshold = 20
    # print('pred_like_playlist_name = ',pred_like_playlist_name)
    # print('genre threshold = ',genre_threshold)
    # print('Scope defined\n****PART 1: Get Liked Songs Dataframe****\n')
        #time.sleep(2)
        #webbrowser.open('https://spotify-playlist-290119.uc.r.appspot.com:8081/',new=0)
        #subprocess.run('open localhost:8082/', shell=True)
    #return webbrowser.open('http://0.0.0.0:8082/',new=0)
    return 'ok'

if __name__ == '__main__':
    socketio.run(app)
    #,debug=True
