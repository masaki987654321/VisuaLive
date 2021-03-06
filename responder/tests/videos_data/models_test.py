import pytest

from videos_data.models import VideoData

# DBへの保存ができるかのテスト
def test_valid_insert(having_no_data_session):
    videoData = VideoData(
        username = 'masaki',
        title = 'testだよ',
        broadcasted_at = '2020-09-13T14:15:18Z',
        url = 'https://www.twitch.tv/videos/739949384',
        channel_url = 'https://www.twitch.tv/videos/739949384',
        duration_minutes = 30,
        w_count = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        comment_count = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    )

    having_no_data_session.add(videoData)

    having_no_data_session.commit()
    
    result = having_no_data_session.query(VideoData).count()
    expected = 1
    assert result == expected
