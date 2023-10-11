# Video Transcoder

The script is designed to automatically transcode a movie for playback from a flash drive on a TV using **FFmpeg**.

Based on the parameters set in the input file, it selects an audio stream in one of the preferred languages and adds "forced" subtitles in the same language if available.

If audio in the preferred language is not available, it selects the default audio and adds subtitles in one of the preferred languages.

If needed, it will reduce the number of audio channels and video resolution so that the TV can play it without stuttering or lagging.

## Dependencies

`ffmpeg` and `ffprobe` binaries installed in system path.

### Install Python libraries

`pip3 install -f requirements.txt`

## Configuration

The script reads the configuration from the `~/.video-transcoder.toml` file.
If the file does not exist, the script will create it and populate it with default values when it is first run.

## Run script

```shell
python3 ./recode_video.py <input_file_path>
```

## Author

Jan Čejka

- GitHub: [@Cuchulain](https://github.com/Cuchulain)
- web: [jancejka.cz](https://jancejka.cz), [merguian.eth](http://merguian.eth)
