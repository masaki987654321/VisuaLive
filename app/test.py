import json

import pytest

from twitch import TwitchVideo

@pytest.fixture()
def video():
    return TwitchVideo('https://www.twitch.tv/videos/739949384')


class TestTwitch:
    def test_init(self, video):
        with open('config.json', 'r') as f:
            config = json.load(f)

        assert video.video_id == '739949384'
        assert video.client_id == config['twitch']['client_id']
        assert video.client_secret == config['twitch']['client_secret']
        assert video.app_access_token == config['twitch']['app_access_token']


    def test_get_info(self, mocker, video):
        res_mock = mocker.Mock()
        res_mock.status_code = 200
        with open('get_info.json') as f:
            res_mock.text = f.read()

        mocker.patch('requests.get').return_value = res_mock

        video_info = video.get_info()
        assert 'user_name' in video_info
        assert 'title' in video_info
        assert 'created_at' in video_info
        assert 'url' in video_info
        assert 'duration_minutes' in video_info
        assert type(video_info['duration_minutes']) is int


    # ------実際にtwitch apiを叩くテスト----------
    # def test_get_info_real_api(self, video):
    #     video_info = video.get_info()
    #     assert 'user_name' in video_info
    #     assert 'title' in video_info
    #     assert 'created_at' in video_info
    #     assert 'url' in video_info
    #     assert 'duration_minutes' in video_info
    #     assert type(video_info['duration_minutes']) is int
    # -----------------------------------------------------


    # app_access_tokenの期限が切れて、無効になっていた場合のテスト
    def test_get_info_with_invalid_token(self, mocker, video):
        res_mock = mocker.Mock()
        res_mock.status_code = 404
        res_mock.text = '{"error": "Unauthorized", "status": 401, "message": "Invalid OAuth token"}'

        mocker.patch('requests.get').return_value = res_mock

        # todo requestsが投げる例外の正体がわからない
        with pytest.raises(Exception):
            video.get_info()


    def test_get_token(self, mocker, video):
        with open('config.json', 'r') as f:
            config = json.load(f)

        get_token_mock = mocker.Mock()
        get_token_mock.status_code = 200
        get_token_mock.text = '{"access_token": "sample_token_for_test", "expires_in": 5669710, "token_type": "bearer"}'

        mocker.patch('requests.post').return_value = get_token_mock

        video._get_token()
        assert video.app_access_token == 'sample_token_for_test'

        # テスト用に変更したtokenを元に戻す
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        # テスト用に変更したtokenが元に戻っているか確認
        # assert video.app_access_token == config['twitch']['app_access_token']


    # ------実際にtwitch apiを叩くテスト----------
    # def test_get_token_real_api(self, mocker, video):
    #     with open('config.json', 'r') as f:
    #         config = json.load(f)

    #     video.get_token()
    #     assert video.app_access_token != config['twitch']['app_access_token']   
    # -------------------------------------------------


    # def test_get_comments(self, video):
    #     video.get_token()
    #     assert 'comment_count' in video.get_comments