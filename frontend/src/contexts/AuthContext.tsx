import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, StoreWorkspace } from '../types';
import { getCurrentProfile, loginUser, registerUser, logoutUser } from '../services/api';

interface AuthContextType {
  user: User | null;
  stores: StoreWorkspace[];
  activeStore: StoreWorkspace | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string; store_name?: string; store_location?: string }) => Promise<void>;
  logout: () => Promise<void>;
  switchStore: (storeId: string) => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [stores, setStores] = useState<StoreWorkspace[]>([]);
  const [activeStore, setActiveStore] = useState<StoreWorkspace | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshProfile = async () => {
    try {
      const data = await getCurrentProfile();
      setUser(data.user);
      setStores(data.stores);

      const savedStoreId = localStorage.getItem('dukaandost_store_id');
      const found = data.stores.find((s) => s.store_id === savedStoreId) || data.stores[0] || null;
      setActiveStore(found);
      if (found) {
        localStorage.setItem('dukaandost_store_id', found.store_id);
      }
    } catch (err) {
      // Fallback demo user
      setUser({
        id: 1,
        email: 'owner@sharmastore.com',
        full_name: 'Sharma Ji',
        is_active: true
      });
      const defaultStore: StoreWorkspace = {
        store_id: 'STORE_001',
        name: 'Sharma General Store',
        location: 'Ranchi, Jharkhand',
        owner_name: 'Sharma Ji',
        role: 'OWNER',
        initial_net_income: 8000.0,
        target_net_income: 10000.0,
        current_net_income: 8000.0,
        simulated_net_income: 8000.0
      };
      setStores([defaultStore]);
      setActiveStore(defaultStore);
      localStorage.setItem('dukaandost_store_id', 'STORE_001');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshProfile();
  }, []);

  const login = async (email: string, pass: string) => {
    const res = await loginUser(email, pass);
    setUser(res.user);
    setStores(res.stores);
    if (res.stores.length > 0) {
      setActiveStore(res.stores[0]);
      localStorage.setItem('dukaandost_store_id', res.stores[0].store_id);
    }
  };

  const register = async (data: { email: string; password: string; full_name: string; store_name?: string }) => {
    const res = await registerUser(data);
    setUser(res.user);
    setStores(res.stores);
    if (res.stores.length > 0) {
      setActiveStore(res.stores[0]);
      localStorage.setItem('dukaandost_store_id', res.stores[0].store_id);
    }
  };

  const logout = async () => {
    await logoutUser();
    setUser(null);
    setStores([]);
    setActiveStore(null);
    localStorage.removeItem('dukaandost_token');
  };

  const switchStore = (storeId: string) => {
    const found = stores.find((s) => s.store_id === storeId);
    if (found) {
      setActiveStore(found);
      localStorage.setItem('dukaandost_store_id', found.store_id);
      window.location.reload();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        stores,
        activeStore,
        loading,
        login,
        register,
        logout,
        switchStore,
        refreshProfile
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
