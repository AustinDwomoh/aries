from clans.models import Clans
from django.contrib.auth.models import User
from scripts.error_handle import ErrorHandler
from django.conf import settings
def profile_picture_context(request):
    """
    Context processor that provides profile picture URL and authentication status
    for either a logged-in user or a clan.

    It checks the session for 'is_user' or 'is_clan' flags and fetches the
    corresponding profile picture URL. If none is found, returns a default image URL.

    Returns:
        dict: Contains
            - 'profile_pic_url': URL string for the profile or clan picture (or default).
            - 'is_user_authenticated': Boolean flag if a user is authenticated.
            - 'is_clan_authenticated': Boolean flag if a clan is authenticated.
    """
    default_url = '/static/images/aries-1.png'
    profile_pic_url = default_url
    is_user_authenticated = False
    is_clan_authenticated = False

    try:
         # Check if the current session belongs to a regular user
        if request.session.get('is_user'):
            user = User.objects.get(id=request.session.get('user_id'))
            if user.profile.profile_picture:
                profile_pic_url = user.profile.profile_picture.url
            is_user_authenticated = True
        # Check if the current session belongs to a clan
        elif request.session.get('is_clan'):
            clan = Clans.objects.get(id=request.session.get('clan_id'))
            if clan.clan_profile_pic:
                profile_pic_url = clan.clan_profile_pic.url
            is_clan_authenticated = True
    except Exception as e:
        ErrorHandler().handle(e, context="Profile Picture Context Processor")

    return {
        'profile_pic_url': profile_pic_url,
        'is_user_authenticated': is_user_authenticated,
        'is_clan_authenticated': is_clan_authenticated
    }
    
def make_social_links_dict(social_links):
    """
    Converts a queryset of social links into a dictionary with icons and URLs.
    uses the constants defined in settings.SOCIAL_ICONS for icon HTML.
    Args:
        social_links (QuerySet): A queryset of SocialLink objects (with fields: name, url).
    
    Returns:
        dict: { "platform": {"url": url, "icon": icon_html}, ... }
    """
    result = {}
    for link in social_links:
        key = link.link_type.lower().strip()
        result[key] = {
            "url": link.url,
            "icon": settings.SOCIAL_ICONS.get(key, settings.SOCIAL_ICONS["other"])
        }
    return result