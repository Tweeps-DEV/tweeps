'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import DashboardGreeting from '@/components/dashboard/DashboardGreeting';
import { Search, Menu, ShoppingCart } from 'lucide-react';
import Link from 'next/link';
import { toast } from '@/components/ui/toast';
import { useAuth } from '@/contexts/auth-context';

// Types
interface MenuItem {
  id: string;
  name: string;
  price: number;
  image_url: string;
  description: string;
  category: string;
  preparation_time: number;
  is_available: boolean;
  calories: number;
}

interface Category {
  id: string;
  name: string;
  icon: string;
}

const CATEGORY_ICONS: Record<string, string> = {
  'Sushi': '🍣',
  'Ramen': '🍜',
  'Curry': '🍛',
  'Drinks': '🥤',
  'Desserts': '🍰',
  'default': '🍴'
};

const DashboardContent = () => {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoadingData, setIsLoadingData] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [menuResponse, categoryResponse] = await Promise.all([
          fetch('/api/menu-items'),
          fetch('/api/categories')
        ]);

        if (!menuResponse.ok || !categoryResponse.ok) {
          throw new Error('Failed to fetch data');
        }

        const menuData = await menuResponse.json();
        const categoryData = await categoryResponse.json();

        const categoriesWithIcons = categoryData.map((cat: { name: string }) => ({
          id: cat.name.toLowerCase(),
          name: cat.name,
          icon: CATEGORY_ICONS[cat.name] || CATEGORY_ICONS.default
        }));

        setMenuItems(menuData);
        setCategories(categoriesWithIcons);
      } catch (error) {
        console.error('Error fetching data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load menu items. Please try again later.',
          variant: 'destructive'
        });
      } finally {
        setIsLoadingData(false);
      }
    };

    fetchData();
  }, []);

  // Filter menu items based on search
  const filteredItems = menuItems.filter(item =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoadingData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#f2ae2a]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <button className="p-2 rounded-lg hover:bg-gray-100">
              <Menu className="h-6 w-6 text-gray-600" />
            </button>
            <Link href="/cart" className="p-2 rounded-lg hover:bg-gray-100 relative">
              <ShoppingCart className="h-6 w-6 text-gray-600" />
              <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                {0}
              </span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Welcome Banner */}
        <div className="mb-6">
          <DashboardGreeting />
        </div>

        {/* Search Bar */}
        <div className="relative mb-6">
          <input
            type="text"
            placeholder="Search menu items..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f2ae2a] focus:border-transparent"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        </div>

        {/* Categories */}
        <div className="mb-8">
          <div className="flex space-x-6 overflow-x-auto py-2 scrollbar-hide">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSearchQuery(category.name)}
                className="flex flex-col items-center space-y-1 min-w-[64px]"
              >
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center text-2xl">
                  {category.icon}
                </div>
                <span className="text-sm text-gray-600">{category.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Menu Items Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <img
                src={item.image_url || '/api/placeholder/320/240'}
                alt={item.name}
                className="w-full h-48 object-cover rounded-lg mb-4"
              />
              <div className="space-y-2">
                <h3 className="font-medium text-lg text-gray-900">{item.name}</h3>
                <p className="text-sm text-gray-500 line-clamp-2">{item.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-[#f2ae2a] font-semibold text-lg">
                    ${item.price.toFixed(2)}
                  </span>
                  <span className="text-sm text-gray-500">
                    {item.preparation_time} min
                  </span>
                </div>
                {item.calories && (
                  <span className="text-sm text-gray-500">
                    {item.calories} cal
                  </span>
                )}
                {!item.is_available && (
                  <div className="text-red-500 text-sm">Currently unavailable</div>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredItems.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No menu items found</p>
          </div>
        )}
      </main>
    </div>
  );
};


const DashboardPage = () => {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
};


export default DashboardPage;
