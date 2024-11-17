'use client';
import { useAuth } from '@/contexts/auth-context';

export default function DashboardGreeting() {
  const { user } = useAuth();
  
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-bold text-gray-900">
        {getGreeting()}, {user?.name || 'Guest'} 👋
      </h1>
      <p className="text-gray-500 text-sm">
        What would you like to order today?
      </p>
    </div>
  );
}
