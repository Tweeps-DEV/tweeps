'use client';
import { useState, useEffect } from 'react';
import { getUserName } from '@/lib/auth';

export default function DashboardGreeting() {
  const [greeting, setGreeting] = useState('Hello');
  const [userName, setUserName] = useState('Guest');

  useEffect(() => {
    setUserName(getUserName());
    setGreeting(getGreeting());
  }, []);
  
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-bold text-gray-900">
        {greeting}, {userName} 👋
      </h1>
      <p className="text-gray-500 text-sm">
        What would you like to order today?
      </p>
    </div>
  );
}
