from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.name = data.get('name') or ' '.join(
            filter(None, [
                data.get('first_name'),
                data.get('last_name')
            ])
        )
        return user