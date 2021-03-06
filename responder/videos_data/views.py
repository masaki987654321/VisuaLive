import re

from apps.app import api, logger
from apps.base import ViewBase
from videos_data.exceptions import VideoNotFound
from videos_data.service import VideoDataService

class CreateChartView(ViewBase):
    def __init__(self):
        self.service = VideoDataService()

    async def on_post(self, req, resp):
        request = await req.media()

        # urlの確認の処理
        if re.fullmatch('https://www.twitch.tv/videos/\d{9}', request['url']) != None:
            video_type = 'twitch'
        elif re.fullmatch('https://www.youtube.com/watch\?v=[0-9A-Za-z-_]{11}', request['url']) != None:
            video_type = 'youtube'
        else:
            resp.html = api.template('homes/home.html', error_message='コメントの取得に失敗しました')
            return

        try:    
            video_data = self.service.get_video_data(request['url'], video_type)
            resp.html = api.template('videos_data/chart.html', video_data=video_data)
        except VideoNotFound:
            logger.warning('catch VideoNotFound')
            resp.html = api.template('homes/home.html', error_message='コメントの取得に失敗しました')            
