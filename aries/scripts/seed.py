import os,time,random,django,requests
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
        name = fake.user_name()
        if not User.objects.filter(name=name).exists():
            user = create_user_with_image(name)
            return user
def download_image(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.exceptions.RequestException as e:
            print(f"[WARN] Failed to download image (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                sleep_time = delay + random.uniform(0, 1)  # jitter
                print(f"[INFO] Retrying in {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            else:
                print("[ERROR] Max retries reached. Skipping image.")
                return BytesIO()  # return an empty image buffer or handle default

def create_user_with_image(name):
    user = User.objects.create_user(name=name, password='pass1234', email=f'{name}@example.com')
    profile = user.profile
    profile.is_verified = True
    img_temp = download_image('https://picsum.photos/300/300')
    if img_temp.getbuffer().nbytes > 0:
        profile.profile_picture.save(f'{name}.jpg', File(img_temp), save=True)
    else:
        print(f"[WARN] No image saved for user {name}")
    
    print(f"Created user {user.name} with profile picture.")
    

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
        name=name,
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

    print(f"Created clan {clan.name} by {created_by.name}")
    return clan

def seed():
    users = []
    for _ in range(TOTAL_USERS):
        user = create_unique_user()
        users.append(user)

    clans = []
    for i in range(NUM_CLANS):
        name = f'Clan_{fake.unique.user_name()}'
        clan = create_clan_with_image(name, users[i])
        clans.append(clan)

    # Assign 10 users per clan
    for idx, clan in enumerate(clans):
        clan_users = users[idx * CLAN_MEMBERS : (idx + 1) * CLAN_MEMBERS]
        for user in clan_users:
            profile = user.profile
            profile.clan = clan
            profile.role = 'member'  # Or randomly assign roles if you want
            profile.is_verified = True
            profile.save()

if __name__ == '__main__':
    seed()
