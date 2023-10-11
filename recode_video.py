#!/usr/bin/env python3

"""
    File name: recode_video.py
    Author: Jan Čejka
    GitHub: https://github.com/Cuchulain/video-transcoder
    Email: posta@jancejka.cz
    Website: https://jancejka.cz
    Date created: 2023-10-09
    Date last modified: 2023-10-11
    Python Version: 3.9
"""

import json
import os
import pipes
import platform
import subprocess
import sys

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


def get_ffmpeg_parameters(file_path):
    file_streams = get_file_metadata(file_path, 'streams')
    file_format = get_file_metadata(file_path, 'format')
    metadata = file_streams | file_format

    audios = {}
    subtitles = {}
    forced_subtitles = {}
    default_audio = None
    video = None
    index = 0

    recode_parameters = []

    for stream in metadata['streams']:

        if stream['codec_type'] == 'video':
            video = index
            recode_parameters.append("-map 0:{}".format(index))

        if stream['codec_type'] == 'audio':
            audios[stream['tags']['language']] = index
            if default_audio is None:
                default_audio = index
            if stream['disposition']['default']:
                default_audio = index

        if stream['codec_type'] == 'subtitle':
            subtitles[stream['tags']['language']] = index
            if stream['disposition']['forced']:
                forced_subtitles[stream['tags']['language']] = index

        index += 1

    width = metadata['streams'][video]['width']
    height = metadata['streams'][video]['height']

    resize_video = False
    new_width = width
    new_height = height

    if height > MAX_HEIGHT:
        resize_video = True
        new_height = MAX_HEIGHT
        new_width = int(width * (new_height / height))

    if width > MAX_WIDTH:
        resize_video = True
        new_width = MAX_WIDTH
        new_height = int(height * (new_width / width))

    recode_video = resize_video

    if recode_video or metadata['streams'][video]['codec_name'] not in ALLOWED_VIDEO_CODECS:
        recode_parameters.append("-c:v {} {}".format(FALLBACK_VIDEO_CODEC, VIDEO_QUALITY))
    else:
        recode_parameters.append("-c:v copy")

    if resize_video:
        recode_parameters.append("-filter:v scale={}:{}".format(new_width, new_height))

    audio_index = default_audio
    audio_lang = metadata['streams'][default_audio]['tags']['language']
    subtitle_index = None
    audio_title = get_language_title(
        audio_lang,
        metadata['streams'][default_audio]
    )
    subtitle_title = None

    for lang in list(PREFERRED_LANGUAGES_AUDIO):
        if lang in audios:
            audio_index = audios[lang]
            audio_lang = lang
            if audio_lang in forced_subtitles:
                subtitle_index = forced_subtitles[lang]
                subtitle_title = get_language_title(
                    lang,
                    metadata['streams'][subtitle_index]
                ) + ' (forced)'
            break

    if subtitle_index is None:
        for lang in list(PREFERRED_LANGUAGES_SUBTITLES):
            if lang in subtitles and lang not in audios:
                subtitle_index = subtitles[lang]
                subtitle_title = get_language_title(
                    lang,
                    metadata['streams'][subtitle_index]
                )
                break

    if audio_index is not None:
        recode_parameters.append('-map 0:{} -metadata:s:a:0 title="{}"'
                                 .format(audio_index, audio_title))
        recode_audio = False

        if metadata['streams'][audio_index]['channels'] > 2:
            recode_parameters.append('-filter:a "pan=stereo|c0=c2+0.30*c0+0.30*c4|c1=c2+0.30*c1+0.30*c5"')
            recode_audio = True

        if recode_audio or metadata['streams'][audio_index]['codec_name'] not in ALLOWED_AUDIO_CODECS:
            recode_parameters.append("-c:a {}".format(FALLBACK_AUDIO_CODEC))
        else:
            recode_parameters.append("-c:a copy")

    if subtitle_index is not None:
        recode_parameters.append('-map 0:{} -disposition:s:0 default -metadata:s:s:0 title="{}"'
                                 .format(subtitle_index, subtitle_title))

        if metadata['streams'][subtitle_index]['codec_name'] not in ALLOWED_SUBTITLE_CODECS:
            recode_parameters.append("-c:s {}".format(FALLBACK_SUBTITLE_CODEC))
        else:
            recode_parameters.append("-c:s copy")

    parameters = " ".join(recode_parameters)

    return parameters


def get_language_title(language, stream_info=None):
    default = language

    if stream_info is not None and 'title' in stream_info['tags']:
        default = stream_info['tags']['title']

    if default is None:
        default = language

    if language in LANGUAGE_NAMES:
        return LANGUAGE_NAMES[language]
    else:
        return default


def get_file_metadata(file_path, section_type):
    cmd = get_command("ffprobe -show_{} -print_format json -hide_banner".format(section_type), file_path)

    metadata = json.loads(call_command(cmd))

    return metadata


def call_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    if p.returncode is not None:
        raise IOError("Error {}: {}".format(p.returncode, p.stderr.read()))

    return p.stdout.read()


def get_command(command, file_path):
    if str(platform.system()) == 'Windows':
        cmd = command.split(' ').append(file_path)
    else:
        cmd = [command + ' ' + pipes.quote(file_path)]

    return cmd


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <media_file>".format(os.path.basename(__file__)))
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = "{}-{}.{}".format(os.path.splitext(input_file)[0], OUTPUT_FILE_NAME_SUFFIX, OUTPUT_FILE_EXTENSION)

    ffmpeg_parameters = get_ffmpeg_parameters(input_file)
    ffmpeg_command = 'ffmpeg -i "{}" {} "{}"'.format(input_file, ffmpeg_parameters, output_file)

    print("\nCall this command:\n{}\n".format(ffmpeg_command))

    os.system(ffmpeg_command)
