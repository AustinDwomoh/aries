from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from Home.models import Follow  
from clans.models import Clans  
from django.contrib.auth.models import User
from django import template
from django.contrib.contenttypes.models import ContentType
from collections import defaultdict

def get_logged_in_entity(request):
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


def get_profile_instance(profile_id):
    try:
        return Clans.objects.get(id=profile_id)
    except Clans.DoesNotExist:
        return get_object_or_404(User, id=profile_id)


def follow(follower_instance, followed_instance, status='accepted'):
    if type(follower_instance) == type(followed_instance) and follower_instance.id == followed_instance.id:
        raise ValueError("Cannot follow yourself.")

    follow_obj, created = Follow.objects.get_or_create(
        follower_content_type=ContentType.objects.get_for_model(follower_instance),
        follower_object_id=follower_instance.id,
        followed_content_type=ContentType.objects.get_for_model(followed_instance),
        followed_object_id=followed_instance.id,
        defaults={'status': status}
    )

    if not created and follow_obj.status != status:
        follow_obj.status = status
        follow_obj.save()

    # Handle is_mutual
    reverse = Follow.objects.filter(
        follower_content_type=ContentType.objects.get_for_model(followed_instance),
        follower_object_id=followed_instance.id,
        followed_content_type=ContentType.objects.get_for_model(follower_instance),
        followed_object_id=follower_instance.id,
        status='accepted'
    ).first()

    if reverse and status == 'accepted':
        follow_obj.is_mutual = True
        reverse.is_mutual = True
        follow_obj.save()
        reverse.save()

    return follow_obj, created



def unfollow(follower_instance, followed_instance):
    return Follow.objects.filter(
        follower_content_type=ContentType.objects.get_for_model(follower_instance),
        follower_object_id=follower_instance.id,
        followed_content_type=ContentType.objects.get_for_model(followed_instance),
        followed_object_id=followed_instance.id
    ).delete()


def is_follower(follower_instance, followed_instance):
    return Follow.objects.filter(
        follower_content_type=ContentType.objects.get_for_model(follower_instance),
        follower_object_id=follower_instance.id,
        followed_content_type=ContentType.objects.get_for_model(followed_instance),
        followed_object_id=followed_instance.id
    ).exists()


def get_following(instance):
    content_type = ContentType.objects.get_for_model(instance)
    follows = Follow.objects.filter(
        follower_content_type=content_type,
        follower_object_id=instance.id,
        status='accepted'
    )

    result = {"users": [], "clans": []}
    for f in follows:
        obj = f.followed
        if isinstance(obj, User):
            result["users"].append(obj)
        elif isinstance(obj, Clans):
            result["clans"].append(obj)

    return result


def get_followers(instance):
    content_type = ContentType.objects.get_for_model(instance)
    follows = Follow.objects.filter(
        followed_content_type=content_type,
        followed_object_id=instance.id,
        status='accepted'
    )
    result = {"users": [], "clans": []}

    for f in follows:
        obj = f.follower
        if isinstance(obj, User):
            result["users"].append(obj)
        elif isinstance(obj, Clans):
            result["clans"].append(obj)
    return result

def count_following(instance):
    content_type = ContentType.objects.get_for_model(instance)
    return Follow.objects.filter(
        follower_content_type=content_type,
        follower_object_id=instance.id,
        status='accepted'
    ).count()

def count_followers(instance):
    content_type = ContentType.objects.get_for_model(instance)
    return Follow.objects.filter(
        followed_content_type=content_type,
        followed_object_id=instance.id,
        status='accepted'
    ).count()

def block(follower_instance, followed_instance):
    return follow(follower_instance, followed_instance, status='blocked')


def accept_follow_request(followed_instance, follower_instance):
    """
    Accept a pending follow request.
    Note: follower_instance initiated the follow.
    """
    follow_obj = Follow.objects.filter(
        follower_content_type=ContentType.objects.get_for_model(follower_instance),
        follower_object_id=follower_instance.id,
        followed_content_type=ContentType.objects.get_for_model(followed_instance),
        followed_object_id=followed_instance.id,
        status='pending'
    ).first()

    if follow_obj:
        follow_obj.status = 'accepted'
        follow_obj.save()
        reverse = Follow.objects.filter(
            follower_content_type=ContentType.objects.get_for_model(followed_instance),
            follower_object_id=followed_instance.id,
            followed_content_type=ContentType.objects.get_for_model(follower_instance),
            followed_object_id=follower_instance.id,
            status='accepted'
        ).first()

        if reverse:
            follow_obj.is_mutual = True
            reverse.is_mutual = True
            follow_obj.save()
            reverse.save()

        return follow_obj

    return None


def get_unnotified_follows_for(instance):
    return Follow.objects.filter(
        followed_content_type=ContentType.objects.get_for_model(instance),
        followed_object_id=instance.id,
        notified=False,
        status='accepted'
    )



