from django.contrib.contenttypes.models import ContentType
from Home.models import Follow  
from clans.models import Clans
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

def get_logged_in_entity(request):
    """
    Returns the currently logged-in entity (User or Clan)
    based on session flags.
    """
    if request.session.get('is_user'):
        return request.user
    elif request.session.get('is_clan'):
        try:
            return Clans.objects.get(id=request.session.get('clan_id'))
        except Clans.DoesNotExist:
            
            request.session.pop('clan_id', None)
            request.session.pop('is_clan', None)
            return None
    return None  

def get_followed_instance(followed_model, followed_id):
    model_map = {
        "clan": Clans,
        "user": User,
    }
    Model = model_map.get(followed_model.lower())
    if not Model:
        raise ValueError("Invalid followed model.")
    return get_object_or_404(Model, id=followed_id)

def get_following(instance):
    """
    Returns a queryset of all objects that the given instance is following.

    Args:
        instance (Model): A model instance (e.g., User or Clan).

    Returns:
        QuerySet[Follow]: All Follow relationships where the instance is the follower.
    """
    ctype = ContentType.objects.get_for_model(instance.__class__)
    return Follow.objects.filter(follower_type=ctype, follower_id=instance.id)


def get_followers(instance):
    """
    Returns a queryset of all objects following the given instance.

    Args:
        instance (Model): A model instance (e.g., User or Clan).

    Returns:
        QuerySet[Follow]: All Follow relationships where the instance is being followed.
    """
    ctype = ContentType.objects.get_for_model(instance.__class__)
    return Follow.objects.filter(followed_type=ctype, followed_id=instance.id)

def count_following(instance):
    """
    Returns the count of how many objects the instance is following.
    """
    return get_following(instance).count()

def count_followers(instance):
    """
    Returns the count of how many followers the instance has.
    """
    return get_followers(instance).count()

def is_follower(follower_instance, followed_instance):
    """
    Checks if the follower_instance is following the followed_instance.

    Returns:
        bool: True if following, False otherwise.
    """
    return Follow.objects.filter(
        follower_type=ContentType.objects.get_for_model(follower_instance.__class__),
        follower_id=follower_instance.id,
        followed_type=ContentType.objects.get_for_model(followed_instance.__class__),
        followed_id=followed_instance.id
    ).exists()

def follow(follower_instance, followed_instance):
    """
    Creates a follow relationship if it doesn't exist.

    Returns:
        Tuple[Follow, bool]: (Follow instance, created True/False)
    """
    if (
        type(follower_instance) == type(followed_instance)
        and follower_instance.id == followed_instance.id
    ):
        raise ValueError("Cannot follow yourself.")

    return Follow.objects.get_or_create(
        follower_type=ContentType.objects.get_for_model(follower_instance.__class__),
        follower_id=follower_instance.id,
        followed_type=ContentType.objects.get_for_model(followed_instance.__class__),
        followed_id=followed_instance.id
    )

def unfollow(follower_instance, followed_instance):
    """
    Deletes the follow relationship between the two instances if it exists.

    Returns:
        Tuple[int, dict]: (Number of deletions, deletion details)
    """
    return Follow.objects.filter(
        follower_type=ContentType.objects.get_for_model(follower_instance.__class__),
        follower_id=follower_instance.id,
        followed_type=ContentType.objects.get_for_model(followed_instance.__class__),
        followed_id=followed_instance.id
    ).delete()