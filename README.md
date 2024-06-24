# Stym - Spotify To YoutubeMusic Migrator

# Motivation
I needed a tool that would migrate my existing playlists from Spotify to YouTubeMusic.

# Setup

## Spotify Credentials

1. Navigate to https://developer.spotify.com/dashboard/ and log into it using your Spotify credentials
2. Create an application by clicking on Create app.
3. Select WebAPI access checkbox. Redirect URI is not important and can be given any value.
4. Once created, retrieve and save the *Client ID* and *Client Secret* from the app settings page.

## YouTube Credentials

`stym` uses the Python library (ytmusicapi)[https://ytmusicapi.readthedocs.io/en/stable/index.html]. 
When installed, a shell Utility called `ytmusicapi` is installed, which is necessary for authentication.

This app provides a wrapper for invoking the `ytmusicapi` utility, which will be explained in the next section.

# Usage

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

Spotify playlist ids can be retrieved by navigating to the playlist in Spotify's web browser interface - https://open.spotify.com.
It's usually in the following form - https://open.spotify.com/playlist/Osdgif451we53. The last random ID after `playlist/` is the playlist ID.

> Recommendation: Migrate one playlist a time.

## Invocation


# Credit
Took inspiration from the project https://github.com/rimonhanna/Spotify-To-Youtube
