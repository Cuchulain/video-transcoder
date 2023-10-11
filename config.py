import os

import toml

PATH = 'video-transcoder.toml'

DEFAULT_VALUES = {
    'recoding': {
        'preferred_languages': {
            'audio': ['eng', 'cze', 'slo'],
            'subtitles': ['eng', 'cze', 'slo'],
        },
        'codecs': {
            'video': {
                'allowed': ['h264', 'mpeg4', 'mp4', 'libx264'],
                'fallback': 'h264_videotoolbox',
            },
            'audio': {
                'allowed': ['aac', 'ac3', 'mp3'],
                'fallback': 'aac',
            },
            'subtitle': {
                'allowed': ['subrip', 'ass'],
                'fallback': 'ass',
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
                'parameter': '-b:v 1200k',  # or '-q:v 50' for example
            }
        },
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
    full_path = os.path.join(home_directory, ".{}".format(PATH))

    if not os.path.exists(full_path):
        toml.dump(DEFAULT_VALUES, open(full_path, 'w'))

    return toml.load(full_path)
