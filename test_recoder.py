import recode_video


def test_recode_video():
    metadata = {
        'tags': {
            'title': 'test',
        }
    }

    assert recode_video.get_language_title('cze', metadata) == 'Czech'
    assert recode_video.get_language_title('slo', metadata) == 'Slovak'
    assert recode_video.get_language_title('eng', metadata) == 'English'
    assert recode_video.get_language_title('ger', metadata) == 'German'
    assert recode_video.get_language_title('xxx', metadata) == 'test'
