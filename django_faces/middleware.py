from django.conf import settings

class XPavatar:
    def __init__(self):
        self.author_avatar = None
        image = getattr(settings, 'AUTHOR_AVATAR', None)
        if image is not None:
            self.author_avatar = settings.MEDIA_URL + image

    def process_response(self, request, response):
        if response.status_code == 200:
            if self.author_avatar is not None:
                response['X-Pavatar'] = self.author_avatar
        return response

