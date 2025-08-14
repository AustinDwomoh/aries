from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User,AbstractBaseUser, BaseUserManager, PermissionsMixin,Group, Permission
import os, json
from scripts.error_handle import ErrorHandler
from PIL import Image
from django.conf import settings

# Custom manager for Clans, mimicking UserManager pattern
class ClanManager(BaseUserManager):
    def create_clan(self, name, password=None, **extra_fields):
        if not name:
            raise ValueError('Clans must have a name')
        clan = self.model(clan_name=name, **extra_fields)
        clan.set_password(password)# Uses hashing method
        clan.save(using=self._db)
        return clan

class Clans(AbstractBaseUser, PermissionsMixin):
    """
    Clan model acting as a User substitute for clans.
    Stores clan info, login credentials, social links, recruiting status, etc.
    Inherits Django's AbstractBaseUser for auth compatibility.
    """
    clan_name = models.CharField(max_length=255, unique=True)
    clan_tag = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    clan_description = models.TextField()
    clan_logo = models.ImageField(default="areis-1.png", upload_to='clan_logos')
    clan_profile_pic = models.ImageField(default="areis-2.jpg", upload_to='clan_profile')
    clan_website = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    primary_game = models.CharField(max_length=255, blank=True, null=True)
    other_games = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50)  
    is_recruiting = models.BooleanField(default=False)
    recruitment_requirements = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True,unique=True)
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Django auth-required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'clan_name'
    REQUIRED_FIELDS = ['email']
    objects = ClanManager()
    
    # Permissions and groups fields override for clans as "users"
    groups = models.ManyToManyField(Group,related_name='clan_set',  blank=True,help_text='The groups this clan belongs to.',related_query_name='clan',)
    user_permissions = models.ManyToManyField(Permission,related_name='clan_permissions_set',  blank=True,help_text='Specific permissions for this clan.',related_query_name='clan',)

    class Meta:
        verbose_name = "Clan"
        verbose_name_plural = "Clans"

    def set_password(self, raw_password):
        """Hash and store the password."""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Check the provided password against the stored hash."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.clan_name}"
    
    def save(self, *args, **kwargs): 
        """Resize profile pic on save if bigger than 300x300."""
        super().save(*args, **kwargs)
        if self.clan_profile_pic:
            img = Image.open(self.clan_profile_pic.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.clan_profile_pic.path)
       
class ClanStats(models.Model):
    """
    Tracks clan performance metrics.
    Linked to Clans via one-to-one.
    Stores wins/losses, ELO rating, rankings, match data JSON.
    """
    clan = models.OneToOneField(Clans, on_delete=models.CASCADE,related_name='stat')
    total_matches = models.IntegerField(default=0, editable=False)
    win_rate = models.FloatField(default=0.0, editable=False)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_draws = models.IntegerField(default=0)
    RANK_CHOICES = [('bronze', 'Bronze'),('silver', 'Silver'),('gold', 'Gold'),('platinum', 'Platinum'),('diamond', 'Diamond'),('master', 'Master'),('grandmaster', 'Grandmaster'),('champion', 'Champion'),('invincible', 'Invincible'),]
    rank = models.CharField(max_length=20,choices=RANK_CHOICES,blank=True,null=True,editable=False)
    player_scored = models.IntegerField(default=0)
    player_conceeded = models.IntegerField(default=0)
    gd = models.IntegerField(default=0) # Goal difference 
    gf = models.IntegerField(default=0) #Goal For
    ga = models.IntegerField(default=0) # Goal Against
    average_team_score = models.FloatField(default=0.0, editable=False)
    achievements = models.JSONField(blank=True, null=True)
    elo_rating = models.FloatField(default=1200, editable=False)
    match_data = models.JSONField(blank=True, null=True, default=dict)

    def set_rank_based_on_elo(self):
        """Set ranking string based on Elo thresholds."""
        ranking_thresholds = [
            (1200, 'bronze'),
            (1400, 'silver'),
            (1600, 'gold'),
            (1800, 'platinum'),
            (2000, 'diamond'),
            (2200, 'master'),
            (2400, 'grandmaster'),
            (2600, 'champion'),
        ]
        self.rank = 'invincible'

        for threshold, rank in ranking_thresholds:
            if self.elo_rating < threshold:
                self.rank = rank
                break

        self.save()
  
    def get_json_file_path(self):
        """File path for external JSON backup of match data."""
        directory = os.path.join(settings.MEDIA_ROOT, 'match_data')
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, f'clan_match_data_{self.pk}.json')

    def save_match_data_to_file(self):
        """Backup match_data to JSON file."""
        if not self.match_data:
            return
        file_path = self.get_json_file_path()
        with open(file_path, 'w') as json_file:
            json.dump(self.match_data, json_file, indent=4)

    def load_match_data_from_file(self):
        """Load match_data from JSON backup file."""
        file_path = self.get_json_file_path()
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            try:
                with open(file_path, 'r') as json_file:
                    return json.load(json_file)
            except json.JSONDecodeError:
                return {}
        return {}

    def delete(self, *args, **kwargs):
        """Remove JSON backup file on delete."""
        file_path = self.get_json_file_path()
        if os.path.exists(file_path):
            os.remove(file_path)
        super().delete(*args, **kwargs)

class ClanJoinRequest(models.Model):
    """
    Stores player requests to join a clan.
    Tracks status (pending, approved, rejected).
    """
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    clan = models.ForeignKey(Clans, on_delete=models.CASCADE)
    status = models.CharField(max_length=20,choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)

    def approve(self):
        """
        Approve the join request:
        - Set status approved
        - Add clan to player's profile
        - Reject any other pending requests for the same player
        Uses try/except to catch and handle errors gracefully.
        """
        try:
            self.status = "approved"
            self.save()

            # Update player's profile
            profile = self.player.profile
            profile.clan = self.clan
            profile.save()

            # Reject other pending requests for the same player
            ClanJoinRequest.objects.filter(player=self.player, status="pending").exclude(pk=self.pk).update(status="rejected")
        except Exception as e:
            ErrorHandler().handle(e, context=f"Failed to approve join request for user {self.player.id} to clan {self.clan.id}")

    def reject(self):
        """Reject the join request by setting status to rejected."""
        self.status = "rejected"
        self.save()

class ClanSocialLink(models.Model):
    SOCIAL_CHOICES = [
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('website', 'Website'),
        ('other', 'Other'),
    ]

    clan = models.ForeignKey(Clans, on_delete=models.CASCADE, related_name='social_links')
    link_type = models.CharField(max_length=20, choices=SOCIAL_CHOICES)
    url = models.URLField(max_length=500)
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which this link should appear")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "link_type"]
        unique_together = ("clan", "link_type")

    def __str__(self):
        return f"{self.get_link_type_display()} - {self.url}"

    def clean(self):
        if self.url and not self.url.startswith(("http://", "https://")):
            self.url = "https://" + self.url
