from django.conf import settings

from django_faces.settings import *

class XPavatar:
    def process_response(self, request, response):
        if response.status_code == 200:
            if AUTHOR_AVATAR is not None:
                response['X-Pavatar'] = AUTHOR_AVATAR
        return response

