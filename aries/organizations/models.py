from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django_countries.fields import CountryField
from PIL import Image
from scripts.error_handle import ErrorHandler


class OrganizationManager(BaseUserManager):
    def create_organization(self, name, password=None, **extra_fields):
        if not name:
            raise ValueError('Organizations must have a name')
        organization = self.model(name=name, **extra_fields)
        organization.set_password(password)
        organization.save(using=self._db)
        return organization


class Organization(AbstractBaseUser, PermissionsMixin):
    """
    Organization model for tournament organizers and event companies.
    Organizations are pure organizers - they create and manage tournaments but don't participate.
    """
    ORGANIZATION_TYPES = [
        ('esports_company', 'Esports Company'),
        ('tournament_organizer', 'Tournament Organizer'),
        ('gaming_community', 'Gaming Community'),
        ('event_company', 'Event Company'),
        ('sponsor', 'Sponsor'),
        ('media_company', 'Media Company'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    tag = models.CharField(max_length=10, unique=True, help_text="Organization tag must be unique and up to 10 characters long.")
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    description = models.TextField()
    logo = models.ImageField(default="areis-1.png", upload_to='organization_logos')
    profile_picture = models.ImageField(default="areis-2.jpg", upload_to='organization_profiles')
    website = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    primary_game = models.CharField(max_length=255, blank=True, null=True)
    other_games = models.CharField(max_length=255, blank=True, null=True)
    country = CountryField(blank_label='(select country)')
    # Organization-specific fields
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPES, default='tournament_organizer')
    
    # Organizer capabilities
    can_host_tournaments = models.BooleanField(default=True)
    can_sponsor_events = models.BooleanField(default=False)
    can_manage_prizes = models.BooleanField(default=True)
    can_verify_teams = models.BooleanField(default=False)
    
    # Business information
    business_license = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    
    # Financial information
    total_prize_money_distributed = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_tournaments_hosted = models.PositiveIntegerField(default=0)
    average_tournament_size = models.PositiveIntegerField(default=0)
    
    # Django auth-required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']
    objects = OrganizationManager()
    
    # Permissions and groups fields override for organizations as "users"
    groups = models.ManyToManyField(Group, related_name='organization_set', blank=True, help_text='The groups this organization belongs to.', related_query_name='organization')
    user_permissions = models.ManyToManyField(Permission, related_name='organization_permissions_set', blank=True, help_text='Specific permissions for this organization.', related_query_name='organization')
    
    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
    
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
                ErrorHandler().handle(e, context=f"Error resizing organization profile picture for {self.name}")


class OrganizationReputation(models.Model):
    """
    Tracks organization reputation and organizer metrics.
    Organizations don't compete, they organize and build reputation.
    """
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='reputation')
    
    # Reputation metrics
    reputation_score = models.FloatField(default=0.0)  # 0-100 scale
    total_events_organized = models.PositiveIntegerField(default=0)
    total_participants_reached = models.PositiveIntegerField(default=0)
    average_event_rating = models.FloatField(default=0.0)
    
    # Financial metrics
    total_prize_money_distributed = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Quality metrics
    on_time_completion_rate = models.FloatField(default=100.0)  # Percentage
    participant_satisfaction = models.FloatField(default=0.0)  # 0-5 scale
    dispute_resolution_rate = models.FloatField(default=100.0)  # Percentage
    
    # Achievements and badges
    achievements = models.JSONField(blank=True, null=True, default=list)
    badges = models.JSONField(blank=True, null=True, default=list)
    
    # Verification status
    is_verified_organizer = models.BooleanField(default=False)
    verification_level = models.CharField(max_length=20, choices=[
        ('basic', 'Basic'),
        ('verified', 'Verified'),
        ('premium', 'Premium'),
        ('elite', 'Elite'),
    ], default='basic')
    
    def calculate_reputation_score(self):
        """Calculate overall reputation score based on various metrics."""
        # Weighted calculation of reputation
        score = 0
        score += self.average_event_rating * 20  # 0-100
        score += min(self.total_events_organized * 2, 30)  # Max 30 points
        score += min(self.on_time_completion_rate, 20)  # Max 20 points
        score += min(self.participant_satisfaction * 4, 20)  # Max 20 points
        score += min(self.dispute_resolution_rate, 10)  # Max 10 points
        
        self.reputation_score = min(score, 100.0)
        self.save()
        return self.reputation_score


class OrganizationMember(models.Model):
    """
    Represents a member of an organization.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('captain', 'Captain'),
        ('member', 'Member'),
        ('recruit', 'Recruit'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('organization', 'user')
        verbose_name = "Organization Member"
        verbose_name_plural = "Organization Members"
    
    def __str__(self):
        return f"{self.user.username} - {self.organization.name}"


class OrganizationJoinRequest(models.Model):
    """
    Stores user requests to join an organization.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'organization')
        verbose_name = "Organization Join Request"
        verbose_name_plural = "Organization Join Requests"
    
    def approve(self):
        """Approve the join request and add user to organization."""
        try:
            self.status = "approved"
            self.save()
            
            # Add user to organization
            OrganizationMember.objects.get_or_create(
                organization=self.organization,
                user=self.user,
                defaults={'role': 'member'}
            )
            
            # Reject other pending requests for the same user
            OrganizationJoinRequest.objects.filter(
                user=self.user, 
                status="pending"
            ).exclude(pk=self.pk).update(status="rejected")
        except Exception as e:
            ErrorHandler().handle(e, context=f"Failed to approve join request for user {self.user.id} to organization {self.organization.id}")
    
    def reject(self):
        """Reject the join request."""
        self.status = "rejected"
        self.save()
    
    def __str__(self):
        return f"{self.user.username} -> {self.organization.name} ({self.status})"


class OrganizationSocialLink(models.Model):
    """
    Social media links for organizations.
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
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='social_links')
    link_type = models.CharField(max_length=20, choices=SOCIAL_CHOICES)
    url = models.URLField(max_length=500)
    
    class Meta:
        unique_together = ("organization", "link_type")
        verbose_name = "Organization Social Link"
        verbose_name_plural = "Organization Social Links"
    
    def __str__(self):
        return f"{self.organization.name} - {self.get_link_type_display()}"
    
    def clean(self):
        if self.url and not self.url.startswith(("http://", "https://")):
            self.url = "https://" + self.url
