import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthUser } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isLoadingAuth: boolean;
  login: (userId: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      const savedUser = localStorage.getItem('kavach_user');
      if (!savedUser) return null;
      const parsed = JSON.parse(savedUser);
      return (parsed?.user || parsed) as AuthUser;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState<string | null>(() => {
    try {
      return localStorage.getItem('kavach_token');
    } catch {
      return null;
    }
  });

  const [isLoadingAuth, setIsLoadingAuth] = useState<boolean>(true);

  const logout = () => {
    try {
      api.logout().catch(() => {});
    } finally {
      localStorage.removeItem('kavach_token');
      localStorage.removeItem('kavach_user');
      setToken(null);
      setUser(null);
    }
  };

  useEffect(() => {
    const handleUnauthorized = () => {
      logout();
    };

    window.addEventListener('kavach_unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('kavach_unauthorized', handleUnauthorized);
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const verifySession = async () => {
      const storedToken = localStorage.getItem('kavach_token');
      if (!storedToken) {
        if (isMounted) {
          setIsLoadingAuth(false);
        }
        return;
      }

      try {
        const rawUser = await api.getMe();
        const currentUser = ((rawUser as any)?.user || rawUser) as AuthUser;
        if (isMounted) {
          setUser(currentUser);
          localStorage.setItem('kavach_user', JSON.stringify(currentUser));
        }
      } catch (err) {
        if (isMounted) {
          localStorage.removeItem('kavach_token');
          localStorage.removeItem('kavach_user');
          setToken(null);
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setIsLoadingAuth(false);
        }
      }
    };

    verifySession();
    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (userId: string, password: string) => {
    const cleanId = userId.trim().toUpperCase();
    const res = await api.login(cleanId, password);
    localStorage.setItem('kavach_token', res.access_token);
    localStorage.setItem('kavach_user', JSON.stringify(res.user));
    setToken(res.access_token);
    setUser(res.user);
  };

  const isAdmin = user?.role === 'admin' || user?.id === 'ADMIN001';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isAdmin,
        isLoadingAuth,
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
