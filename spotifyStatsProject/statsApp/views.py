from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os


@csrf_exempt
def index(request):
    """
    View to authenticate the users Spotify account, get the time period (short, medium or long term) and
    fetch the corresponding users top tracks.
    """

    # Import Spotify Client ID and Client Secret environment variables
    SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
    SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']

    # Define Scope and Redirect URI
    SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:9090'

    # Using 'user-top-read' scope as stated in Spotify's documentation:
    # 'Read access to a user's top artists and tracks'
    SCOPE = 'user-top-read'

    # Get the POST variable time to see whether user wants short, medium or long term tracks.
    if request.POST.get("time"):
        time = request.POST.get("time")
    else:
        # If none selected, default to short term
        time = "short_term"

    # Get authorisation from users Spotify account
    auth = SpotifyOAuth(scope=SCOPE,
                        client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        cache_path=".spotifycache")

    sp = spotipy.Spotify(auth_manager=auth)

    # Get the users top 50 tracks.
    results = sp.current_user_top_tracks(limit=50, time_range=time)

    track_ids = getTrackIDs(results)

    # Iterate over each track ID and get the track info
    all_tracks = []
    for track_id in track_ids:

        track_info = get_track_features(track_id, sp)
        all_tracks.append(track_info)

    context = {'tracks': all_tracks, 'time':time}
    print(context)

    return render(request, 'index.html', context=context)


def getTrackIDs(time_frame):
    """
    Function to iterate over users top songs and return a list of their IDs
    """

    track_ids = []
    for song in time_frame['items']:
        track_ids.append(song['id'])
    return track_ids


def get_track_features(id, sp):
    """
    Function which given a track ID will return the tracks info, including name, artist, URL and album cover
    """

    song = sp.track(id)
    name = song['name']
    album = song['album']['name']
    artist = song['album']['artists'][0]['name']
    spotify_url = song['external_urls']['spotify']
    album_cover = song['album']['images'][0]['url']
    track_info = [name, album, artist, spotify_url, album_cover]
    return track_info
