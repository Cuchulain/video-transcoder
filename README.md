# Video Transcoder

FFmpeg wrapper for automatically video parameters detect and transcoding

The script is designed to automatically transcode a movie for playback from a flash drive on a TV.

Based on the parameters set in the input file, it selects an audio stream in one of the preferred languages and adds "forced" subtitles in the same language if available.

If audio in the preferred language is not available, it selects the default audio and adds subtitles in one of the preferred languages.

If needed, it will reduce the number of audio channels and video resolution so that the TV can play it without stuttering or lagging.

## Configuration

In this version, all configuration parameters are defined in main script:

```python
PREFERRED_LANGUAGES_AUDIO = ['cze', 'slo']
PREFERRED_LANGUAGES_SUBTITLES = ['cze', 'slo']

LANGUAGE_NAMES = {
    'cze': 'Czech',
    'slo': 'Slovak',
    'eng': 'English',
}

ALLOWED_VIDEO_CODECS = ['h264', 'mpeg4', 'mp4', 'libx264']
FALLBACK_VIDEO_CODEC = 'h264_videotoolbox'

ALLOWED_AUDIO_CODECS = ['aac', 'ac3', 'mp3']
FALLBACK_AUDIO_CODEC = 'aac'

ALLOWED_SUBTITLE_CODECS = ['subrip', 'ass']
FALLBACK_SUBTITLE_CODEC = 'ass'

MAX_WIDTH = 1366
MAX_HEIGHT = 768
VIDEO_QUALITY = '-b:v 1200k' # or '-q:v 50' for example

OUTPUT_FILE_NAME_SUFFIX = 'recoded4tv'
OUTPUT_FILE_EXTENSION = 'mkv'
```

## Run script

```shell
python3 ./recode_video.py <input_file_path>
```

## Author

Jan Čejka

- GitHub: [@Cuchulain](https://github.com/Cuchulain)
- web: [jancejka.cz](https://jancejka.cz), [merguian.eth](http://merguian.eth)
