import json

import pytest

from videos_data.external import TwitchVideo
from videos_data.exceptions import VideoNotFound

@pytest.fixture()
def video():
    return TwitchVideo('https://www.twitch.tv/videos/739949384')


class TestInit:
    def test_init(self, video):
        with open('config/external.json', 'r') as f:
            config = json.load(f)

        assert video.video_id == '739949384'
        assert video.client_id == config['twitch']['client_id']
        assert video.client_secret == config['twitch']['client_secret']
        assert video.app_access_token == config['twitch']['app_access_token']


class TestGetInfo:
    # twithcから動画情報を取得し、正しく加工できているかのテスト
    def test_get_info(self, mocker, video):
        res_mock = mocker.Mock()
        res_mock.status_code = 200
        with open('tests/json/video_info.json') as f:
            res_mock.text = f.read()

        mocker.patch('requests.get').return_value = res_mock

        video_info = video._get_info()
        assert 'user_name' in video_info
        assert 'title' in video_info
        assert 'created_at' in video_info
        assert 'url' in video_info
        assert 'channel_url' in video_info
        assert 'duration_minutes' in video_info
        assert type(video_info['duration_minutes']) is int

    # 実際にtwitch apiを叩き、twithcから動画情報を取得し、正しく加工できているかのテスト
    # def test_get_info_real_api(self, video):
    #     video_info = video._get_info()
    #     assert 'user_name' in video_info
    #     assert 'title' in video_info
    #     assert 'created_at' in video_info
    #     assert 'url' in video_info
    #     assert 'channel_url' in video_info
    #     assert 'duration_minutes' in video_info
    #     assert type(video_info['duration_minutes']) is int


    # app_access_tokenの期限が切れていて、tokenの再取得を行う場合のテスト
    def test_get_info_with_invalid_token(self, mocker, video):
        # 無効なトークンで動画情報を取得しようとした場合のモック
        error_res_mock = mocker.Mock()
        error_res_mock.status_code = 401
        error_res_mock.text = '{"error": "Unauthorized", "status": 401, "message": "Invalid OAuth token"}'
        # 有効なトークンで動画情報を取得しようとした場合のモック
        ok_res_mock = mocker.Mock()
        ok_res_mock.status_code = 200
        with open('tests/json/video_info.json') as f:
            ok_res_mock.text = f.read()

        mocker.patch('requests.get').side_effect = [error_res_mock, ok_res_mock]

        # 新しいトークンを取得する処理のモック
        with open('config/external.json', 'r') as f:
            config = json.load(f)
        get_token_mock = mocker.Mock()
        get_token_mock.status_code = 200
        get_token_mock.text = '{"access_token": "' + config['twitch']['app_access_token'] + '", "expires_in": 5669710, "token_type": "bearer"}'
        
        mocker.patch('requests.post').return_value = get_token_mock

        video_info = video._get_info()

        assert 'user_name' in video_info
        assert 'title' in video_info
        assert 'created_at' in video_info
        assert 'url' in video_info
        assert 'channel_url' in video_info
        assert 'duration_minutes' in video_info
        assert type(video_info['duration_minutes']) is int


    # 動画が削除、公開終了していて、動画情報を取得できない場合のテスト
    def test_get_info_video_not_fount(self, mocker, video):
        res_mock = mocker.Mock()
        res_mock.status_code = 404
        res_mock.text = '{"error": "Not Found", "status": 404, "message": "vods not found"}'
        mocker.patch('requests.get').return_value = res_mock

        with pytest.raises(VideoNotFound):
            video._get_info()

class TestGetToken:
    def test_get_token(self, mocker, video):
        with open('config/external.json', 'r') as f:
            config = json.load(f)

        get_token_mock = mocker.Mock()
        get_token_mock.status_code = 200
        get_token_mock.text = '{"access_token": "sample_token_for_test", "expires_in": 5669710, "token_type": "bearer"}'

        mocker.patch('requests.post').return_value = get_token_mock

        video._get_token()
        assert video.app_access_token == 'sample_token_for_test'

        # テスト用に変更したtokenを元に戻す
        with open('config/external.json', 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


    # 実際にtwitch apiを叩いてtokenを取得するテスト
    # def test_get_token_real_api(self, mocker, video):
    #     with open('config/external.json', 'r') as f:
    #         config = json.load(f)

    #     video._get_token()
    #     assert video.app_access_token != config['twitch']['app_access_token']   


class TestGetCommentData:
    # 動画のコメントを取得し、正しく加工できているかのテスト
    def test_get_comment_data(self, mocker, video):
        # コメント取得のモック(_nextあり)
        with_next_mock = mocker.Mock()
        with_next_mock.status_code = 200
        with open('tests/json/twitch_comment_with_next.json') as f:
            with_next_mock.text = f.read()
        # コメント取得のモック（_nextなし）
        without_next_mock = mocker.Mock()
        without_next_mock.status_code = 200
        with open('tests/json/twitch_comment_without_next.json') as f:
            without_next_mock.text = f.read()

        mocker.patch('requests.get').side_effect = [with_next_mock, without_next_mock]

        comment_data = video._get_comment_data()
        assert sum(comment_data['comment_count']) == 84
        assert type(comment_data['w_count'][0]) is int


    # 実際にtwitch apiを叩き、動画のコメントを取得し、正しく加工できているかのテスト
    # def test_get_comments_real_api(self, video):
    #     comment_data = video._get_comment_data()
    #     assert sum(comment_data['comment_count']) == 84
    #     assert type(comment_data['w_count'][0]) is int


class TestGetData:
    def test_get_data(self, mocker, video):
        # 動画情報取得のモック
        get_info_mock = mocker.Mock()
        get_info_mock.status_code = 200
        with open('tests/json/video_info.json') as f:
            get_info_mock.text = f.read()
        # コメント取得のモック(_nextあり)
        with_next_mock = mocker.Mock()
        with_next_mock.status_code = 200
        with open('tests/json/twitch_comment_with_next.json') as f:
            with_next_mock.text = f.read()
        # コメント取得のモック（_nextなし）
        without_next_mock = mocker.Mock()
        without_next_mock.status_code = 200
        with open('tests/json/twitch_comment_without_next.json') as f:
            without_next_mock.text = f.read()

        mocker.patch('requests.get').side_effect = [get_info_mock, with_next_mock, without_next_mock]

        video_data = video.get_data()
        assert 'user_name' in video_data
        assert 'title' in video_data
        assert 'broadcasted_at' in video_data
        assert 'url' in video_data
        assert 'channel_url' in video_data
        assert 'duration_minutes' in video_data
        assert 'comment_count' in video_data
        assert 'w_count' in video_data


