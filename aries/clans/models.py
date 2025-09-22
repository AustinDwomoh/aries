from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django_countries.fields import CountryField
from PIL import Image
from scripts.error_handle import ErrorHandler


class ClanManager(BaseUserManager):
    def create_clan(self, name, password=None, **extra_fields):
        if not name:
            raise ValueError('Clans must have a name')
        clan = self.model(name=name, **extra_fields)
        clan.set_password(password)
        clan.save(using=self._db)
        return clan


class Clan(AbstractBaseUser, PermissionsMixin):
    """
    Clan model for gaming teams that participate in tournaments.
    Clans are competitive gaming teams, not organizers.
    """
    name = models.CharField(max_length=255, unique=True)
    tag = models.CharField(max_length=6, unique=True, help_text="Clan tag must be unique and up to 6 characters long.")
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    description = models.TextField()
    logo = models.ImageField(default="clan-default.png", upload_to='clan_logos')
    profile_picture = models.ImageField(default="clan-profile-default.jpg", upload_to='clan_profiles')
    website = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Gaming information
    primary_game = models.CharField(max_length=255, blank=True, null=True)
    other_games = models.CharField(max_length=255, blank=True, null=True)
    country = CountryField(blank_label='(select country)')
    
    # Clan status
    is_recruiting = models.BooleanField(default=False)
    recruitment_requirements = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Django auth-required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']
    objects = ClanManager()
    
    # Permissions and groups fields override for clans as "users"
    groups = models.ManyToManyField(Group, related_name='clan_set', blank=True, help_text='The groups this clan belongs to.', related_query_name='clan')
    user_permissions = models.ManyToManyField(Permission, related_name='clan_permissions_set', blank=True, help_text='Specific permissions for this clan.', related_query_name='clan')
    
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
        return f"{self.name} [{self.tag}]"
    
    def save(self, *args, **kwargs):
        """Resize profile pic on save if bigger than 300x300."""
        super().save(*args, **kwargs)
        if self.profile_picture:
            try:
                img = Image.open(self.profile_picture.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.profile_picture.path)
            except Exception as e:
                ErrorHandler().handle(e, context=f"Error resizing clan profile picture for {self.name}")


class ClanStats(models.Model):
    """
    Tracks clan performance metrics for competitive gaming.
    """
    clan = models.OneToOneField(Clan, on_delete=models.CASCADE, related_name='stats')
    total_matches = models.IntegerField(default=0, editable=False)
    win_rate = models.FloatField(default=0.0, editable=False)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_draws = models.IntegerField(default=0)
    
    RANK_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
        ('master', 'Master'),
        ('grandmaster', 'Grandmaster'),
        ('champion', 'Champion'),
        ('invincible', 'Invincible'),
    ]
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, blank=True, null=True, editable=False)
    player_scored = models.IntegerField(default=0)
    player_conceded = models.IntegerField(default=0)
    gd = models.IntegerField(default=0)  # Goal difference
    gf = models.IntegerField(default=0)  # Goals for
    ga = models.IntegerField(default=0)  # Goals against
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


class ClanMember(models.Model):
    """
    Represents a member of a clan.
    """
    ROLE_CHOICES = [
        ('leader', 'Leader'),
        ('captain', 'Captain'),
        ('member', 'Member'),
        ('recruit', 'Recruit'),
    ]
    
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='clan_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('clan', 'user')
        verbose_name = "Clan Member"
        verbose_name_plural = "Clan Members"
    
    def __str__(self):
        return f"{self.user.username} - {self.clan.name}"


class ClanJoinRequest(models.Model):
    """
    Stores user requests to join a clan.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'clan')
        verbose_name = "Clan Join Request"
        verbose_name_plural = "Clan Join Requests"
    
    def approve(self):
        """Approve the join request and add user to clan."""
        try:
            self.status = "approved"
            self.save()
            
            # Add user to clan
            ClanMember.objects.get_or_create(
                clan=self.clan,
                user=self.user,
                defaults={'role': 'member'}
            )
            
            # Reject other pending requests for the same user
            ClanJoinRequest.objects.filter(
                user=self.user, 
                status="pending"
            ).exclude(pk=self.pk).update(status="rejected")
        except Exception as e:
            ErrorHandler().handle(e, context=f"Failed to approve join request for user {self.user.id} to clan {self.clan.id}")
    
    def reject(self):
        """Reject the join request."""
        self.status = "rejected"
        self.save()
    
    def __str__(self):
        return f"{self.user.username} -> {self.clan.name} ({self.status})"


class ClanSocialLink(models.Model):
    """
    Social media links for clans.
    """
    SOCIAL_CHOICES = [
        ('discord', 'Discord'),
        ('whatsapp', 'WhatsApp'),
        ('x', 'X / Twitter'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('twitch', 'Twitch'),
        ('website', 'Website'),
        ('other', 'Other'),
    ]
    
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='social_links')
    link_type = models.CharField(max_length=20, choices=SOCIAL_CHOICES)
    url = models.URLField(max_length=500)
    
    class Meta:
        unique_together = ("clan", "link_type")
        verbose_name = "Clan Social Link"
        verbose_name_plural = "Clan Social Links"
    
    def __str__(self):
        return f"{self.clan.name} - {self.get_link_type_display()}"
    
    def clean(self):
        if self.url and not self.url.startswith(("http://", "https://")):
            self.url = "https://" + self.url
