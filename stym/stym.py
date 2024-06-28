#!/usr/bin/python3

import yaml
import argparse
import pexpect
import time

from yaml import CLoader as Loader
from stym.symbols import *
from stym import SpotifyToYouTubeMigrator
from stym.exception import (
    SongNotAddedException,
    SongNotFoundException
)
from spotipy import SpotifyException


def parse_arguments() -> argparse.ArgumentParser:
    """Parse command line arguments.

    Returns: Parsed arguments object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--authenticate",
        default=False,
        action="store_true",
        help="Authenticate with Google. Credentials will be deposited \
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
        help="Location of config YAML file. For reference read project README",
    )
    args = parser.parse_args()

    return args


def ytmusicapi_oauth() -> None:
    """Function for invoking the ytmusicapi shell utility for authenticattion."""
    command = "ytmusicapi oauth"
    child = pexpect.spawn(command)
    child.expect("abort")
    auth_string = f"{child.before.decode('utf-8')}{child.after.decode('utf-8')}"
    print(auth_string)
    child.interact()


def main() -> None:
    """Main method"""
    parsed_args = parse_arguments()

    if parsed_args.authenticate:
        ytmusicapi_oauth()
        return

    songs_not_found = []
    songs_not_added = []

    with open(parsed_args.config, "r") as fin:
        playlist_config = yaml.load(fin, Loader)

    spot_playlists = playlist_config["spotify"]["playlists"]
    yt_playlists = playlist_config["youtube"]["playlists"]
    if len(spot_playlists) != len(yt_playlists):
        print(
            "\nThe number of Spotify and YouTubeMusic playlists must match " + CROSS_MARK
        )
        return

    migrator = SpotifyToYouTubeMigrator(playlist_config, parsed_args.oauth_file)

    for index, playlist_id in enumerate(spot_playlists):
        try:
            tracks = migrator.get_spotify_playlist_tracks(playlist_id)
        except SpotifyException as e:
            print(e)
            print(LINE_MARKER + f" Error retrieving playlist {playlist_id} " + CROSS_MARK)
            continue

        print(LINE_MARKER + f" Retrieved Spotify playlist tracks " + CHECK_MARK)

        yt_playlist = yt_playlists[index]
        yt_playlist_id = migrator.create_yt_playlist(yt_playlist)

        print(
            LINE_MARKER
            + f" Adding tracks to YouTubeMusic playlist {yt_playlist} "
            + CLOCK
        )
        for track in tracks:
            time.sleep(1)
            try:
                migrator.add_to_yt_playlist(track, yt_playlist_id)
                print(PLUS_MARK + f" Added {track} " + CHECK_MARK)
            except SongNotFoundException:
                print(PLUS_MARK + f" Couldn't find {track} on YouTubeMusic " + CROSS_MARK)
                songs_not_found.append(track)
            except SongNotAddedException:
                print(PLUS_MARK + f" {track} could not be added " + CROSS_MARK)
                songs_not_added.append((yt_playlist, track))

        print(
            LINE_MARKER
            + f" Successfully migrated Spotify playlist {playlist_id} "
            + CHECK_MARK
        )

    if songs_not_found:
        print(LINE_MARKER + " The following song(s) could not be found on YouTubeMusic")
        for song in songs_not_found:
            print(song)

    if songs_not_added:
        print(
            LINE_MARKER
            + " The following song(s) couldn't be added to respective YouTubeMusic \
              playlist(s)"
        )
        for playlist, song in songs_not_added:
            print(f"Playlist: {playlist} | Song: {song}")


if __name__ == "__main__":
    main()
