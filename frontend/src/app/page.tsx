'use client';
import type { NextPage } from 'next';
import { useState, useRef, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { motion, AnimatePresence } from 'framer-motion';
import _ from 'lodash';
import { Instagram, Twitter } from 'lucide-react';
import { Navigation } from '../components/Navigation';
import { Button } from '../components/ui/Button';
import { AnimatedSection } from '../components/ui/AnimatedSection';
import LottiePlayer from '../components/LottiePlayer';
import { MenuCard } from '../components/MenuCard';
import HeroSection from '../components/HeroSection';
import FeatureSection from '../components/FeatureSection';
import TestimonialCarousel from '../components/TestimonialCarousel';
import { Menu, Clock, MapPin, Star, Mail, Phone, X } from 'lucide-react';
import AboutSection from '../components/About';
import Link from 'next/link';

const Home: NextPage = () => {
  const {  session, status } = useSession();
  const isAuthenticated = status === "authenticated";
  const user = session?.user;
  const [showContent, setShowContent] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const sectionRefs = {
    hero: useRef<HTMLDivElement>(null),
    features: useRef<HTMLDivElement>(null),
    menu: useRef<HTMLDivElement>(null),
    testimonials: useRef<HTMLDivElement>(null),
    about: useRef<HTMLDivElement>(null)
  };

  const scrollToSection = (sectionId: keyof typeof sectionRefs) => {
    sectionRefs[sectionId].current?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
      duration: 1000
    });
  };


  function useIntersectionObserver(ref: RefObject<HTMLElement>, options: IntersectionObserverInit = {}) {
  const [isIntersecting, setIntersecting] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      setIntersecting(entry.isIntersecting);
    }, options);

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      observer.disconnect();
     };
    }, [ref, options]);

    return isIntersecting;
  }

  const menuItems = [
    {
      title: "Truffle Pasta",
      description: "Fresh homemade pasta with black truffle and parmesan",
      price: "$28",
      image: "/api/placeholder/400/300"
    },
    {
      title: "Wagyu Steak",
      description: "Grade A5 Japanese Wagyu with seasonal vegetables",
      price: "$85",
      image: "/api/placeholder/400/300"
    },
    {
      title: "Seafood Platter",
      description: "Fresh daily catch with lobster, oysters, and prawns",
      price: "$65",
      image: "/api/placeholder/400/300"
    }
  ];
 
  if (!showContent) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LottiePlayer onLoadComplete={() => setShowContent(true)} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600">Oops, Something went wrong</h2>
          <p className="mt-2 text-gray-600">{error.message}</p>
          <button
            onClick={() => setError(null)}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <Navigation
        isAuthenticated={isAuthenticated}
        user={user}
        isMenuOpen={isMenuOpen}
        setIsMenuOpen={setIsMenuOpen}
        onNavigate={scrollToSection}
      />

      <main className="flex-1 overflow-y-auto snap-y snap-proximity scroll-smooth no-scrollbar">
        <div ref={sectionRefs.hero} className="snap-start h-screen w-full">
          <HeroSection />
        </div>

        <div ref={sectionRefs.features} className="snap-start overflow-hidden h-screen w-full">
          <FeatureSection />
        </div>

        {/* Menu Section */}
        <section ref={sectionRefs.menu} className="snap-start min-h-screen w-full overflow-hidden py-12 sm:py-16 md:py-24" id="menu">
          <div className="container mx-auto px-4 lg:px-8">
            <h2 className="text-3xl sm:text-4xl font-bold text-center mb-8 sm:mb-12 md:mb-16 tracking-tight">
              Today's top picks
            </h2>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 md:gap-10">
              {menuItems.map((item, index) => (
                <AnimatedSection key={item.title} delay={index * 0.2}>
                  <MenuCard {...item} />
                </AnimatedSection>
              ))}
            </div>
          </div>
        </section>

        <section ref={sectionRefs.testimonials} className="snap-start h-screen overflow-hidden w-full py-24">
          <TestimonialCarousel />
        </section>

        <section ref={sectionRefs.about} className="snap-start" id="about">
          <AboutSection />
        </section>

        {/* Footer */}
        <footer className="bg-[#f2ae2a] text-gray-300 py-12">
          <div className="container mx-auto px-4 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              {/* Company Information */}
              <div className="space-y-4">
                <img
                  src="/tweeps-logo.svg"
                  alt="Tweeps Logo"
                  className="h-44 w-auto"
                />
                <p className="text-sm text-gray-800 max-w-xs">
                  Serving delicious, quality fast food since 2020. Your satisfaction is our priority.
                </p>
                <div className="flex space-x-4">
                  <a
                    href="https://instagram.com/tweeps"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-800 hover:text-white transition-colors"
                  >
                    <Instagram size={20} />
                  </a>
                  <a
                    href="https://twitter.com/tweeps"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-800 hover:text-white transition-colors"
                  >
                    <Twitter size={20} />
                  </a>
                </div>
              </div>

              {/* Contact Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-[#895B1E]">Contact Us</h3>
                <div className="space-y-3">
                  <a href="tel:+254705704788" className="flex items-center space-x-2 text-gray-800 hover:text-white transition-colors">
                    <Phone size={16} />
                    <span>+254 705 704 788</span>
                  </a>
                  <a href="mailto:tweepsfastfood@gmail.com" className="flex items-center space-x-2 text-gray-800 hover:text-white transition-colors">
                    <Mail size={16} />
                    <span>tweepsfastfood@gmail.com</span>
                  </a>
                  <a
                    href="https://maps.app.goo.gl/FFR5MHwjt8j5Sows9"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 text-gray-800 hover:text-white transition-colors"
                  >
                    <MapPin size={16} />
                    <span>Rm 12 Pressy Building</span>
                  </a>
                </div>
              </div>

              {/* Operating Hours */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-[#895B1E]">Opening Hours</h3>
                <div className="space-y-2 text-gray-800">
                  <div className="flex items-start space-x-2">
                    <Clock size={16} className="mt-1 flex-shrink-0" />
                    <div>
                      <p>Monday - Friday: 11:00 AM - 11:00 PM</p>
                      <p>Saturday - Sunday: 10:00 AM - 12:00 AM</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-12 pt-8 border-t border-gray-800">
              <p className="text-sm text-gray-900">© {new Date().getFullYear()} Tweeps™. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
};

export default Home;
