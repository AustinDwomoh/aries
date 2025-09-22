// Base types
export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at: string;
}

// User and Profile types
export interface User extends BaseEntity {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  last_login: string | null;
}

export interface Profile extends BaseEntity {
  user: User;
  profile_picture: string;
  role: 'admin' | 'captain' | 'member';
  is_organizer: boolean;
  phone?: string;
  is_verified: boolean;
  clan?: Clan;
  social_links: SocialLink[];
  stats?: PlayerStats;
}

export interface PlayerStats extends BaseEntity {
  user_profile: number;
  achievements: Record<string, any>;
  rank: 'rookie' | 'prodigy' | 'veteran' | 'legend' | 'superstar' | 'elite' | 'mvp' | 'world_class';
  total_matches: number;
  win_rate: number;
  total_wins: number;
  total_losses: number;
  total_draws: number;
  gd: number; // Goal difference
  gf: number; // Goals for
  ga: number; // Goals against
  elo_rating: number;
  season: string;
  match_data: Record<string, any>;
}

// Organization types (pure organizers)
export interface Organization extends BaseEntity {
  name: string;
  tag: string;
  email: string;
  description: string;
  logo: string;
  profile_picture: string;
  website?: string;
  primary_game?: string;
  other_games?: string;
  country: string;
  is_verified: boolean;
  created_by: number;
  is_active: boolean;
  is_staff: boolean;
  organization_type: 'esports_company' | 'tournament_organizer' | 'gaming_community' | 'event_company' | 'sponsor' | 'media_company';
  
  // Organizer capabilities
  can_host_tournaments: boolean;
  can_sponsor_events: boolean;
  can_manage_prizes: boolean;
  can_verify_teams: boolean;
  
  // Business information
  business_license?: string;
  tax_id?: string;
  contact_phone?: string;
  established_date?: string;
  
  // Financial information
  total_prize_money_distributed: number;
  total_tournaments_hosted: number;
  average_tournament_size: number;
  
  social_links: OrganizationSocialLink[];
  reputation?: OrganizationReputation;
  members: OrganizationMember[];
}

// Clan types (gaming teams that participate)
export interface Clan extends BaseEntity {
  name: string;
  tag: string;
  email: string;
  description: string;
  logo: string;
  profile_picture: string;
  website?: string;
  primary_game?: string;
  other_games?: string;
  country: string;
  is_recruiting: boolean;
  recruitment_requirements?: string;
  is_verified: boolean;
  created_by: number;
  is_active: boolean;
  is_staff: boolean;
  social_links: ClanSocialLink[];
  stats?: ClanStats;
  members: ClanMember[];
}

export interface ClanStats extends BaseEntity {
  clan: number;
  total_matches: number;
  win_rate: number;
  total_wins: number;
  total_losses: number;
  total_draws: number;
  rank: 'bronze' | 'silver' | 'gold' | 'platinum' | 'diamond' | 'master' | 'grandmaster' | 'champion' | 'invincible';
  player_scored: number;
  player_conceded: number;
  gd: number;
  gf: number;
  ga: number;
  average_team_score: number;
  achievements: Record<string, any>;
  elo_rating: number;
  match_data: Record<string, any>;
}

export interface ClanMember extends BaseEntity {
  clan: number;
  user: User;
  role: 'leader' | 'captain' | 'member' | 'recruit';
  joined_at: string;
  is_active: boolean;
}

export interface ClanJoinRequest extends BaseEntity {
  user: User;
  clan: number;
  status: 'pending' | 'approved' | 'rejected';
  requested_at: string;
  message?: string;
}

export interface ClanSocialLink extends BaseEntity {
  clan: number;
  link_type: 'discord' | 'whatsapp' | 'x' | 'instagram' | 'tiktok' | 'youtube' | 'twitch' | 'website' | 'other';
  url: string;
}

// Organization reputation (not stats)
export interface OrganizationReputation extends BaseEntity {
  organization: number;
  reputation_score: number;
  total_events_organized: number;
  total_participants_reached: number;
  average_event_rating: number;
  total_prize_money_distributed: number;
  total_revenue_generated: number;
  on_time_completion_rate: number;
  participant_satisfaction: number;
  dispute_resolution_rate: number;
  achievements: string[];
  badges: string[];
  is_verified_organizer: boolean;
  verification_level: 'basic' | 'verified' | 'premium' | 'elite';
}

export interface OrganizationMember extends BaseEntity {
  organization: number;
  user: User;
  role: 'admin' | 'captain' | 'member' | 'recruit';
  joined_at: string;
  is_active: boolean;
}

export interface OrganizationJoinRequest extends BaseEntity {
  user: User;
  organization: number;
  status: 'pending' | 'approved' | 'rejected';
  requested_at: string;
  message?: string;
}

// Social Links
export interface SocialLink extends BaseEntity {
  profile: number;
  link_type: 'discord' | 'whatsapp' | 'x' | 'instagram' | 'tiktok' | 'youtube' | 'twitch' | 'website' | 'other';
  url: string;
}

export interface OrganizationSocialLink extends BaseEntity {
  organization: number;
  link_type: 'discord' | 'whatsapp' | 'x' | 'instagram' | 'tiktok' | 'youtube' | 'twitch' | 'website' | 'other';
  url: string;
}

// Tournament types
export interface Tournament extends BaseEntity {
  name: string;
  description?: string;
  created_by: User;
  organizer: Organization;  // Organizations organize tournaments
  logo: string;
  tournament_type: 'individual' | 'clan';
  tour_format: 'league' | 'cup' | 'groups_knockout';
  status: 'upcoming' | 'ongoing' | 'completed' | 'cancelled';
  start_date: string;
  end_date?: string;
  max_participants?: number;
  entry_fee?: number;
  prize_pool?: number;
  home_or_away: boolean;
  participants: TournamentParticipant[];
  matches: Match[];
}

export interface TournamentParticipant extends BaseEntity {
  tournament: number;
  user?: User;  // For individual tournaments
  clan?: Clan;  // For clan tournaments
  joined_at: string;
  status: 'active' | 'eliminated' | 'withdrawn';
}

export interface Match extends BaseEntity {
  tournament: number;
  round: number;
  home_participant: number;
  away_participant: number;
  home_score?: number;
  away_score?: number;
  status: 'scheduled' | 'ongoing' | 'completed' | 'cancelled';
  scheduled_at: string;
  completed_at?: string;
  is_knockout: boolean;
  knockout_stage?: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
  page: number;
  total_pages: number;
}

// Form types
export interface LoginForm {
  username: string;
  password: string;
  remember_me: boolean;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
  confirm_password: string;
  first_name: string;
  last_name: string;
}

export interface OrganizationForm {
  name: string;
  tag: string;
  email: string;
  description: string;
  website?: string;
  primary_game?: string;
  other_games?: string;
  country: string;
  organization_type: 'esports_company' | 'tournament_organizer' | 'gaming_community' | 'event_company' | 'sponsor' | 'media_company';
}

export interface ClanForm {
  name: string;
  tag: string;
  email: string;
  description: string;
  website?: string;
  primary_game?: string;
  other_games?: string;
  country: string;
  is_recruiting: boolean;
  recruitment_requirements?: string;
}

export interface TournamentForm {
  name: string;
  description?: string;
  tournament_type: 'individual' | 'clan';
  tour_format: 'league' | 'cup' | 'groups_knockout';
  start_date: string;
  end_date?: string;
  max_participants?: number;
  entry_fee?: number;
  prize_pool?: number;
  home_or_away: boolean;
}

// UI State types
export interface AuthState {
  user: User | null;
  profile: Profile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface OrganizationState {
  currentOrganization: Organization | null;
  organizations: Organization[];
  isLoading: boolean;
  error: string | null;
}

export interface ClanState {
  currentClan: Clan | null;
  clans: Clan[];
  isLoading: boolean;
  error: string | null;
}

export interface TournamentState {
  tournaments: Tournament[];
  currentTournament: Tournament | null;
  isLoading: boolean;
  error: string | null;
}

// Component Props types
export interface CardProps {
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
  hover?: boolean;
}

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

// Filter and Search types
export interface OrganizationFilters {
  organization_type?: string;
  country?: string;
  is_verified?: boolean;
  search?: string;
}

export interface ClanFilters {
  country?: string;
  is_recruiting?: boolean;
  is_verified?: boolean;
  primary_game?: string;
  search?: string;
}

export interface TournamentFilters {
  tournament_type?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
}

// Notification types
export interface Notification extends BaseEntity {
  user: number;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  is_read: boolean;
  action_url?: string;
}