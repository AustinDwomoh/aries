# Aries - Modern Gaming Platform

<<<<<<< Updated upstream
**Aries** is a comprehensive gaming platform that revolutionizes esports tournaments and community building. Built with Django REST Framework and React TypeScript, it provides a unified platform for organizations, individual players, and tournament management.
=======
**Aries** is a modern web application designed to revolutionize gaming tournaments and community building in esports. Built with Django REST Framework and React TypeScript, it provides a unified platform for organizations, individual players, and tournament management.

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

### **Developer Experience**
- **REST API**: Comprehensive Django REST Framework API
- **Type Safety**: Full TypeScript support throughout
- **Modern Tooling**: Vite, ESLint, Prettier, and more
- **Documentation**: Comprehensive API and component documentation

## 🏗️ Architecture

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
│   └── settings.py         # Django configuration
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
# Aries Frontend - Modern TypeScript Gaming Platform

This is the modern TypeScript frontend for the Aries gaming platform, featuring a unified organization system and modern UI components.
>>>>>>> Stashed changes

## 🚀 Features

<<<<<<< Updated upstream
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
=======
- **Modern TypeScript/React Frontend**: Built with Vite, React 18, and TypeScript
- **Unified Organization System**: Organizations work like users for both clans and organizations
- **Beautiful UI Components**: Modern card-based design with Tailwind CSS
- **State Management**: Zustand for efficient state management
- **REST API Integration**: Seamless communication with Django backend
- **Responsive Design**: Mobile-first approach with modern animations

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Forms**: React Hook Form
- **Notifications**: React Hot Toast
>>>>>>> Stashed changes

## 🏗️ Tech Stack

<<<<<<< Updated upstream
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
=======
### Prerequisites

- Node.js 18+ 
- npm or yarn
- Python 3.10+ (for Django backend)
- Django backend running on port 8000

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

4. **Type checking**:
   ```bash
   npm run type-check
   ```

5. **Linting**:
   ```bash
   npm run lint
   ```

### Development

The frontend runs on `http://localhost:3000` and automatically proxies API requests to the Django backend at `http://localhost:8000`.

### Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (Card, Button, Modal, etc.)
│   ├── OrganizationCard.tsx
│   ├── TournamentCard.tsx
│   └── Dashboard.tsx
├── pages/              # Page components
│   ├── LoginPage.tsx
│   └── RegisterPage.tsx
├── store/              # State management
│   ├── authStore.ts
│   ├── organizationStore.ts
│   └── tournamentStore.ts
├── services/           # API services
│   └── api.ts
├── types/              # TypeScript type definitions
│   └── index.ts
├── App.tsx             # Main app component
├── main.tsx           # Entry point
└── index.css          # Global styles
```

## Key Features

### Unified Organization System

The new system treats organizations as first-class users, supporting:
- **Multiple Organization Types**: Clans, Organizations, Teams, Guilds
- **Member Management**: Role-based permissions (Admin, Captain, Member, Recruit)
- **Join Requests**: Request-based joining with approval workflow
- **Social Links**: Multiple social media platform support
- **Statistics**: Performance tracking and ranking system

### Modern UI Components

- **Organization Cards**: Beautiful cards with stats, social links, and actions
- **Tournament Cards**: Comprehensive tournament information with join functionality
- **Dashboard**: Modern dashboard with stats, filtering, and grid/list views
- **Responsive Design**: Mobile-first approach with smooth animations

### State Management

- **Auth Store**: User authentication and profile management
- **Organization Store**: Organization data and member management
- **Tournament Store**: Tournament data and participation management

## API Integration

The frontend communicates with the Django backend through REST API endpoints:

- `GET /api/organizations/` - List organizations
- `POST /api/organizations/` - Create organization
- `GET /api/organizations/{id}/` - Get organization details
- `POST /api/organizations/{id}/join/` - Join organization
- `POST /api/organizations/{id}/leave/` - Leave organization

## Development Workflow

1. **Start Django backend**: `python manage.py runserver`
2. **Start frontend**: `npm run dev`
3. **Access application**: `http://localhost:3000`

## Building for Production

1. **Build frontend**: `npm run build`
2. **Serve static files**: The built files will be in the `dist/` directory
3. **Configure Django**: Update Django settings to serve the built files
>>>>>>> Stashed changes

### **1. Clone the Repository**
```bash
git clone https://github.com/INPHINITHY/aries.git
cd aries
```

<<<<<<< Updated upstream
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

=======
1. Follow TypeScript best practices
2. Use Tailwind CSS for styling
3. Write reusable components
4. Add proper TypeScript types
5. Test components thoroughly

## License

This project is licensed under the MIT License.

### **2. Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start Django server
python manage.py runserver
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
python manage.py runserver

# Run tests
python manage.py test

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
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
python manage.py test
```

### **Frontend Tests**
```bash
npm test
```

## 📦 Deployment

### **Backend Deployment**
1. Set up production database (PostgreSQL recommended)
2. Configure environment variables
3. Run migrations: `python manage.py migrate`
4. Collect static files: `python manage.py collectstatic`
5. Deploy with your preferred WSGI server (Gunicorn, uWSGI)

### **Frontend Deployment**
1. Build the frontend: `npm run build`
2. Serve the `dist/` directory with your web server
3. Configure API endpoints for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `npm test` and `python manage.py test`
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

Created by [Austin Nana Dwomoh (INPHINITHY)](https://austindwomoh.xyz/).  
Connect on [GitHub](https://github.com/INPHINITHY), [Instagram](https://www.instagram.com/inphinithy1/), or [LinkedIn](https://www.linkedin.com/in/austin-dwomoh/).

>>>>>>> Stashed changes
---

> "Join us in building a community where gaming dreams become reality—because together, we're not just playing the game; we're shaping the future of esports."