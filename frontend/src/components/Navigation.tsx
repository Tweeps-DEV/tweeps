import { useState } from 'react';
import { Menu, Info, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/Button';
import Link from 'next/link';

const NAVIGATION_ITEMS = [
  { href: '#menu', text: 'Menu', icon: Menu },
  { href: '#about', text: 'About', icon: Info }
] as const;

interface NavigationProps {
  isAuthenticated: boolean;
  isMenuOpen: boolean;
  setIsMenuOpen: (isOpen: boolean) => void;
  onNavigate: (section: keyof typeof sectionRefs) => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  isAuthenticated,
  isMenuOpen,
  setIsMenuOpen,
  onNavigate
}) => {
  return (
    <>
      <div className="sticky top-0 z-50 bg-white">
        <nav className="py-6 px-4 lg:px-8">
          <div className="container mx-auto flex justify-between items-center">
            <div className="flex-shrink-0">
              <img src="/tweeps-logo.svg" alt="Tweeps Logo" className="h-12 w-auto" />
            </div>

            <div className="hidden lg:flex items-center space-x-12">
              <a href="#menu" className="text-gray-600 hover:text-[#f2ae2a] transition-colors">
                Menu
              </a>
              <a href="#about" className="text-gray-600 hover:text-[#f2ae2a] transition-colors">
                About
              </a>
              {isAuthenticated ? (
                <Button variant="secondary" size="sm">
                  Logout
                </Button>
              ) : (
                <Link href="/login" passHref>
                  <Button variant="primary" size="sm">
                    Login
                  </Button>
                </Link>
              )}
            </div>

            <motion.button
              className="lg:hidden text-gray-600 hover:text-[#f2ae2a] z-50"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              initial={false}
              animate={{ rotate: isMenuOpen ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              <motion.div
                animate={{ opacity: isMenuOpen ? 0 : 1 }}
                transition={{ duration: 0.2 }}
              >
                <Menu size={24} />
              </motion.div>
              <motion.div
                className="absolute top-0 left-0"
                animate={{ opacity: isMenuOpen ? 1 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <X size={24} />
              </motion.div>
            </motion.button>
          </div>
        </nav>
        
        <div className="h-px bg-gradient-to-r from-transparent via-[#f2ae2a] to-transparent opacity-50">
          <div className="h-1 w-full bg-gradient-to-b from-black/5 to-transparent" />
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed top-0 right-0 w-full h-screen bg-white z-40 overflow-y-auto"
          >
            <div className="pt-24 px-8">
              <motion.div
                className="space-y-8"
                initial="hidden"
                animate="visible"
                variants={{
                  hidden: { opacity: 0 },
                  visible: {
                    opacity: 1,
                    transition: {
                      staggerChildren: 0.1
                    }
                  }
                }}
              >
                {[
                  { href: "#menu", text: "Menu", icon: Menu },
                  { href: "#about", text: "About", icon: Info }
                ].map((item) => (
                  <motion.a
                    key={item.href}
                    href={item.href}
                    className="block text-base font-medium text-gray-900 hover:text-[#f2ae2a] tracking-tight"
                    variants={{
                      hidden: { opacity: 0, x: -20 },
                      visible: { opacity: 1, x: 0 }
                    }}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {item.text}
                  </motion.a>
                ))}
                <motion.div
                  variants={{
                    hidden: { opacity: 0, x: -20 },
                    visible: { opacity: 1, x: 0 }
                  }}
                >
                  {isAuthenticated ? (
                    <Button variant="secondary" size="lg" className="w-full tracking-tight">
                      Logout
                    </Button>
                  ) : (
                    <Link href="/login" passHref>
                      <Button variant="primary" size="lg" className="w-full tracking-tight">
                        Login
                      </Button>
                    </Link>
                  )}
                </motion.div>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
