import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Trophy, 
  Calendar, 
  TrendingUp, 
  Plus,
  Search,
  Filter,
  Grid,
  List,
  Crown,
  Zap,
  Target,
  Gamepad2,
  Star,
  Flame,
  Sword,
  Shield
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useOrganizationStore } from '@/store/organizationStore';
import { useTournamentStore } from '@/store/tournamentStore';
import { OrganizationCard } from './OrganizationCard';
import { TournamentCard } from './TournamentCard';
import { Card, CardContent } from './ui/Card';
import { Button } from './ui/Button';
import { OrganizationFilters, TournamentFilters } from '@/types';

export const Dashboard: React.FC = () => {
  const { user, profile } = useAuthStore();
  const { 
    organizations, 
    fetchOrganizations, 
    isLoading: orgsLoading 
  } = useOrganizationStore();
  const { 
    tournaments, 
    fetchTournaments, 
    isLoading: tournamentsLoading 
  } = useTournamentStore();

  const [orgFilters] = useState<OrganizationFilters>({});
  const [tournamentFilters] = useState<TournamentFilters>({});
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [activeTab, setActiveTab] = useState<'organizations' | 'tournaments'>('organizations');

  useEffect(() => {
    fetchOrganizations(orgFilters);
    fetchTournaments(tournamentFilters);
  }, [orgFilters, tournamentFilters]);


  const handleViewOrganization = (id: number) => {
    // TODO: Implement view organization logic
    console.log('View organization:', id);
  };

  const handleJoinTournament = (id: number) => {
    // TODO: Implement join tournament logic
    console.log('Join tournament:', id);
  };

  const handleViewTournament = (id: number) => {
    // TODO: Implement view tournament logic
    console.log('View tournament:', id);
  };

  const stats = [
    {
      title: 'Active Organizations',
      value: organizations.length,
      icon: Crown,
      color: 'text-yellow-500',
      bgColor: 'bg-gradient-to-br from-yellow-100 to-yellow-200',
      description: 'Tournament organizers',
    },
    {
      title: 'Live Tournaments',
      value: tournaments.filter(t => t.status === 'ongoing').length,
      icon: Flame,
      color: 'text-red-500',
      bgColor: 'bg-gradient-to-br from-red-100 to-red-200',
      description: 'Currently running',
    },
    {
      title: 'Upcoming Battles',
      value: tournaments.filter(t => t.status === 'upcoming').length,
      icon: Target,
      color: 'text-purple-500',
      bgColor: 'bg-gradient-to-br from-purple-100 to-purple-200',
      description: 'Ready to compete',
    },
    {
      title: 'Your Clan',
      value: profile?.clan ? 1 : 0,
      icon: Shield,
      color: 'text-blue-500',
      bgColor: 'bg-gradient-to-br from-blue-100 to-blue-200',
      description: 'Your team status',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Gaming Header */}
      <div className="relative bg-gradient-to-r from-purple-900 via-blue-900 to-indigo-900 shadow-2xl border-b border-purple-500/20">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-8">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl shadow-lg">
                <Gamepad2 className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
                  Welcome back, {user?.first_name || user?.username}!
                </h1>
                <p className="text-purple-200 mt-2 text-lg">
                  Ready to dominate the esports arena? 🎮
                </p>
              </div>
            </div>
            <div className="flex space-x-4">
              <Button variant="outline" className="bg-white/10 border-purple-400 text-white hover:bg-purple-500/20">
                <Crown className="w-4 h-4 mr-2" />
                Create Organization
              </Button>
              <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg">
                <Trophy className="w-4 h-4 mr-2" />
                Host Tournament
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Gaming Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ delay: index * 0.1, type: "spring", stiffness: 100 }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="group"
            >
              <Card className="bg-gradient-to-br from-gray-800 to-gray-900 border-gray-700 hover:border-purple-500/50 transition-all duration-300 shadow-xl hover:shadow-2xl">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`p-4 rounded-xl ${stat.bgColor} group-hover:scale-110 transition-transform duration-300`}>
                        <stat.icon className={`w-8 h-8 ${stat.color}`} />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors">
                          {stat.title}
                        </p>
                        <p className="text-3xl font-bold text-white group-hover:text-purple-300 transition-colors">
                          {stat.value}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          {stat.description}
                        </p>
                      </div>
                    </div>
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <Zap className="w-5 h-5 text-purple-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Main Content */}
        <div className="space-y-8">
          {/* Gaming Tabs */}
          <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-xl p-1 border border-gray-700">
            <nav className="flex space-x-2">
              <button
                onClick={() => setActiveTab('organizations')}
                className={`flex items-center space-x-2 py-3 px-6 rounded-lg font-medium text-sm transition-all duration-300 ${
                  activeTab === 'organizations'
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`}
              >
                <Crown className="w-4 h-4" />
                <span>Organizations</span>
              </button>
              <button
                onClick={() => setActiveTab('tournaments')}
                className={`flex items-center space-x-2 py-3 px-6 rounded-lg font-medium text-sm transition-all duration-300 ${
                  activeTab === 'tournaments'
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`}
              >
                <Trophy className="w-4 h-4" />
                <span>Tournaments</span>
              </button>
            </nav>
          </div>

          {/* Gaming Filters and Controls */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="relative group">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-purple-400 w-5 h-5 group-hover:text-purple-300 transition-colors" />
                <input
                  type="text"
                  placeholder="Search for organizations, tournaments..."
                  className="pl-12 pr-4 py-3 border border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-gray-800 text-white placeholder-gray-400 w-80 transition-all duration-300 hover:border-purple-500/50"
                />
              </div>
              <Button variant="outline" size="sm" className="bg-gray-800 border-gray-600 text-white hover:bg-purple-600 hover:border-purple-500">
                <Filter className="w-4 h-4 mr-2" />
                Advanced Filters
              </Button>
            </div>
            
            <div className="flex items-center space-x-2 bg-gray-800 rounded-lg p-1">
              <Button
                variant={viewMode === 'grid' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
                className={viewMode === 'grid' ? 'bg-purple-600 hover:bg-purple-700' : 'bg-transparent border-gray-600 text-gray-400 hover:text-white hover:bg-gray-700'}
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
                className={viewMode === 'list' ? 'bg-purple-600 hover:bg-purple-700' : 'bg-transparent border-gray-600 text-gray-400 hover:text-white hover:bg-gray-700'}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Content */}
          {activeTab === 'organizations' ? (
            <div className="space-y-6">
              {orgsLoading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : (
                <div className={`grid gap-6 ${
                  viewMode === 'grid' 
                    ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' 
                    : 'grid-cols-1'
                }`}>
                  {organizations.map((organization) => (
                    <OrganizationCard
                      key={organization.id}
                      organization={organization}
                      onView={handleViewOrganization}
                      showActions={true}
                    />
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {tournamentsLoading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : (
                <div className={`grid gap-6 ${
                  viewMode === 'grid' 
                    ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' 
                    : 'grid-cols-1'
                }`}>
                  {tournaments.map((tournament) => (
                    <TournamentCard
                      key={tournament.id}
                      tournament={tournament}
                      onJoin={handleJoinTournament}
                      onView={handleViewTournament}
                      showActions={true}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
