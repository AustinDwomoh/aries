import { create } from 'zustand';
import { Tournament, TournamentFilters } from '@/types';
import { apiService } from '@/services/api';

interface TournamentState {
  tournaments: Tournament[];
  currentTournament: Tournament | null;
  isLoading: boolean;
  error: string | null;
  filters: TournamentFilters;
  pagination: {
    page: number;
    totalPages: number;
    totalCount: number;
  };
}

interface TournamentActions {
  fetchTournaments: (filters?: TournamentFilters, page?: number) => Promise<void>;
  fetchTournament: (id: number) => Promise<void>;
  createTournament: (tournamentData: any) => Promise<void>;
  updateTournament: (id: number, tournamentData: any) => Promise<void>;
  deleteTournament: (id: number) => Promise<void>;
  joinTournament: (id: number) => Promise<void>;
  leaveTournament: (id: number) => Promise<void>;
  updateMatchResult: (tournamentId: number, matchId: number, result: any) => Promise<void>;
  setCurrentTournament: (tournament: Tournament | null) => void;
  setFilters: (filters: TournamentFilters) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

type TournamentStore = TournamentState & TournamentActions;

export const useTournamentStore = create<TournamentStore>((set, get) => ({
  // Initial state
  tournaments: [],
  currentTournament: null,
  isLoading: false,
  error: null,
  filters: {},
  pagination: {
    page: 1,
    totalPages: 0,
    totalCount: 0,
  },

  // Actions
  fetchTournaments: async (filters = {}, page = 1) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.getTournaments(filters, page);
      
      set({
        tournaments: response.results,
        pagination: {
          page: response.page,
          totalPages: response.total_pages,
          totalCount: response.count,
        },
        filters,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to fetch tournaments', 
        isLoading: false 
      });
    }
  },

  fetchTournament: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.getTournament(id);
      
      if (response.success) {
        set({
          currentTournament: response.data,
          isLoading: false,
          error: null,
        });
      } else {
        set({ error: response.message || 'Failed to fetch tournament', isLoading: false });
      }
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to fetch tournament', 
        isLoading: false 
      });
    }
  },

  createTournament: async (tournamentData: any) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.createTournament(tournamentData);
      
      if (response.success) {
        const { tournaments } = get();
        set({
          tournaments: [response.data, ...tournaments],
          currentTournament: response.data,
          isLoading: false,
          error: null,
        });
      } else {
        set({ error: response.message || 'Failed to create tournament', isLoading: false });
      }
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to create tournament', 
        isLoading: false 
      });
    }
  },

  updateTournament: async (id: number, tournamentData: any) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.updateTournament(id, tournamentData);
      
      if (response.success) {
        const { tournaments, currentTournament } = get();
        const updatedTournaments = tournaments.map(tournament => 
          tournament.id === id ? response.data : tournament
        );
        
        set({
          tournaments: updatedTournaments,
          currentTournament: currentTournament?.id === id ? response.data : currentTournament,
          isLoading: false,
          error: null,
        });
      } else {
        set({ error: response.message || 'Failed to update tournament', isLoading: false });
      }
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to update tournament', 
        isLoading: false 
      });
    }
  },

  deleteTournament: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiService.deleteTournament(id);
      
      const { tournaments, currentTournament } = get();
      const updatedTournaments = tournaments.filter(tournament => tournament.id !== id);
      
      set({
        tournaments: updatedTournaments,
        currentTournament: currentTournament?.id === id ? null : currentTournament,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to delete tournament', 
        isLoading: false 
      });
    }
  },

  joinTournament: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.joinTournament(id);
      
      if (response.success) {
        // Refresh the tournament data to get updated participant status
        await get().fetchTournament(id);
        set({ isLoading: false, error: null });
      } else {
        set({ error: response.message || 'Failed to join tournament', isLoading: false });
      }
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to join tournament', 
        isLoading: false 
      });
    }
  },

  leaveTournament: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiService.leaveTournament(id);
      
      // Refresh the tournament data to get updated participant status
      await get().fetchTournament(id);
      set({ isLoading: false, error: null });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to leave tournament', 
        isLoading: false 
      });
    }
  },

  updateMatchResult: async (tournamentId: number, matchId: number, result: any) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.updateMatchResult(tournamentId, matchId, result);
      
      if (response.success) {
        // Refresh the tournament data to get updated match results
        await get().fetchTournament(tournamentId);
        set({ isLoading: false, error: null });
      } else {
        set({ error: response.message || 'Failed to update match result', isLoading: false });
      }
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to update match result', 
        isLoading: false 
      });
    }
  },

  setCurrentTournament: (tournament: Tournament | null) => {
    set({ currentTournament: tournament });
  },

  setFilters: (filters: TournamentFilters) => {
    set({ filters });
  },

  clearError: () => set({ error: null }),
  setLoading: (loading: boolean) => set({ isLoading: loading }),
}));
