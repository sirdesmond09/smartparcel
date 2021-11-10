from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .serializers import GoogleSocialAuthSerializer, FacebookSocialAuthSerializer
# from config.settings import SIMPLE_JWT

class GoogleSocialAuthView(GenericAPIView):

    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        """
        POST with "auth_token"
        Send an idtoken as from google to get user information
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        # refresh_token = data.pop('refresh')
        response= Response(data, status=status.HTTP_200_OK)
        # cookie_max_age = 120 * 60 * 60 #5days
        # response.set_cookie('refresh', refresh_token,expires=SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'),httponly=True, max_age=cookie_max_age, samesite='Lax')
        
        return response


class FacebookSocialAuthView(GenericAPIView):

    serializer_class = FacebookSocialAuthSerializer

    def post(self, request):
        """
        POST with "auth_token"
        Send an access token as from facebook to get user information
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        # refresh_token = data.pop('refresh')
        response= Response(data, status=status.HTTP_200_OK)
        # cookie_max_age = 120 * 60 * 60 #5 days
        # response.set_cookie('refresh', refresh_token,expires=SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'),httponly=True, max_age=cookie_max_age, samesite='Lax')
        
        return response

