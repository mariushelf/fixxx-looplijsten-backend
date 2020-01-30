from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from api.users.models import User

def get_authenticated_client():
    '''
    Returns an authenticated APIClient, for unit testing API requests
    '''
    user = User.objects.create(email='foo@foo.com')
    access_token = RefreshToken.for_user(user).access_token

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))
    return client

def get_unauthenticated_client():
    '''
    Returns an unauthenticated APIClient, for unit testing API requests
    '''
    return APIClient()
