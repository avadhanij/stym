#!/usr/bin/python3

import yaml
import argparse
import logging

from spotoytm import SpotifyToYouTubeMigrator
from spotoytm.exception import SongNotAddedException, SongNotFoundException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.ArgumentParser:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--authenticate",
        help="Authenticate with YouTubeMusic. Credentials will be deposited \
                        in a file called 'oath.json' in the current working directory",
    )
    parser.add_argument(
        "-o",
        "--oauth-file",
        default="oauth.json",
        help="Location of oauth.json file that's generated \
                        after the authenticate step.",
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Location of config YAML file. For reference read project README",
    )
    args = parser.parse_args()

    return args


def main():
    """Main method"""
    parsed_args = parse_arguments()

    songs_not_found = []
    songs_not_added = []

    with open(parsed_args.config, "r") as fin:
        playlist_config = yaml.load(fin)

    spot_playlists = playlist_config["spotify"]["playlists"]
    yt_playlists = playlist_config["youtube"]["playlists"]
    if len(spot_playlists) != len(yt_playlists):
        logger.error("The number of Spotify and YouTubeMusic playlists must match")
        return

    stym = SpotifyToYouTubeMigrator(playlist_config, parsed_args.oauth_file)

    for index, playlist_id in enumerate(spot_playlists):
        logger.info(f"Getting tracks of spotify playlist {playlist_id}")

        tracks = stym.get_spotify_playlist_tracks(playlist_id)
        logger.info(f"Retrieved playlist tracks")

        yt_playlist = yt_playlists[index]
        yt_playlist_id = stym.create_yt_playlist(yt_playlist)
        logger.info(f"Created YouTubeMusic playlist {yt_playlist}")
        logger.info(f"Adding tracks to YouTubeMusic playlist {yt_playlist}")

        for track in tracks:
            try:
                stym.add_to_yt_playlist(track, yt_playlist_id)
                logger.info(f"Added {track} to playlist")
            except SongNotFoundException:
                songs_not_found.append(track)
            except SongNotAddedException:
                songs_not_added.append(track)

        logger.info(f"Playlist {playlist_id} successfully migrated")


if __name__ == "__main__":
    main()
