import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Tournament

@receiver(pre_delete, sender=Tournament)
def delete_json_file(sender, instance, **kwargs):
    """
    Signal handler that deletes the JSON file associated with a tournament instance 
    before the instance itself is deleted.

    This function is triggered when a `Tournament` instance 
    is about to be deleted. It retrieves the JSON file path from the instance and 
    attempts to delete it.

    Parameters:
        sender (Model): The model class that sent the signal (`Tournament`).
        instance (Model instance): The specific tournament instance being deleted.
        kwargs (dict): Additional keyword arguments.

    Behavior:
        - Retrieves the file path using `instance.get_json_file_path()`.
        - Attempts to remove the file.
        - Handles exceptions gracefully:
            - `FileNotFoundError`: If the file does not exist, the error is ignored.
    """
    file_path = instance.get_json_file_path()
    if os.path.exists(file_path):
        try:
            os.remove(file_path)  
        except FileNotFoundError:
            pass  
     
