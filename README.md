# Aries

**Aries** is a web application designed to revolutionize clan-based tournaments and community building in the world of esports and gaming. Its primary goal is to bridge the gap between passion and professionalism, enabling players, organizers, and teams to connect, compete, and succeed on a modern, user-friendly platform.

## Features

- **Clan Management:** Create, join, and manage clans with custom profile pictures and secure authentication.
- **User Profiles:** Gamers can create unique profiles, follow each other, and track their stats and ranks.
- **Tournaments:** Organizers can host, manage, and run tournaments involving multiple clans and users.
- **Custom Authentication:** Support for multi-field authentication and clan-based login workflows.
- **Social Integration:** Follow system, social icons, and profile context throughout the app.
- **Email Verification & OTP:** Secure account verification for both users and clans via tokens and OTPs.
- **Responsive UI:** Built with Bootstrap 5 and enhanced with AOS (Animate On Scroll) for smooth animations.

## Project Structure

- `aries/` – Django project configuration and settings.
- `Home/` – Landing pages, about, and core templates.
- `clans/` – Clan models, views, and templates for clan management.
- `tournaments/` – Tournament management and related features.
- `users/` – User registration, authentication, and profile management.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/INPHINITHY/aries.git
   cd aries
   ```

2. **Setup your environment:**
   - Python 3.10+
   - Django 5.1.4+
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Configure environment variables:**
   - Copy `.env.production` or create your own `.env` file in the project root.
   - Set necessary secrets (`SECRET_KEY`, API keys, etc.).

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the app:**
   - Navigate to `http://localhost:8000/` in your browser.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.

## About the Author

Created by [Austin Nana Dwomoh (INPHINITHY)](https://austindwomoh.xyz/).  
Connect on [GitHub](https://github.com/INPHINITHY), [Instagram](https://www.instagram.com/inphinithy1/), or [LinkedIn](https://www.linkedin.com/in/austin-dwomoh/).

## License

This project is licensed under the MIT License.

---

> "Join us in building a community where gaming dreams become reality—because together, we’re not just playing the game; we're shaping the future of esports."
