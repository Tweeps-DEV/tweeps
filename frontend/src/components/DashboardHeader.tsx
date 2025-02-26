import { useState, useEffect, useRef } from 'react';
import { ShoppingCart, LogOut, User, Settings, ChevronDown, Home, ShoppingBag } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { toast } from '@/components/ui/use-toast';
import { logout, getUserData } from '@/lib/auth';

const DashboardHeader = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState<any>(null);
  const pathname = usePathname();
  const menuRef = useRef<HTMLDivElement>(null);

  const isHomePage = pathname === '/';

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const user = getUserData();
        setIsAuthenticated(!!user);
        setUserData(user);
      } catch (error) {
        console.error('Error checking authentication:', error);
      }
    };

    checkAuth();
  }, [pathname]);

  const handleLogout = async () => {
    try {
      await logout();
      setIsAuthenticated(false);
      setUserData(null);
      toast({
        title: 'Logged out successfully',
        description: 'You have been logged out of your account.',
      });
      
      window.location.href = '/login';
    } catch (error) {
      console.error('Error logging out:', error);
      toast({
        title: 'Error',
        description: 'Failed to log out. Please try again.',
        variant: 'destructive'
      });
    }
  };

  const getInitials = () => {
    if (userData && userData.name) {
      return userData.name.charAt(0).toUpperCase();
    }
    return "U";
  };

  return (
    <>
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Link href="/dashboard" className="block">
                <Image 
                  src="/tweeps-logo.svg"
                  alt="Tweeps Logo"
                  width={50}
                  height={50}
                  className="cursor-pointer"
                />
              </Link>
            </div>

            {isAuthenticated && !isHomePage && (
              <div className="flex items-center space-x-3">
                <Link href="/cart" className="p-2 rounded-lg hover:bg-gray-100 relative">
                  <ShoppingCart className="h-6 w-6 text-gray-600" />
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center shadow-sm">
                    {0}
                  </span>
                </Link>
                
                {/* Profile Avatar Button */}
                <div className="relative" ref={menuRef}>
                  <button 
                    className="flex items-center space-x-1 rounded-full hover:bg-gray-100 p-1 focus:outline-none"
                    onClick={() => setIsMenuOpen(!isMenuOpen)}
                  >
                    <div className="w-8 h-8 bg-[#f2ae2a] rounded-full flex items-center justify-center text-white font-semibold">
                      {getInitials()}
                    </div>
                    <ChevronDown className="h-4 w-4 text-gray-500" />
                  </button>
                  
                  <AnimatePresence>
                    {isMenuOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.1 }}
                        className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg py-2 z-50 border border-gray-200"
                      >
                        {/* User info */}
                        <div className="px-4 py-3 border-b border-gray-100">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-[#f2ae2a] rounded-full flex items-center justify-center text-white font-semibold">
                              {getInitials()}
                            </div>
                            <div className="overflow-hidden">
                              <p className="font-medium truncate">{userData?.name || "User"}</p>
                              <p className="text-sm text-gray-500 truncate">{userData?.email || ""}</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="py-1">
                          <Link 
                            href="/dashboard"
                            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            onClick={() => setIsMenuOpen(false)}
                          >
                            <Home className="h-4 w-4 mr-3 text-gray-500" />
                            <span>Home</span>
                          </Link>
                          
                          <Link 
                            href="/profile"
                            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            onClick={() => setIsMenuOpen(false)}
                          >
                            <User className="h-4 w-4 mr-3 text-gray-500" />
                            <span>Profile</span>
                          </Link>
                          
                          <Link 
                            href="/settings"
                            className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            onClick={() => setIsMenuOpen(false)}
                          >
                            <Settings className="h-4 w-4 mr-3 text-gray-500" />
                            <span>Settings</span>
                          </Link>
                          
                          <div className="border-t border-gray-100 my-1"></div>
                          
                          <button 
                            onClick={() => {
                              handleLogout();
                              setIsMenuOpen(false);
                            }}
                            className="flex items-center px-4 py-2 text-sm text-red-600 hover:bg-gray-100 w-full text-left"
                          >
                            <LogOut className="h-4 w-4 mr-3" />
                            <span>Logout</span>
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>
    </>
  );
};

export default DashboardHeader;
