import json
from flask import Flask, request, redirect, g, render_template, session
import requests
import base64
import urllib
import spotipy
import googlemaps
import datetime
import simplejson
from random import randint


# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.

app = Flask(__name__)
app.secret_key = 'asdjhu3ad3hu' #used to run sessions

#  Client Keys
CLIENT_ID = "b5c14ec1f7b64169bb063d7448a3453e"
CLIENT_SECRET = "32c71ce87d6242da85aae92bcaa78aee"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/")
def initPg():
    token_temp = 'BQBnWdfXbWhU_MFOJ0-Ti4dlmzjw6XIOy7jLhbllBGkyph1LA8saQ4sMWnusJ8NcPnMOyFNjYx8f9gdjk8CW3oxdxgu2_LSy5bkFhSTAFptot745tDkf27emtnT44-PfdembClUIfVujAFMnhXs7Z1SuuhUMrZzO30OZQXnJvkpO9OiPmItAkOXKxLelRpRTff0'
    spot = spotipy.Spotify(token_temp)
    genres = json.loads(spot.recommendation_genre_seeds())
    print(genres['genres'])
    

    return render_template("index.html")#, sorted_array = genres)

@app.route("/n")
def index():
    session['startplace'] = request.args.get("startplace")
    session['endplace'] = request.args.get("endplace")
    session['randomise'] = request.args.get("randomise")
    session['playlistname'] = request.args.get("playlistname")
    session['genre'] = request.args.get("genre")
    session['hated'] = request.args.get("hated")
    session['explicit'] = request.args.get("explicit")
    session['nonexplicit'] = request.args.get("nonexplicit")

    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}

    # code to do the thing
    #init gmap object
    gmaps = googlemaps.Client(key='AIzaSyBZdjs2225sM2jqaZJ_g37PanppIRcHBBU')
    travelTime = 0

    #get lat and long
    if session['startplace'] == "":
        startplace = 'london'
    else:
        startplace = session['startplace']
    if session['endplace'] == "":
        endplace = 'canterbury'
    else:
        endplace = session['endplace']
    
    geocode_result = gmaps.geocode(startplace)
    orig_lat_ne = geocode_result[0]['geometry']['bounds']['northeast']['lat']
    orig_lng_ne = geocode_result[0]['geometry']['bounds']['northeast']['lng']
    orig_lat_sw = geocode_result[0]['geometry']['bounds']['southwest']['lat']
    orig_lng_sw = geocode_result[0]['geometry']['bounds']['southwest']['lng']

    geocode_result = gmaps.geocode(endplace)
    end_lat_ne = geocode_result[0]['geometry']['bounds']['northeast']['lat']
    end_lng_ne = geocode_result[0]['geometry']['bounds']['northeast']['lng']
    end_lat_sw = geocode_result[0]['geometry']['bounds']['southwest']['lat']
    end_lng_sw = geocode_result[0]['geometry']['bounds']['southwest']['lng']

    orig_coord = midpoint(orig_lat_ne, orig_lng_ne, orig_lat_sw, orig_lng_sw)
    dest_coord = midpoint(end_lat_ne, end_lng_ne, end_lat_sw, end_lng_sw)

    #get travel distance
    url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins=" + str(orig_coord)[1:-1] + "&destinations=" + str(dest_coord)[1:-1] + "&mode=driving&language=en-EN&sensor=false"
    result = simplejson.load(urllib.urlopen(url))
    driving_time = result['rows'][0]['elements'][0]['duration']['value']


    #compile playlist
    sp = spotipy.Spotify(auth=access_token)
    genre =session['genre']
    results = sp.recommendations(seed_genres = genre)

    tracksToShow = [orig_coord, dest_coord, url, result, driving_time, results]
    

    return render_template("display.html",sorted_array=tracksToShow)

def midpoint(x1, y1, x2, y2):
    midpoint = 0
    x = abs(x1 - x2)
    x_final = (x/2) + min(x1, x2)

    y = abs(y1 - y2)
    y_final = (y/2) + min(y1, y2)

    midpoint = x_final, y_final
    return midpoint


if __name__ == "__main__":
    app.run(debug=True,port=PORT)
