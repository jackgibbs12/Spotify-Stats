from django.http import HttpResponse
from django.shortcuts import render
import spotipy
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from spotipy.oauth2 import SpotifyOAuth
import os


@csrf_exempt
def index(request):
    print(request.POST.get("time"))
    SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
    SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
    SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:9090'
    SCOPE = 'user-top-read'

    if request.POST.get("time"):
        time = request.POST.get("time")
    else:
        time = "short_term"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE))
    results = sp.current_user_top_tracks(limit=50, time_range=time)

    def getTrackIDs(time_frame):
        track_ids = []
        for song in time_frame['items']:
            track_ids.append(song['id'])
        return track_ids

    track_ids = getTrackIDs(results)

    def get_track_features(id):
        meta = sp.track(id)
        # meta
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        spotify_url = meta['external_urls']['spotify']
        album_cover = meta['album']['images'][0]['url']
        track_info = [name, album, artist, spotify_url, album_cover]
        return track_info

    all_tracks = []
    for track_id in track_ids:
        all_tracks.append(get_track_features(track_id))
        context = {'tracks': all_tracks}

    return render(request, 'index.html', context=context)
