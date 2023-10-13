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
import config
import iso639
import argparse


def get_ffmpeg_parameters(file_path, params):
    file_streams = get_file_metadata(file_path, 'streams')
    file_format = get_file_metadata(file_path, 'format')
    metadata = file_streams | file_format

    audios = {}
    subtitles = {}
    forced_subtitles = {}
    default_audio = None
    default_subtitles = None
    video = None
    index = 0

    recode_parameters = []

    for stream in metadata['streams']:

        if stream['codec_type'] == 'video' and (video is None or stream['disposition'].get('default')):
            video = index

        if stream['codec_type'] == 'audio':
            audios[get_stream_language(stream)] = index
            if default_audio is None:
                default_audio = index
            if stream['disposition'].get('default'):
                default_audio = index

        if stream['codec_type'] == 'subtitle':
            subtitles[get_stream_language(stream)] = index
            if stream['disposition']['forced'] or 'forced' in stream['tags'].get('title', '').lower():
                forced_subtitles[get_stream_language(stream)] = index
            if default_subtitles is None:
                default_subtitles = index
            if stream['disposition'].get('default'):
                default_subtitles = index

        index += 1

    recode_parameters.append("-map 0:{}".format(video))

    width = metadata['streams'][video]['width']
    height = metadata['streams'][video]['height']

    resize_video = False
    new_width = width
    new_height = height

    if height > params['dimensions']['max']['height']:
        resize_video = True
        new_height = params['dimensions']['max']['height']
        new_width = int(width * (new_height / height))

    if width > params['dimensions']['max']['width']:
        resize_video = True
        new_width = params['dimensions']['max']['width']
        new_height = int(height * (new_width / width))

    recode_video = resize_video

    if recode_video or metadata['streams'][video]['codec_name'] not in params['codecs']['video']['allowed']:
        recode_parameters.append("-c:v {} {}".format(
            params['codecs']['video']['fallback'],
            params['quality']['video']['parameter']
        ))
    else:
        recode_parameters.append("-c:v copy")

    if resize_video:
        recode_parameters.append("-filter:v scale={}:{}".format(new_width, new_height))

    audio_index = default_audio
    audio_lang = get_stream_language(metadata['streams'][default_audio])
    subtitles_index = None
    subtitles_lang = None
    audio_title = get_language_title(
        audio_lang,
        metadata['streams'][default_audio]
    )
    has_preferred_audio = False
    subtitles_title = None

    for lang in list(params['preferred_languages']['audio']):
        if lang in audios:
            audio_index = audios[lang]
            audio_lang = lang
            has_preferred_audio = True
            if audio_lang in forced_subtitles:
                subtitles_index = forced_subtitles[lang]
                subtitles_title = get_language_title(
                    lang,
                    metadata['streams'][subtitles_index]
                ) + ' (forced)'
            break

    if not has_preferred_audio and subtitles_index is None:
        for lang in list(params['preferred_languages']['subtitles']):
            if lang in subtitles and lang not in forced_subtitles:
                if lang != audio_lang:
                    subtitles_index = subtitles[lang]
                    subtitles_title = get_language_title(
                        lang,
                        metadata['streams'][subtitles_index]
                    )
                break

    if audio_index is not None:
        recode_parameters.append('-map 0:{} -metadata:s:a:0 title="{}"'
                                 .format(audio_index, audio_title))
        recode_audio = False

        if metadata['streams'][audio_index]['channels'] > 2:
            recode_parameters.append('-filter:a "pan=stereo|c0=c2+0.30*c0+0.30*c4|c1=c2+0.30*c1+0.30*c5"')
            recode_audio = True

        if recode_audio or metadata['streams'][audio_index]['codec_name'] not in params['codecs']['audio']['allowed']:
            recode_parameters.append("-c:a {}".format(params['codecs']['audio']['fallback']))
        else:
            recode_parameters.append("-c:a copy")

    if subtitles_index is not None:
        if subtitles_title is None:
            subtitles_title = get_language_title(
                subtitles_lang,
                metadata['streams'][subtitles_index]
            )

        recode_parameters.append('-map 0:{} -disposition:s:0 default -metadata:s:s:0 title="{}"'
                                 .format(subtitles_index, subtitles_title))

        if metadata['streams'][subtitles_index]['codec_name'] not in params['codecs']['subtitle']['allowed']:
            recode_parameters.append("-c:s {}".format(params['codecs']['subtitle']['fallback']))
        else:
            recode_parameters.append("-c:s copy")

    return " ".join(recode_parameters)


def get_stream_language(stream):
    try:
        return stream['tags']['language']
    except KeyError:
        return 'und'


def get_language_title(language, stream_info=None):
    default = language

    if stream_info is not None and 'title' in stream_info['tags']:
        default = stream_info['tags']['title']

    if default is None:
        default = language

    try:
        language_info = iso639.Language.from_part2b(language)
        return language_info.name
    except iso639.LanguageNotFoundError:
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
    parameters = config.get_values()

    parser = argparse.ArgumentParser(description='Recode video')

    parser.add_argument('-n', '--dry-run', action='store_true', help='Only display the command, don\'t recode')
    parser.add_argument('filename', type=str, help='Media file to recode')

    args = parser.parse_args()

    input_file = args.filename
    output_file = "{}-{}.{}".format(
        os.path.splitext(input_file)[0],
        parameters['files']['output']['suffix'],
        parameters['files']['output']['extension']
    )

    if not os.path.exists(input_file):
        print("File '{}' does not exist".format(input_file))
        exit(1)

    ffmpeg_parameters = get_ffmpeg_parameters(input_file, parameters['recoding'])
    ffmpeg_command = ('ffmpeg -i "{}" {} {} "{}"'
                      .format(input_file, ffmpeg_parameters, parameters['recoding']['extra'], output_file))

    print("\nCall this command:\n{}\n".format(ffmpeg_command))

    if not args.dry_run:
        os.system(ffmpeg_command)
