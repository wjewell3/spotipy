#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Project Overview: Create Relevant Spotify Playlist with New Songs
# 0. Declare name of playlist to be created
# 1. Import Packages and establish creds to connect to Spotify
# 2. Get raw Spotify data of Liked (Hearted) songs into a dataframe
# 3. Add audio features
# 4. Add genre data
# 5. Create genre score
### Repeat process (steps 2-5) for disliked songs (based on dislike playlist) ###
# 6. Create playlist df (to access disliked playlist)


# In[24]:


# 0. Declare name of playlist to be created
pred_like_playlist_name = "Genre_Score>0"


# In[3]:


#### ALL FUNCTIONS BELOW ####

# 1. Import Packages and establish creds to connect to Spotify
import os
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
import matplotlib.pyplot as plt  
import inspect
import pickle

def define_scope():
    global username
    username = os.environ['SPOTIPY_USERNAME']
    global scope 
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
    global token, sp, user, headers
    try:
        token = util.prompt_for_user_token(username, scope)
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope)
    sp = spotipy.Spotify(auth=token)
    user = sp.current_user()
    headers = {'Authorization': "Bearer {}".format(token)}
    return

# 2. Get raw Spotify data of Liked (i.e. Hearted) songs into a dataframe
# 2a. Get raw data of liked songs into a list
def req(url,headers):
    r = requests.get(url, headers=headers)
    return json.loads(r.text)

def get_raw_liked_song_list():
    print('Get_raw_liked_song_list')
    offset = 0
    url = f"https://api.spotify.com/v1/me/tracks?limit=50&offset={offset}"

    liked_song_count = req(url,headers=headers)["total"]
    print("Liked song count: ", liked_song_count)

    raw_liked_songs = []
    for i in range(int(math.ceil(liked_song_count/50.0))):
        offset = 50*i
        raw_liked_songs.extend(req(f"https://api.spotify.com/v1/me/tracks?limit=50&offset={offset}",headers=headers)["items"])

    print(f">> raw liked songs['0'] \n>> {raw_liked_songs[0]}")
    return raw_liked_songs

# 2b. transform liked song raw data list into df
# parse out data from Liked Songs' raw data
def song_metadata_to_df(raw_songs):
    print('Transforming song raw data list into df\n')
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
            print(f"{i}/{len(raw_songs)} parsed")
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
    print('Combining song_df with audio_feature_df')
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
    print('Getting genres\n')
    g = []
    artist_uris = df['artist_uri'].unique()
    print(len(artist_uris), ' distinct artists')
    for i in range(0, len(artist_uris)):
        if (i/100).is_integer():
            print(f"{i}/{len(artist_uris)} parsed")
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
    
    print('\ngenre_df')
    display(genres_df.head())
    return genres_df

# There is a list of genres for one artist that must be broken out
def explode_genres(df):
    genre_exploded_df = df.explode('genre list')
    
    print('\ngenre_exploded_df')
    display(genre_exploded_df.head())
    return genre_exploded_df

# Add these genres back to the df for each song
def add_genres(df, genre_exploded_df):
    # the following does not work oddly enough
    # liked_song_df.reset_index().merge(genre_exploded_df, on = 'artist_uri', how = 'left').set_index('uri', inplace = True)
    df = df.reset_index().merge(genre_exploded_df, on = 'artist_uri', how = 'left').set_index('uri')
    df.rename(columns={'genre list': 'genre'}, inplace=True)
    
    print('Merging genres into song_df')
    display(df.head())
    return df

#5. Create Genre Score

# Get genre counts for liked songs - the higher the count, the higher the score
def get_genre_counts(genre_exploded_df):
    print('Getting genre counts')
    # establish genre counts (which will determine score)
    genre_count_df = pd.DataFrame(genre_exploded_df['genre list'].value_counts()).reset_index()
    genre_count_df.columns = ['genre','genre count']
    print('\ngenre_count_df.head()')
    display(genre_count_df.head())
    return genre_count_df

# Merge the genre counts with the song df and sum the genre column
def establish_genre_score(genre_count_df, df):
    print('\nMerging genre counts with song_df')
    df = df.reset_index().merge(genre_count_df , on = 'genre',how = 'left')
    df.drop(columns=['genre'], inplace=True)
    display(df.head())

    groupby_cols = df.columns.to_list()[:-1]
    
    print('\nSumming genre column')
    df = df.groupby(groupby_cols).sum()
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
        playlist = playlists_raw['items'][i]['name']
        playlist_uri = playlists_raw['items'][i]['uri']
        song_count = playlists_raw['items'][i]['tracks']['total']
        df = df.append(pd.DataFrame([[playlist, playlist_uri, song_count]], columns = ['playlist','playlist_uri','song_count']))
    df.set_index(['playlist'], inplace=True)
    print('playlist_df')
    display(df)
    return df

def get_raw_disliked_song_list():
    playlists_raw = sp.current_user_playlists()
    playlists_df = get_playlist_uris(playlists_raw)
    uri =  playlists_df.loc['Dislikes']['playlist_uri']
    song_count =  playlists_df.loc['Dislikes']['song_count']
    # extract data from Disliked songs
    dislike_raw_list = []
    for i in range(int(math.ceil(song_count/100.0))):
        dislike_raw_list.extend(sp.user_playlist_tracks(uri.split(':')[1], uri.split(':')[2], offset=i*100)['items'])
    print('Getting raw disliked song list')
    return dislike_raw_list

# 7. Combine liked and disliked songs into my_songs dataframe with "Liked" flag
def combine_dfs_to_create_my_songs_df(df1,df2, save_destination):
    print('Combining dfs to create my_songs_df and storing as pickle file')
    df1['Liked'] = 1
    df2['Liked'] = 0
    my_songs_df = pd.concat([df1,df2])
    my_songs_df.to_csv(f"{save_destination}/my_songs.csv")
    my_songs_df.to_pickle("./my_songs.pkl")
    display(my_songs_df.head())
    print('successfully saved to .csv and .pkl files in save_destination')

# 8. Get featured playlist uris so we can get their associated songs
def get_featured_playlist_uris():
    print('Getting raw_featured_playlist_df')
    url = f"https://api.spotify.com/v1/browse/featured-playlists?limit=50&offset=0"
    featured_playlist_count = req(url,headers=headers)['playlists']['total']
    df = pd.DataFrame()
    for i in range(0,featured_playlist_count):
        raw_featured_playlist = req(url,headers=headers)
        playlist = raw_featured_playlist['playlists']['items'][i]['name']
        playlist_uri = raw_featured_playlist['playlists']['items'][i]['uri']
        song_count = raw_featured_playlist['playlists']['items'][i]['tracks']['total']
        df = df.append(pd.DataFrame([[playlist, playlist_uri, song_count]], columns = ['playlist','playlist_uri','song_count']))
    df.set_index(['playlist'], inplace=True)
    display(df)
    return df

# 9. Get raw data from the songs
def get_raw_featured_playlist_song_list():
    playlists_df = get_featured_playlist_uris()
    raw_featured_songs = []
    for uri in playlists_df.loc[:,'playlist_uri'].to_list():
        song_count = playlists_df.loc[playlists_df['playlist_uri']==uri,'song_count'][0]
        offset = 0
        url = f"https://api.spotify.com/v1/playlists/{uri.split(':')[2]}/tracks?limit=50&offset={offset}"
        for i in range(int(math.ceil(song_count/100.0))):
            offset = 100*i
            raw_featured_songs.extend(req(url,headers=headers)['items'])

    return raw_featured_songs

def create_playlist(pred_like_playlist_name, df, genre_score_threshold):
    playlists_raw = sp.current_user_playlists()
    playlists_df = get_playlist_uris(playlists_raw)
    playlist_uri = get_playlist_uris(playlists_raw).loc[playlists_df.index == pred_like_playlist_name,'playlist_uri'][0].split(':')[2]
    uri_list = df.loc[df['genre score']>= genre_score_threshold].reset_index()['uri'].to_list()
    num_songs_to_add = len(uri_list)
    for i in range(int(math.ceil(num_songs_to_add/100.0))):
        url = f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks?uris={','.join(uri_list[i*100:(i+1)*100])}"
        requests.post(url, headers=headers)
    return


# In[4]:


define_scope()
print('Scope defined\n****PART 1: Get Liked Songs Dataframe****\n')
raw_liked_song_list = get_raw_liked_song_list()
liked_song_df = song_metadata_to_df(raw_liked_song_list)
liked_song_df = add_audio_feats(liked_song_df)
genre_df = get_genres(liked_song_df)
genre_exploded_df = explode_genres(genre_df)
liked_song_df = add_genres(liked_song_df, genre_exploded_df)
liked_genre_count_df = get_genre_counts(genre_exploded_df)
liked_song_df = establish_genre_score(liked_genre_count_df, liked_song_df)
print('\n****PART 2: Get Disliked Songs Dataframe****\n')
define_scope()
raw_disliked_song_list = get_raw_disliked_song_list()
disliked_song_df = song_metadata_to_df(raw_disliked_song_list)
disliked_song_df = add_audio_feats(disliked_song_df)
genre_df = get_genres(disliked_song_df)
genre_exploded_df = explode_genres(genre_df)
disliked_song_df = add_genres(disliked_song_df, genre_exploded_df)
disliked_genre_count_df = get_genre_counts(genre_exploded_df)
disliked_genre_count_df['genre count'] = disliked_genre_count_df['genre count'] * -1
genre_count_df = pd.concat([liked_genre_count_df, disliked_genre_count_df])
disliked_song_df = establish_genre_score(disliked_genre_count_df, disliked_song_df)
print('\n****PART 3: Combine liked and disliked songs into my_songs dataframe with "Liked" flag and saving as .csv and pickle file***\n')
my_songs_df = combine_dfs_to_create_my_songs_df(liked_song_df,disliked_song_df,'/Users/Will/Documents/Spotipy')
print('\n****PART 4: Get songs from featured playlists and score them based on genre****\n')
raw_featured_playlist_songs_list = get_raw_featured_playlist_song_list()
featured_playlist_song_df = song_metadata_to_df(raw_featured_playlist_songs_list)
featured_playlist_song_df = add_audio_feats(featured_playlist_song_df)
genre_df = get_genres(featured_playlist_song_df)
genre_exploded_df = explode_genres(genre_df)
featured_playlist_song_df = add_genres(featured_playlist_song_df, genre_exploded_df)
featured_playlist_song_df = establish_genre_score(genre_count_df, featured_playlist_song_df)


# In[21]:


my_songs_df = pd.read_pickle("./my_songs.pkl")


# In[25]:


create_playlist(pred_like_playlist_name, featured_playlist_song_df, 1)


# In[ ]:


def get_uris(df):
    uri_list = df['uri'].tolist()
    return uri_list

def add_songs_to_playlist(uri_list, playlist_uri):
    df = pd.DataFrame()
    for uri in uri_list:
        url = f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks?uris={uri}"
        requests.post(url, headers=headers)
    return

def get_uris_raw(uri_list):
    uri_list_split = []
    for uri in uri_list:
        uri_list_split.append(uri.split(':')[2])
    return uri_list_split

