from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from Home.models import Follow  
from clans.models import Clans  
from django.contrib.auth.models import User
from . import email_handle
import threading
from django.template.loader import render_to_string
def get_logged_in_entity(request):
    """
    Returns the logged-in user or clan instance based on session flags.
    Returns None if no valid login is found.
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
    """
    Retrieves and returns an instance of User or Clans based on model type string and ID.
    Raises ValueError if the model type is invalid.
    """
    model_map = {
        "clan": Clans,
        "user": User,
    }
    Model = model_map.get(followed_model.lower())
    if not Model:
        raise ValueError("Invalid followed model.")
    return get_object_or_404(Model, id=followed_id)

def follow(follower_instance, followed_instance, status='accepted'):
    """
    Creates or updates a follow relationship between follower and followed.
    Prevents self-follow and updates mutual status if reciprocal accepted follow exists.
    Returns the follow object and whether it was created.
    """
    if (follower_instance.__class__ == followed_instance.__class__ and follower_instance.id == followed_instance.id):
        raise ValueError("Cannot follow yourself.")#safeguard against self-follow 

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
        
    if created or follow_obj.status == 'accepted':
        send_follow_notification(follower_instance, followed_instance, action="followed")

    return follow_obj, created

def unfollow(follower_instance, followed_instance):
    """
    Deletes the follow relationship where follower follows followed.
    Returns the number of deleted objects.
    """
    send_follow_notification(follower_instance, followed_instance, action="unfollowed")
    return Follow.objects.filter(
        follower_content_type=ContentType.objects.get_for_model(follower_instance),
        follower_object_id=follower_instance.id,
        followed_content_type=ContentType.objects.get_for_model(followed_instance),
        followed_object_id=followed_instance.id
    ).delete()

def is_follower(follower_instance, followed_instance):
    """
    Checks if a follow relationship exists where follower follows followed.
    Returns True if exists, False otherwise.
    """
    return Follow.objects.filter(
        follower_content_type=ContentType.objects.get_for_model(follower_instance),
        follower_object_id=follower_instance.id,
        followed_content_type=ContentType.objects.get_for_model(followed_instance),
        followed_object_id=followed_instance.id
    ).exists()

def get_following(instance):
    """
    Returns a dict with lists of users and clans that the instance is following.
    """
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
    """
    Returns a dict with lists of users and clans that are following the instance.
    """
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

def accept_follow_request(followed_instance, follower_instance):
    """
    Accepts a pending follow request initiated by follower to followed.
    Updates mutual status if reciprocal accepted follow exists.
    Returns the updated follow object or None.
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
    """
    Returns all accepted follow records where instance is followed and notification is pending.
    """
    return Follow.objects.filter(
        followed_content_type=ContentType.objects.get_for_model(instance),
        followed_object_id=instance.id,
        notified=False,
        status='accepted'
    )



def send_follow_notification(follower_instance, followed_instance, action="followed"):
    """
    Sends an email notification to the followed entity.
    
    Args:
        follower_instance: The entity who followed/unfollowed.
        followed_instance: The entity receiving the notification.
        action: "followed" or "unfollowed"
    """
    recipient_email = getattr(followed_instance, 'email', None)
    if not recipient_email:
        return  # no email to send

    follow_name = getattr(follower_instance, 'username', None) or getattr(follower_instance, 'clan_name', None)

    html_content = render_to_string("home/follow_notify.html", {
        "follower_name": follow_name,
        "action": action
    })

    threading.Thread(
        target=email_handle.send_email_with_attachment,
        kwargs={
            "subject": f"You were {action}!",
            "body": f"{follow_name} has {action} you.",
            "to_email": recipient_email,
            "file_path": None,
            "from_email": None,
            "html_content": html_content
        }
    ).start()