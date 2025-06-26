import os
import django
import requests
from io import BytesIO
from faker import Faker
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aries.settings')
django.setup()
from django.core.files import File
from django.contrib.auth.models import User
from users.models import Profile
from clans.models import Clans  # adjust import paths
NUM_CLANS = 16
CLAN_MEMBERS = 10
TOTAL_USERS = NUM_CLANS * CLAN_MEMBERS 
fake = Faker()
def create_unique_user():
    while True:
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            user = create_user_with_image(username)
            return user
def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)

def create_user_with_image(username):
    user = User.objects.create_user(username=username, password='pass1234', email=f'{username}@example.com')
    profile = user.profile
    
    img_temp = download_image('https://picsum.photos/300/300')
    profile.profile_picture.save(f'{username}.jpg', File(img_temp), save=True)
    print(f"Created user {user.username} with profile picture.")
    

    return user

def create_clan_with_image(name, created_by):
    clan_tag = name[:4].upper()
    email = f"{name.lower()}@example.com"
    password = fake.password()
    description = fake.paragraph()
    website = f"https://{name.lower()}.gg"
    country = fake.country()

    # Optional: create social links as JSON
    social_links = {
        "twitter": f"https://twitter.com/{name.lower()}",
        "discord": f"https://discord.gg/{fake.lexify(text='????????')}",
    }

    # Download and assign logos
    clan_logo_img = download_image('https://picsum.photos/300/300')
    clan_profile_img = download_image('https://picsum.photos/300/300')

    clan = Clans(
        clan_name=name,
        clan_tag=clan_tag,
        email=email,
        password=password,
        clan_description=description,
        clan_website=website,
        country=country,
        social_links=social_links,
        is_recruiting=fake.boolean(),
        recruitment_requirements=fake.text(max_nb_chars=150),
        created_by=created_by,
        primary_game="Valorant",  
        other_games="Overwatch, Apex Legends"
    )

    # Save the clan so file paths exist
    clan.save()

    clan.clan_logo.save(f'{name}_logo.jpg', File(clan_logo_img), save=True)
    clan.clan_profile_pic.save(f'{name}_profile.jpg', File(clan_profile_img), save=True)

    print(f"Created clan {clan.clan_name} by {created_by.username}")
    return clan

def seed():
    users = []
    for _ in range(TOTAL_USERS):
        user = create_unique_user()
        users.append(user)

    clans = []
    for i in range(NUM_CLANS):
        clan_name = f'Clan_{fake.unique.user_name()}'
        clan = create_clan_with_image(clan_name, users[i])
        clans.append(clan)

    # Assign 10 users per clan
    for idx, clan in enumerate(clans):
        clan_users = users[idx * CLAN_MEMBERS : (idx + 1) * CLAN_MEMBERS]
        for user in clan_users:
            profile = user.profile
            profile.clan = clan
            profile.role = 'member'  # Or randomly assign roles if you want
            profile.save()

if __name__ == '__main__':
    seed()
