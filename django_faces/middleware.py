from django.conf import settings

from django_faces.settings import *

class XPavatar:
    def process_response(self, request, response):
        if response.status_code == 200:
            avatar_url = AUTHOR_AVATAR()
            if avatar_url:
                response['X-Pavatar'] = avatar_url
        return response

