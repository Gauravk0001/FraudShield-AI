import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import type { User } from '../../types';
import { apiRequest } from '../../services/api';

export const Layout: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    apiRequest<User>('/auth/me')
      .then((data) => setUser(data))
      .catch(() => {});
  }, []);

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900 font-sans">
      <Sidebar userRole={user?.role} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header user={user} />
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet context={{ user }} />
        </main>
      </div>
    </div>
  );
};
