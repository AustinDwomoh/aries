import React from 'react';
import { motion } from 'framer-motion';
import { Users, MapPin, Trophy, Star, ExternalLink, Crown, Zap, Flame, Target, Shield, CheckCircle } from 'lucide-react';
import { Organization } from '@/types';
import { Card, CardContent, CardFooter } from './ui/Card';
import { Button } from './ui/Button';

interface OrganizationCardProps {
  organization: Organization;
  onView?: (id: number) => void;
  onFollow?: (id: number) => void;
  showActions?: boolean;
}

export const OrganizationCard: React.FC<OrganizationCardProps> = ({
  organization,
  onView,
  onFollow,
  showActions = true,
}) => {

  const getTypeColor = (type: string) => {
    const colors = {
      esports_company: 'bg-gradient-to-r from-purple-500 to-purple-600 text-white',
      tournament_organizer: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white',
      gaming_community: 'bg-gradient-to-r from-green-500 to-green-600 text-white',
      event_company: 'bg-gradient-to-r from-orange-500 to-orange-600 text-white',
      sponsor: 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-white',
      media_company: 'bg-gradient-to-r from-pink-500 to-pink-600 text-white',
    };
    return colors[type as keyof typeof colors] || 'bg-gradient-to-r from-gray-500 to-gray-600 text-white';
  };

  const getTypeIcon = (type: string) => {
    const icons = {
      esports_company: Crown,
      tournament_organizer: Trophy,
      gaming_community: Users,
      event_company: Target,
      sponsor: Star,
      media_company: Zap,
    };
    return icons[type as keyof typeof icons] || Shield;
  };

  const TypeIcon = getTypeIcon(organization.organization_type);

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
          </div>
          <div className="absolute -bottom-8 left-6">
            <div className="w-16 h-16 rounded-full border-4 border-purple-500 overflow-hidden bg-gray-800 shadow-xl group-hover:scale-110 transition-transform duration-300">
              <img
                src={organization.logo}
                alt={organization.name}
                className="w-full h-full object-cover"
              />
            </div>
          </div>
          <div className="absolute top-4 right-4">
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getTypeColor(organization.organization_type)} flex items-center space-x-1`}>
              <TypeIcon className="w-3 h-3" />
              <span>{organization.organization_type.replace('_', ' ').toUpperCase()}</span>
            </div>
          </div>
          {organization.is_verified && (
            <div className="absolute top-4 left-4">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center shadow-lg">
                <CheckCircle className="w-5 h-5 text-white" />
              </div>
            </div>
          )}
        </div>

        <CardContent className="pt-12 px-6 pb-4 flex-1">
          {/* Organization Name and Description */}
          <div className="mb-4">
            <h3 className="text-xl font-bold text-white group-hover:text-purple-300 transition-colors mb-2">
              {organization.name}
            </h3>
            <p className="text-gray-300 text-sm line-clamp-2 group-hover:text-gray-200 transition-colors">
              {organization.description}
            </p>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Users className="w-4 h-4 text-purple-400" />
              </div>
              <div>
                <p className="text-xs text-gray-400">Members</p>
                <p className="text-sm font-semibold text-white">{organization.member_count || 0}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Trophy className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <p className="text-xs text-gray-400">Tournaments</p>
                <p className="text-sm font-semibold text-white">{organization.tournaments_hosted || 0}</p>
              </div>
            </div>
          </div>

          {/* Location */}
          {organization.location && (
            <div className="flex items-center space-x-2 mb-4">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-300">{organization.location}</span>
            </div>
          )}

          {/* Reputation Score */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Reputation</span>
              <span className="text-sm font-semibold text-purple-400">
                {organization.reputation_score || 0}/100
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(organization.reputation_score || 0)}%` }}
              ></div>
            </div>
          </div>

          {/* Features */}
          <div className="flex flex-wrap gap-2 mb-4">
            {organization.can_host_tournaments && (
              <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                Tournament Host
              </span>
            )}
            {organization.business_license && (
              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                Licensed
              </span>
            )}
            {organization.total_prize_money_distributed > 0 && (
              <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-full">
                Prize Pool: ${organization.total_prize_money_distributed.toLocaleString()}
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
                onClick={() => onView?.(organization.id)}
                className="flex-1 bg-gray-700 border-gray-600 text-white hover:bg-purple-600 hover:border-purple-500 transition-all duration-300"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                View Details
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => onFollow?.(organization.id)}
                className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg"
              >
                <Star className="w-4 h-4 mr-2" />
                Follow
              </Button>
            </div>
          </CardFooter>
        )}
      </Card>
    </motion.div>
  );
};