# Aries - Modern Gaming Platform

**Aries** is a comprehensive gaming platform that revolutionizes esports tournaments and community building. Built with Django REST Framework and React TypeScript, it provides a unified platform for organizations, individual players, and tournament management.

## 🚀 Features

### **Unified Organization System**
- **Multiple Organization Types**: Clans, Organizations, Teams, and Guilds
- **Member Management**: Role-based permissions (Admin, Captain, Member, Recruit)
- **Join Requests**: Request-based joining with approval workflow
- **Social Integration**: Multiple social media platform support
- **Performance Tracking**: Statistics, rankings, and ELO rating system

### **Tournament Management**
- **Individual Tournaments**: Players compete directly
- **Organization Tournaments**: Organizations participate through their members
- **Multiple Formats**: League, Cup, and Groups + Knockout
- **Real-time Updates**: Live match results and standings
- **Prize Management**: Entry fees and prize pool distribution

### **Modern User Experience**
- **TypeScript Frontend**: React 18 with Vite for fast development
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Beautiful UI**: Modern card-based design with smooth animations
- **State Management**: Efficient state management with Zustand
- **Real-time Features**: Live updates and notifications

## 🏗️ Tech Stack

### **Backend (Django)**
- **Django 5.1.4** with REST Framework
- **Unified Organization Model** that works like users
- **PostgreSQL/SQLite** database support
- **JWT Authentication** with session fallback
- **CORS Support** for frontend integration

### **Frontend (React TypeScript)**
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Zustand** for state management
- **Axios** for API communication
- **Framer Motion** for animations

## 📁 Project Structure

```
aries/
├── aries/                    # Django backend
│   ├── organizations/        # Unified organizations app
│   ├── tournaments/         # Tournament management
│   ├── users/              # User management
│   ├── clans/              # Legacy clan system
│   └── manage.py           # Django management script
├── src/                    # React TypeScript frontend
│   ├── components/         # Reusable UI components
│   ├── pages/             # Page components
│   ├── store/             # State management
│   ├── services/          # API services
│   └── types/             # TypeScript definitions
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.10+
- Node.js 18+
- npm or yarn

### **1. Clone the Repository**
```bash
git clone https://github.com/INPHINITHY/aries.git
cd aries
```

### **2. Backend Setup**
```bash
# Create and activate virtual environment
python -m venv aries_venv
# Windows
aries_venv\Scripts\activate
# macOS/Linux
source aries_venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python aries/manage.py makemigrations
python aries/manage.py migrate

# Create superuser (optional)
python aries/manage.py createsuperuser

# Start Django server
python aries/manage.py runserver
```

### **3. Frontend Setup**
```bash
# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

### **4. Access the Application**
- **Frontend**: http://localhost:3000
- **Django Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/

## 🛠️ Development

### **Backend Development**
```bash
# Run Django server
python aries/manage.py runserver

# Run tests
python aries/manage.py test

# Create migrations
python aries/manage.py makemigrations

# Apply migrations
python aries/manage.py migrate
```

### **Frontend Development**
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

## 📚 API Documentation

### **Organizations**
- `GET /api/organizations/` - List organizations
- `POST /api/organizations/` - Create organization
- `GET /api/organizations/{id}/` - Get organization details
- `POST /api/organizations/{id}/join/` - Join organization
- `POST /api/organizations/{id}/leave/` - Leave organization

### **Tournaments**
- `GET /api/tournaments/` - List tournaments
- `POST /api/tournaments/` - Create tournament
- `GET /api/tournaments/{id}/` - Get tournament details
- `POST /api/tournaments/{id}/join/` - Join tournament
- `POST /api/tournaments/{id}/leave/` - Leave tournament

### **Users**
- `GET /api/users/` - List users
- `GET /api/users/{id}/profile/` - Get user profile
- `PATCH /api/users/{id}/profile/` - Update user profile

## 🎨 UI Components

### **Organization Cards**
- Beautiful cards with organization stats
- Social links and member count
- Join/leave functionality
- Responsive design

### **Tournament Cards**
- Comprehensive tournament information
- Status indicators and participant count
- Prize pool and entry fee display
- Join/leave functionality

### **Dashboard**
- Modern dashboard with statistics
- Filtering and search capabilities
- Grid and list view modes
- Real-time updates

## 🔧 Configuration

### **Environment Variables**
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### **Frontend Configuration**
The frontend automatically proxies API requests to the Django backend. No additional configuration needed for development.

## 🧪 Testing

### **Backend Tests**
```bash
python aries/manage.py test
```

### **Frontend Tests**
```bash
npm test
```

## 📦 Deployment

### **Backend Deployment**
1. Set up production database (PostgreSQL recommended)
2. Configure environment variables
3. Run migrations: `python aries/manage.py migrate`
4. Collect static files: `python aries/manage.py collectstatic`
5. Deploy with your preferred WSGI server (Gunicorn, uWSGI)

### **Frontend Deployment**
1. Build the frontend: `npm run build`
2. Serve the `dist/` directory with your web server
3. Configure API endpoints for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `npm test` and `python aries/manage.py test`
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

Created by [Austin Nana Dwomoh (INPHINITHY)](https://austindwomoh.xyz/).  
Connect on [GitHub](https://github.com/INPHINITHY), [Instagram](https://www.instagram.com/inphinithy1/), or [LinkedIn](https://www.linkedin.com/in/austin-dwomoh/).

---

> "Join us in building a community where gaming dreams become reality—because together, we're not just playing the game; we're shaping the future of esports."