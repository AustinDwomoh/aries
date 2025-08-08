import os, time, random, django, requests
from io import BytesIO
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aries.settings')
django.setup()

import logging
logging.getLogger().setLevel(logging.CRITICAL)  # Only show your print statements

from django.core.files import File
from django.contrib.auth.models import User
from users.models import Profile
from clans.models import Clans

# Constants
NUM_CLANS = 4
CLAN_MEMBERS = 10
TOTAL_USERS = 5

fake = Faker()

def create_unique_user():
    while True:
        name = fake.user_name()
        if not User.objects.filter(username=name).exists():
            return create_user_with_image(name)

def download_image(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                time.sleep(delay + random.uniform(0, 1))
            else:
                return BytesIO()

def create_user_with_image(name):
    user = User.objects.create_user(username=name, password='pass1234', email=f'{name}@example.com')
    profile = user.profile
    profile.is_verified = True

    img_temp = download_image('https://picsum.photos/300/300')
    if img_temp.getbuffer().nbytes > 0:
        profile.profile_picture.save(f'{name}.jpg', File(img_temp), save=True)

    print(f"[+] Created user: {user.username}")
    return user

def create_clan_with_image(name, created_by):
    clan_tag = name[:4].upper()
    email = f"{name.lower()}@example.com"
    password = fake.password()
    print(f"[+] Created clan: {name} | Password: {password}")

    social_links = {
        "twitter": f"https://twitter.com/{name.lower()}",
        "discord": f"https://discord.gg/{fake.lexify(text='????????')}",
    }

    clan = Clans(
        clan_name=name,
        clan_tag=clan_tag,
        email=email,
        password=password,
        clan_description=fake.paragraph(),
        clan_website=f"https://{name.lower()}.gg",
        country=fake.country(),
        social_links=social_links,
        is_recruiting=fake.boolean(),
        recruitment_requirements=fake.text(max_nb_chars=150),
        created_by=created_by,
        primary_game="Valorant",
        other_games="Overwatch, Apex Legends"
    )
    clan.save()

    clan.clan_logo.save(f'{name}_logo.jpg', File(download_image('https://picsum.photos/300/300')), save=True)
    clan.clan_profile_pic.save(f'{name}_profile.jpg', File(download_image('https://picsum.photos/300/300')), save=True)

    return clan

def seed():
    users = [create_unique_user() for _ in range(TOTAL_USERS)]

    clans = []
    for i in range(NUM_CLANS):
        name = f'Clan_{fake.unique.user_name()}'
        clans.append(create_clan_with_image(name, users[i]))

    for idx, clan in enumerate(clans):
        start = idx * CLAN_MEMBERS
        end = start + CLAN_MEMBERS
        for user in users[start:end]:
            profile = user.profile
            profile.clan = clan
            profile.role = 'member'
            profile.is_verified = True
            profile.save()

if __name__ == '__main__':
    seed()
