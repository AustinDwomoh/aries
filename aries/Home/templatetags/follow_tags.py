from django import template
from django.contrib.contenttypes.models import ContentType
from scripts import follow
register = template.Library()

@register.inclusion_tag('Home/follow_button.html', takes_context=True)
def render_follow_button(context, profile_obj, model_name):
    request = context['request']
    logged_in_entity = follow.get_logged_in_entity(request)

    is_following = follow.is_follower(logged_in_entity, profile_obj)
    is_blocked = follow.is_blocked(logged_in_entity, profile_obj) if hasattr(follow, 'is_blocked') else False
    is_pending = follow.is_pending(logged_in_entity, profile_obj) if hasattr(follow, 'is_pending') else False

    return {
        'request': request,
        'is_following': is_following,
        'is_blocked': is_blocked,
        'is_pending': is_pending,
        'profile_id': profile_obj.id,
        'model_name': model_name,
        'show_button': request.user.is_authenticated and request.user != profile_obj,
    }
    
@register.inclusion_tag("Home/follow_summary.html",takes_context=True)
def render_follow_summary(context,account, followers, following):
    
    if account.__class__.__name__.lower() == "user":
        model_name = 'user'
        rank = account.profile.stats.rank
    elif account.__class__.__name__.lower() == "clans":
        model_name = 'clan'
        rank = account.stat.rank
    return {
        'request': context['request'],
        "profile_id": account.id,
        "followers": followers,
        "following": following,
        "rank": rank,
        "target": account,
        "model_name": model_name
    }