import os

import toml

CONFIG_FILE_NAME = 'video-transcoder.toml'

DEFAULT_VALUES = {
    'recoding': {
        'preferred_languages': {
            'audio': ['eng', 'cze', 'slo'],
            'subtitles': ['eng', 'cze', 'slo'],
        },
        'codecs': {
            'video': {
                'allowed': ['h264', 'mpeg4', 'mp4', 'libx264'],
                'fallback': 'libx264',
            },
            'audio': {
                'allowed': ['aac', 'ac3', 'mp3'],
                'fallback': 'aac',
            },
            'subtitle': {
                'allowed': ['subrip', 'ass'],
                'fallback': 'subrip',
            }
        },
        'dimensions': {
            'max': {
                'width': 1920,
                'height': 1080,
            }
        },
        'quality': {
            'video': {
                'parameter': '-b:v 3400k',  # or '-q:v 50' for example
            }
        },
        'extra': '',
    },
    'files': {
        'output': {
            'suffix': 'recoded4tv',
            'extension': 'mkv',
        }
    }
}


def get_values():
    home_directory = os.path.expanduser('~')
    full_path = os.path.join(home_directory, ".{}".format(CONFIG_FILE_NAME))

    if not os.path.exists(full_path):
        toml.dump(DEFAULT_VALUES, open(full_path, 'w'))
        print("The configuration file was not found, a new one was created here: {}".format(full_path))

    parameters = toml.load(full_path)

    merged_parameters = parameters | DEFAULT_VALUES

    if parameters != merged_parameters:
        toml.dump(merged_parameters, open(full_path, 'w'))

    return merged_parameters
