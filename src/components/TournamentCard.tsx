import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Users, Trophy, Clock, MapPin, ExternalLink, Sword, Shield, Zap, Target, Flame, Star } from 'lucide-react';
import { Tournament } from '@/types';
import { Card, CardContent, CardFooter } from './ui/Card';
import { Button } from './ui/Button';
import { format, isAfter, isBefore } from 'date-fns';

interface TournamentCardProps {
  tournament: Tournament;
  onJoin?: (id: number) => void;
  onView?: (id: number) => void;
  isJoined?: boolean;
  showActions?: boolean;
}

export const TournamentCard: React.FC<TournamentCardProps> = ({
  tournament,
  onJoin,
  onView,
  isJoined = false,
  showActions = true,
}) => {
  const getStatusColor = (status: string) => {
    const colors = {
      upcoming: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white',
      ongoing: 'bg-gradient-to-r from-green-500 to-green-600 text-white',
      completed: 'bg-gradient-to-r from-gray-500 to-gray-600 text-white',
      cancelled: 'bg-gradient-to-r from-red-500 to-red-600 text-white',
    };
    return colors[status as keyof typeof colors] || 'bg-gradient-to-r from-gray-500 to-gray-600 text-white';
  };

  const getFormatColor = (format: string) => {
    const colors = {
      league: 'bg-gradient-to-r from-purple-500 to-purple-600 text-white',
      cup: 'bg-gradient-to-r from-orange-500 to-orange-600 text-white',
      groups_knockout: 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white',
    };
    return colors[format as keyof typeof colors] || 'bg-gradient-to-r from-gray-500 to-gray-600 text-white';
  };

  const getTypeColor = (type: string) => {
    const colors = {
      individual: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white',
      clan: 'bg-gradient-to-r from-green-500 to-green-600 text-white',
    };
    return colors[type as keyof typeof colors] || 'bg-gradient-to-r from-gray-500 to-gray-600 text-white';
  };

  const getTypeIcon = (type: string) => {
    return type === 'individual' ? Sword : Shield;
  };

  const getStatusIcon = (status: string) => {
    const icons = {
      upcoming: Target,
      ongoing: Flame,
      completed: Trophy,
      cancelled: Clock,
    };
    return icons[status as keyof typeof icons] || Clock;
  };

  const TypeIcon = getTypeIcon(tournament.tournament_type);
  const StatusIcon = getStatusIcon(tournament.status);

  const isRegistrationOpen = tournament.status === 'upcoming' && 
    isBefore(new Date(), new Date(tournament.registration_deadline));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, type: "spring", stiffness: 100 }}
      whileHover={{ y: -8, scale: 1.02 }}
      className="h-full group"
    >
      <Card className="h-full flex flex-col bg-gradient-to-br from-gray-800 to-gray-900 border-gray-700 hover:border-purple-500/50 transition-all duration-300 shadow-xl hover:shadow-2xl overflow-hidden">
        {/* Gaming Header with animated background */}
        <div className="relative overflow-hidden">
          <div className="h-32 bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 relative">
            <div className="absolute inset-0 bg-black/20"></div>
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-pulse"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Trophy className="w-16 h-16 text-white/20" />
            </div>
          </div>
          
          {/* Status Badge */}
          <div className="absolute top-4 right-4">
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(tournament.status)} flex items-center space-x-1`}>
              <StatusIcon className="w-3 h-3" />
              <span>{tournament.status.toUpperCase()}</span>
            </div>
          </div>

          {/* Tournament Type Badge */}
          <div className="absolute top-4 left-4">
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getTypeColor(tournament.tournament_type)} flex items-center space-x-1`}>
              <TypeIcon className="w-3 h-3" />
              <span>{tournament.tournament_type.toUpperCase()}</span>
            </div>
          </div>

          {/* Prize Pool */}
          {tournament.prize_pool > 0 && (
            <div className="absolute bottom-4 left-4">
              <div className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-3 py-1 rounded-full text-sm font-bold shadow-lg">
                ${tournament.prize_pool.toLocaleString()}
              </div>
            </div>
          )}
        </div>

        <CardContent className="p-6 flex-1">
          {/* Tournament Name and Description */}
          <div className="mb-4">
            <h3 className="text-xl font-bold text-white group-hover:text-purple-300 transition-colors mb-2">
              {tournament.name}
            </h3>
            <p className="text-gray-300 text-sm line-clamp-2 group-hover:text-gray-200 transition-colors">
              {tournament.description}
            </p>
          </div>

          {/* Tournament Details */}
          <div className="space-y-3 mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Calendar className="w-4 h-4 text-purple-400" />
              </div>
              <div>
                <p className="text-xs text-gray-400">Start Date</p>
                <p className="text-sm font-semibold text-white">
                  {format(new Date(tournament.start_date), 'MMM dd, yyyy')}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Users className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <p className="text-xs text-gray-400">Participants</p>
                <p className="text-sm font-semibold text-white">
                  {tournament.current_participants || 0} / {tournament.max_participants || '∞'}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <Trophy className="w-4 h-4 text-green-400" />
              </div>
              <div>
                <p className="text-xs text-gray-400">Format</p>
                <p className="text-sm font-semibold text-white">
                  {tournament.format.replace('_', ' ').toUpperCase()}
                </p>
              </div>
            </div>

            {tournament.location && (
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-orange-500/20 rounded-lg">
                  <MapPin className="w-4 h-4 text-orange-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-400">Location</p>
                  <p className="text-sm font-semibold text-white">{tournament.location}</p>
                </div>
              </div>
            )}
          </div>

          {/* Registration Status */}
          {isRegistrationOpen && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400 font-medium">
                  Registration open until {format(new Date(tournament.registration_deadline), 'MMM dd, yyyy')}
                </span>
              </div>
            </div>
          )}

          {/* Features */}
          <div className="flex flex-wrap gap-2">
            <span className={`px-2 py-1 text-xs rounded-full ${getFormatColor(tournament.format)}`}>
              {tournament.format.replace('_', ' ').toUpperCase()}
            </span>
            {tournament.is_online && (
              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                Online
              </span>
            )}
            {tournament.requires_team && (
              <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded-full">
                Team Required
              </span>
            )}
          </div>
        </CardContent>

        {showActions && (
          <CardFooter className="px-6 pb-6 pt-0">
            <div className="flex space-x-2 w-full">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onView?.(tournament.id)}
                className="flex-1 bg-gray-700 border-gray-600 text-white hover:bg-purple-600 hover:border-purple-500 transition-all duration-300"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                View Details
              </Button>
              {isRegistrationOpen && !isJoined && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => onJoin?.(tournament.id)}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Join Tournament
                </Button>
              )}
              {isJoined && (
                <Button
                  variant="primary"
                  size="sm"
                  disabled
                  className="flex-1 bg-green-600 text-white"
                >
                  <Star className="w-4 h-4 mr-2" />
                  Joined
                </Button>
              )}
            </div>
          </CardFooter>
        )}
      </Card>
    </motion.div>
  );
};