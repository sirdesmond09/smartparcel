from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthBackend(object):
    """
        My custom authentication
        Authenticate using an e-mail address.
    """


    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        
            return None
        except User.DoesNotExist:
            return None
    
    def get_user(self, member_id):
        try:
            return User.objects.get(pk=member_id)
        except User.DoesNotExist:
            return None