from clans.models import Clans
from django.contrib.auth.models import User

def profile_picture_context(request):
    default_url = '/static/images/aries-1.png'
    profile_pic_url = default_url
    is_user_authenticated = False
    is_clan_authenticated = False

    try:
        if request.session.get('is_user'):
            user = User.objects.get(id=request.session.get('user_id'))
            if user.profile.profile_picture:
                profile_pic_url = user.profile.profile_picture.url
                print(profile_pic_url)
            is_user_authenticated = True

        elif request.session.get('is_clan'):
            clan = Clans.objects.get(id=request.session.get('clan_id'))
            if clan.clan_profile_pic:
                profile_pic_url = clan.clan_profile_pic.url
            is_clan_authenticated = True

    except Exception as e:
        pass

    return {
        'profile_pic_url': profile_pic_url,
        'is_user_authenticated': is_user_authenticated,
        'is_clan_authenticated': is_clan_authenticated
    }