class SongNotFoundException(Exception):
    """Exception class for not being able to find a song in YouTubeMusic"""

    def __init__(self, *args: object, **kwargs) -> None:
        self.song_name = kwargs["song"]
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"Could not find the song {self.song_name} on YouTubeMusic"


class SongNotAddedException(Exception):
    """Exception class for not being able to add a song to YouTubeMusic playlist"""

    def __init__(self, *args: object, **kwargs) -> None:
        self.song_name = kwargs["song"]
        self.playlist_name = kwargs["playlist"]
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"Could not add the song {self.song_name} to the YT playlist {self.playlist_name}"
