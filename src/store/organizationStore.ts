import { create } from 'zustand';
import { Organization, OrganizationFilters } from '@/types';
import { apiService } from '@/services/api';

interface OrganizationState {
  organizations: Organization[];
  currentOrganization: Organization | null;
  isLoading: boolean;
  error: string | null;
  filters: OrganizationFilters;
  pagination: {
    page: number;
    totalPages: number;
    totalCount: number;
  };
}

interface OrganizationActions {
  fetchOrganizations: (filters?: OrganizationFilters, page?: number) => Promise<void>;
  fetchOrganization: (id: number) => Promise<void>;
  createOrganization: (organizationData: any) => Promise<void>;
  updateOrganization: (id: number, organizationData: any) => Promise<void>;
  deleteOrganization: (id: number) => Promise<void>;
  joinOrganization: (id: number, message?: string) => Promise<void>;
  leaveOrganization: (id: number) => Promise<void>;
  setCurrentOrganization: (organization: Organization | null) => void;
  setFilters: (filters: OrganizationFilters) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

type OrganizationStore = OrganizationState & OrganizationActions;

export const useOrganizationStore = create<OrganizationStore>((set, get) => ({
  // Initial state
  organizations: [],
  currentOrganization: null,
  isLoading: false,
  error: null,
  filters: {},
  pagination: {
    page: 1,
    totalPages: 0,
    totalCount: 0,
  },

  // Actions
  fetchOrganizations: async (filters = {}, page = 1) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.getOrganizations(filters, page);
      
      set({
        organizations: response.results,
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
        error: error.response?.data?.message || 'Failed to fetch organizations', 
        isLoading: false 
      });
    }
  },

  fetchOrganization: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.getOrganization(id);
      
      if (response.success) {
        set({
          currentOrganization: response.data,
          isLoading: false,
          error: null,
        });
      } else {
        set({ error: response.message || 'Failed to fetch organization', isLoading: false });
      }
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to fetch organization', 
        isLoading: false 
      });
    }
  },

  createOrganization: async (organizationData: any) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.createOrganization(organizationData);
      
      if (response.success) {
        const { organizations } = get();
        set({
          organizations: [response.data, ...organizations],
          currentOrganization: response.data,
          isLoading: false,
          error: null,
        });
      } else {
        set({ error: response.message || 'Failed to create organization', isLoading: false });
      }
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to create organization', 
        isLoading: false 
      });
    }
  },

  updateOrganization: async (id: number, organizationData: any) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.updateOrganization(id, organizationData);
      
      if (response.success) {
        const { organizations, currentOrganization } = get();
        const updatedOrganizations = organizations.map(org => 
          org.id === id ? response.data : org
        );
        
        set({
          organizations: updatedOrganizations,
          currentOrganization: currentOrganization?.id === id ? response.data : currentOrganization,
          isLoading: false,
          error: null,
        });
      } else {
        set({ error: response.message || 'Failed to update organization', isLoading: false });
      }
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to update organization', 
        isLoading: false 
      });
    }
  },

  deleteOrganization: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiService.deleteOrganization(id);
      
      const { organizations, currentOrganization } = get();
      const updatedOrganizations = organizations.filter(org => org.id !== id);
      
      set({
        organizations: updatedOrganizations,
        currentOrganization: currentOrganization?.id === id ? null : currentOrganization,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to delete organization', 
        isLoading: false 
      });
    }
  },

  joinOrganization: async (id: number, message?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.joinOrganization(id, message);
      
      if (response.success) {
        // Refresh the organization data to get updated member status
        await get().fetchOrganization(id);
        set({ isLoading: false, error: null });
      } else {
        set({ error: response.message || 'Failed to join organization', isLoading: false });
      }
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to join organization', 
        isLoading: false 
      });
    }
  },

  leaveOrganization: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiService.leaveOrganization(id);
      
      // Refresh the organization data to get updated member status
      await get().fetchOrganization(id);
      set({ isLoading: false, error: null });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to leave organization', 
        isLoading: false 
      });
    }
  },

  setCurrentOrganization: (organization: Organization | null) => {
    set({ currentOrganization: organization });
  },

  setFilters: (filters: OrganizationFilters) => {
    set({ filters });
  },

  clearError: () => set({ error: null }),
  setLoading: (loading: boolean) => set({ isLoading: loading }),
}));
