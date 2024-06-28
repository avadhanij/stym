import spotipy
import requests
import functools

from stym.symbols import *
from ytmusicapi import YTMusic
from spotipy.oauth2 import SpotifyClientCredentials
from stym.exception import SongNotAddedException, SongNotFoundException


class SpotifyToYouTubeMigrator:
    """Class for managing credentials and migrating playlists from Spotify to YouTubeMusic"""

    def __init__(self, playlist_config, oauth_file_loc) -> None:
        """Init method. Initialize Spotify and YouTubeMusic connection clients"""
        spotify_client_id = playlist_config["spotify"]["client_id"]
        spotify_client_secret = playlist_config["spotify"]["client_secret"]

        session = requests.Session()
        session.request = functools.partial(session.request, timeout=60)
        self.yt_music = YTMusic(oauth_file_loc, requests_session=session)

        client_credentials_manager = SpotifyClientCredentials(
            spotify_client_id, spotify_client_secret
        )
        self.spotify = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager
        )

        yt_playlists = self.yt_music.get_library_playlists()
        self.yt_playlists = {
            playlist["title"]: playlist["playlistId"] for playlist in yt_playlists
        }

    def create_yt_playlist(self, playlist_title: str) -> str:
        """Wrapper method to create YouTubeMusic playlist. 
        Skips creation if playlist of same title already exists.
        
        Returns: YouTube playlist id
        """
        playlist_description = playlist_title

        playlist_id = self.yt_playlists.get(playlist_title)
        if playlist_id is None:
            playlist_id = self.yt_music.create_playlist(
                title=playlist_title, description=playlist_description
            )
            print(
                LINE_MARKER
                + f" Created new YouTube playlist {playlist_title}"
                + CHECK_MARK
            )
        else:
            print(LINE_MARKER + f" The YouTube playlist {playlist_title} already exists")

        return playlist_id

    def add_to_yt_playlist(self, song_name: str, tgt_playlist: str) -> None:
        """Method that searches for a given song and adds it to the given YT playlist."""
        search_results = self.yt_music.search(song_name, "songs") or self.yt_music.search(
            song_name, "videos"
        )
        added = False
        if search_results:
            retries = 3
            while retries != 0:
                try:
                    self.yt_music.add_playlist_items(
                        tgt_playlist, [search_results[0]["videoId"]]
                    )
                    retries = 0
                    added = True
                except Exception as e:
                    retries -= 1
        else:
            raise SongNotFoundException(song=song_name)

        if added is False:
            raise SongNotAddedException(song=song_name, playlist=tgt_playlist)

    def get_spotify_playlist_tracks(self, playlist_id: str) -> list:
        """Method that retrieves all the tracks in a Spotify playlist.
        
        Returns: List of songs in Spotify playlist
        """
        track_list = []

        playlist_info = self.spotify.user_playlist(user="", playlist_id=playlist_id)
        print(
            LINE_MARKER
            + f" Retrieving songs from Spotify playlist titled {playlist_info['name']} "
            + CLOCK
        )
        results = self.spotify.user_playlist_tracks(user="", playlist_id=playlist_id)

        tracks = results["items"]
        while results["next"]:
            results = self.spotify.next(results)
            tracks.extend(results["items"])

        for track in tracks:
            try:
                if track is None or track["track"] is None:
                    print("Missing track information.")
                # If artist info is missing, the song name is used as it's given
                elif track["track"]["artists"] is None:
                    print(f"{track['track']} has no artist information")
                    track_list.append(track["track"]["name"])
                # If there's only one artist, we add track_name - artist.
                elif len(track["track"]["artists"]) == 1:
                    track_list.append(
                        f"{track['track']['name']} - {track['track']['artists'][0]['name']}"
                    )
                # If there's more than one artist, we create a comma separated string of artists
                else:
                    artists = [artist["name"] for artist in track["track"]["artists"]]
                    name_string = ", ".join(artists)
                    track_list.append(f"{track['track']['name']} - {name_string}")
            except Exception as e:
                print(e)
                print(
                    f"Error retrieving the information of {track} from Spotify "
                    + CROSS_MARK
                )

        return track_list
