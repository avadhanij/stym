import spotipy
import requests
import functools
import logging

from ytmusicapi import YTMusic
from spotipy.oauth2 import SpotifyClientCredentials
from spotoytm.exception import SongNotAddedException, SongNotFoundException

logger = logging.getLogger(__name__)


class SpotifyToYouTubeMigrator:
    """Class for managing credentials and migrating playlists from Spotify to YouTubeMusic
    """

    def __init__(self, playlist_config, oauth_file_loc):
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

    def create_yt_playlist(self, playlist_title:str, playlist_description=None) -> str:
        """Wrapper method to create YouTubeMusic playlist. Skips creation if playlist of same title already exists."""
        if playlist_description is None:
            playlist_title = playlist_title

        existing_playlists = self.yt_music.get_library_playlists()
        for playlist in existing_playlists:
            if playlist["title"] == playlist_title:
                logger.info(f"The playlist {playlist_title} already exists")
                return

        return self.yt_music.create_playlist(
            title=playlist_title, description=playlist_description
        )

    def add_to_yt_playlist(self, song_name: str, tgt_playlist: str):
        """Method that searches for a given song and adds it to the given YT playlist.
        """
        search_results = self.yt_music.search(
            song_name, "songs"
        ) or self.yt_music.search(song_name, "videos")
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
                    logger.error(f"An exception occurred: {e}")
                    retries -= 1
        else:
            raise SongNotFoundException(song_name=song_name)

        if not added:
            raise SongNotAddedException(song_name=song_name, playlist=tgt_playlist)

    def get_spotify_playlist_tracks(self, playlist_id: str) -> list:
        """Method that retrieves all the tracks in a Spotify playlist"""
        track_list = []

        results = self.spotify.user_playlist_tracks(user="", playlist_id=playlist_id)

        tracks = results["items"]
        while results["next"]:
            results = self.spotify.next(results)
            tracks.extend(results["items"])

        for track in tracks:
            try:
                if track is None or track["track"] is None:
                    print(track)
                elif track["track"]["artists"] is None:
                    print(track["track"])
                    track_list.append(track["track"]["name"])
                # In case there's only one artist, we add trackName - artist.
                elif len(track["track"]["artists"]) == 1:
                    track_list.append(
                        f"{track["track"]["name"]} - {track["track"]["artists"][0]["name"]}"
                    )
                # In case there's more than one artist, we create a comma separated string of artists
                else:
                    name_string = ", ".join(track["track"]["artists"])
                    track_list.append(f"{track["track"]["name"]} - {name_string}")
            except Exception as e:
                print("An exception occurred:", e)

        return track_list
