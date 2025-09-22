# Aries Frontend - Modern TypeScript Gaming Platform

This is the modern TypeScript frontend for the Aries gaming platform, featuring a unified organization system and modern UI components.

## Features

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

## Getting Started

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

## Contributing

1. Follow TypeScript best practices
2. Use Tailwind CSS for styling
3. Write reusable components
4. Add proper TypeScript types
5. Test components thoroughly

## License

This project is licensed under the MIT License.
