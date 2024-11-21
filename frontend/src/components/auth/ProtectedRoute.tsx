'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, tokens } = useAuth();
  const [authStatus, setAuthStatus] = useState<'loading' | 'authenticated' | 'unauthenticated'>('loading');

  useEffect(() => {
    if (isLoading) {
      setAuthStatus('loading');
    } else if (isAuthenticated) {
      setAuthStatus('authenticated');
      console.log('ProtectedRoute: Authenticated', tokens);
    } else {
      setAuthStatus('unauthenticated');
      console.log('ProtectedRoute: Unauthenticated');
    }
  }, [isLoading, isAuthenticated, tokens]);
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (authStatus === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#f2ae2a]" />
      </div>
    );
  }

  if (authStatus === 'unauthenticated') {
    console.log('Redirecting to /login');
    return null; // Or a loading indicator if you prefer
  }

  return <>{children}</>;
}
