import axios, { AxiosInstance } from 'axios';
import { 
  User, 
  Profile, 
  Organization, 
  Tournament, 
  ApiResponse, 
  PaginatedResponse,
  LoginForm,
  RegisterForm,
  OrganizationForm,
  TournamentForm,
  OrganizationFilters,
  TournamentFilters
} from '@/types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginForm): Promise<ApiResponse<{ user: User; profile: Profile; token: string }>> {
    const response = await this.api.post('/auth/login/', credentials);
    return response.data;
  }

  async register(userData: RegisterForm): Promise<ApiResponse<{ user: User; profile: Profile; token: string }>> {
    const response = await this.api.post('/auth/register/', userData);
    return response.data;
  }

  async logout(): Promise<void> {
    await this.api.post('/auth/logout/');
    localStorage.removeItem('auth_token');
  }

  async getCurrentUser(): Promise<ApiResponse<{ user: User; profile: Profile }>> {
    const response = await this.api.get('/auth/me/');
    return response.data;
  }

  // Organization endpoints
  async getOrganizations(filters?: OrganizationFilters, page = 1): Promise<PaginatedResponse<Organization>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, value.toString());
        }
      });
    }
    params.append('page', page.toString());

    const response = await this.api.get(`/organizations/?${params.toString()}`);
    return response.data;
  }

  async getOrganization(id: number): Promise<ApiResponse<Organization>> {
    const response = await this.api.get(`/organizations/${id}/`);
    return response.data;
  }

  async createOrganization(organizationData: OrganizationForm): Promise<ApiResponse<Organization>> {
    const response = await this.api.post('/organizations/', organizationData);
    return response.data;
  }

  async updateOrganization(id: number, organizationData: Partial<OrganizationForm>): Promise<ApiResponse<Organization>> {
    const response = await this.api.patch(`/organizations/${id}/`, organizationData);
    return response.data;
  }

  async deleteOrganization(id: number): Promise<void> {
    await this.api.delete(`/organizations/${id}/`);
  }

  async joinOrganization(id: number, message?: string): Promise<ApiResponse<void>> {
    const response = await this.api.post(`/organizations/${id}/join/`, { message });
    return response.data;
  }

  async leaveOrganization(id: number): Promise<void> {
    await this.api.post(`/organizations/${id}/leave/`);
  }

  async getOrganizationMembers(id: number): Promise<ApiResponse<Organization[]>> {
    const response = await this.api.get(`/organizations/${id}/members/`);
    return response.data;
  }

  async updateMemberRole(organizationId: number, userId: number, role: string): Promise<ApiResponse<void>> {
    const response = await this.api.patch(`/organizations/${organizationId}/members/${userId}/`, { role });
    return response.data;
  }

  async removeMember(organizationId: number, userId: number): Promise<void> {
    await this.api.delete(`/organizations/${organizationId}/members/${userId}/`);
  }

  // Tournament endpoints
  async getTournaments(filters?: TournamentFilters, page = 1): Promise<PaginatedResponse<Tournament>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, value.toString());
        }
      });
    }
    params.append('page', page.toString());

    const response = await this.api.get(`/tournaments/?${params.toString()}`);
    return response.data;
  }

  async getTournament(id: number): Promise<ApiResponse<Tournament>> {
    const response = await this.api.get(`/tournaments/${id}/`);
    return response.data;
  }

  async createTournament(tournamentData: TournamentForm): Promise<ApiResponse<Tournament>> {
    const response = await this.api.post('/tournaments/', tournamentData);
    return response.data;
  }

  async updateTournament(id: number, tournamentData: Partial<TournamentForm>): Promise<ApiResponse<Tournament>> {
    const response = await this.api.patch(`/tournaments/${id}/`, tournamentData);
    return response.data;
  }

  async deleteTournament(id: number): Promise<void> {
    await this.api.delete(`/tournaments/${id}/`);
  }

  async joinTournament(id: number): Promise<ApiResponse<void>> {
    const response = await this.api.post(`/tournaments/${id}/join/`);
    return response.data;
  }

  async leaveTournament(id: number): Promise<void> {
    await this.api.post(`/tournaments/${id}/leave/`);
  }

  async getTournamentMatches(id: number): Promise<ApiResponse<any[]>> {
    const response = await this.api.get(`/tournaments/${id}/matches/`);
    return response.data;
  }

  async updateMatchResult(tournamentId: number, matchId: number, result: any): Promise<ApiResponse<void>> {
    const response = await this.api.patch(`/tournaments/${tournamentId}/matches/${matchId}/`, result);
    return response.data;
  }

  // User endpoints
  async getUserProfile(userId: number): Promise<ApiResponse<Profile>> {
    const response = await this.api.get(`/users/${userId}/profile/`);
    return response.data;
  }

  async updateUserProfile(userId: number, profileData: Partial<Profile>): Promise<ApiResponse<Profile>> {
    const response = await this.api.patch(`/users/${userId}/profile/`, profileData);
    return response.data;
  }

  async followUser(userId: number): Promise<ApiResponse<void>> {
    const response = await this.api.post(`/users/${userId}/follow/`);
    return response.data;
  }

  async unfollowUser(userId: number): Promise<void> {
    await this.api.post(`/users/${userId}/unfollow/`);
  }

  async followOrganization(organizationId: number): Promise<ApiResponse<void>> {
    const response = await this.api.post(`/organizations/${organizationId}/follow/`);
    return response.data;
  }

  async unfollowOrganization(organizationId: number): Promise<void> {
    await this.api.post(`/organizations/${organizationId}/unfollow/`);
  }

  // File upload
  async uploadFile(file: File, type: 'profile' | 'organization' | 'tournament'): Promise<ApiResponse<{ url: string }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const response = await this.api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
