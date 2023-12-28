import os

import toml

CONFIG_FILE_NAME = '.video-transcoder.toml'

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
    },
    'logging': {
        'to_console': True,
        'to_file': False,
        'file_path': 'recode.log',
        'format': '%(asctime)s [%(levelname)s] %(message)s',
        'level': 'ERROR',
    }
}


def get_values():
    home_directory = os.path.expanduser('~')
    full_path = os.path.join(home_directory, CONFIG_FILE_NAME)

    if not os.path.exists(full_path):
        toml.dump(DEFAULT_VALUES, open(full_path, 'w'))
        print("The configuration file was not found, a new one was created here: {}".format(full_path))

    parameters = toml.load(full_path)

    merged_parameters = merge_dicts(DEFAULT_VALUES, parameters)

    if parameters != merged_parameters:
        toml.dump(merged_parameters, open(full_path, 'w'))

    return merged_parameters


def merge_dicts(tgt, enhancer):
    for key, val in enhancer.items():
        if key not in tgt:
            tgt[key] = val
            continue

        if isinstance(val, dict):
            merge_dicts(tgt[key], val)
        else:
            tgt[key] = val
    return tgt
