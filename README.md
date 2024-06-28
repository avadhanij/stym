# Stym - Spotify To YouTubeMusic Migrator

# Motivation
I wanted a command line based tool that would migrate my existing playlists from Spotify® to YouTubeMusic®.

# Installation

## PyPI

`pip install stym`

or

`pipx install stym`

# Setup

## Spotify Credentials

`stym` uses the Python library [spotipy](https://pypi.org/project/spotipy/) for interacting with Spotify's API.

1. Navigate to the [Spotify developer dashboard](https://developer.spotify.com/dashboard/) and log into it using your Spotify credentials
2. Create an application by clicking on Create app.
3. Select WebAPI access checkbox. Redirect URI is not important and can be given any value.
4. Once created, retrieve and save the *Client ID* and *Client Secret* from the app settings page.

## YouTube Credentials

`stym` uses the Python library [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/index.html). 
When installed, a shell utility called `ytmusicapi` is made available, which is necessary for authentication. 

More information https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html

`stym` provides a wrapper for invoking the `ytmusicapi` utility, which will be explained in the _Usage_ section.

## Config
Populate a file called `config.yaml` with any text editor, using values from prior steps
```
---
spotify:
  client_id: <spotify_client_id>
  client_secret: <spotify_client_secret>
  playlists:
    - spotify_playlist_1_id
    - spotify_playlist_2_id
    - spotify_playlist_3_id

youtube:
  playlists:
    - youtube_playlist_1_name
    - youtube_playlist_2_name
    - youtube_playlist_3_name
```
While regular names can be passed to the YouTube playlists section, Spotify requires playlist *IDs*. 

Spotify playlist ids can be retrieved by navigating to the playlist in Spotify's [web browser interface](https://open.spotify.com).
It's usually in the following form - https://open.spotify.com/playlist/Osdgif451we53. 

The random identifier right after `playlist/` is the playlist ID.

> Recommendation: Migrate one playlist a time for tracking which songs couldn't be found or added.

# Usage

## Step 1 - Google Authentication

This is a one time operation (needed again if credentials expire) to authenticate with Google. 

Invoke as follows

`stym -a`

The credentials are deposited in a file called `oauth.json`.

## Step 2 - Migration

Ensure that `config.yaml` is filled with necessary information and then `stym` can be invoked as follows.

`stym -o oauth.json -c config.yaml`

At the end, `stym` spits out any songs that it was either unable to find or add to YouTube playlist.

# Credit
Took inspiration from the project https://github.com/rimonhanna/Spotify-To-Youtube
