import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, Profile } from '@/types';
import { apiService } from '@/services/api';

interface AuthState {
  user: User | null;
  profile: Profile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  updateProfile: (profileData: Partial<Profile>) => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      profile: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await apiService.login({ 
            username: email, 
            password, 
            remember_me: false 
          });
          console.log(response);
          if (response.success) {
            localStorage.setItem('auth_token', response.data.token);
            set({
              user: response.data.user,
              profile: response.data.profile,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } else {
            set({ error: response.message || 'Login failed', isLoading: false });
          }
        } catch (error: any) {
          set({ 
            error: error.response?.data?.message || 'Login failed', 
            isLoading: false 
          });
        }
      },

      register: async (userData: any) => {
        set({ isLoading: true, error: null });
        try {
          const response = await apiService.register(userData);
          
          if (response.success) {
            localStorage.setItem('auth_token', response.data.token);
            set({
              user: response.data.user,
              profile: response.data.profile,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } else {
            set({ error: response.message || 'Registration failed', isLoading: false });
          }
        } catch (error: any) {
          set({ 
            error: error.response?.data?.message || 'Registration failed', 
            isLoading: false 
          });
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await apiService.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          set({
            user: null,
            profile: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      fetchCurrentUser: async () => {
        set({ isLoading: true });
        try {
          const response = await apiService.getCurrentUser();
          
          if (response.success) {
            set({
              user: response.data.user,
              profile: response.data.profile,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } else {
            set({ 
              isAuthenticated: false, 
              isLoading: false,
              error: response.message || 'Failed to fetch user data'
            });
          }
        } catch (error: any) {
          set({ 
            isAuthenticated: false, 
            isLoading: false,
            error: error.response?.data?.message || 'Failed to fetch user data'
          });
        }
      },

      updateProfile: async (profileData: Partial<Profile>) => {
        const { user } = get();
        if (!user) return;

        set({ isLoading: true });
        try {
          const response = await apiService.updateUserProfile(user.id, profileData);
          
          if (response.success) {
            set({
              profile: response.data,
              isLoading: false,
              error: null,
            });
          } else {
            set({ error: response.message || 'Profile update failed', isLoading: false });
          }
        } catch (error: any) {
          set({ 
            error: error.response?.data?.message || 'Profile update failed', 
            isLoading: false 
          });
        }
      },

      clearError: () => set({ error: null }),
      setLoading: (loading: boolean) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        profile: state.profile,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
