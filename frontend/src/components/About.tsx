import React from 'react';
import Image from 'next/image';

const AboutSection = () => {
  return (
    <div className="relative w-full min-h-screen bg-white overflow-hidden">
      <div 
        className="absolute inset-0 pointer-events-none bg-[url('/about-bg.svg')] bg-cover bg-center bg-no-repeat opacity-5"
        aria-hidden="true"
      />

      <div className="relative w-full min-h-screen py-12 md:py-16 lg:py-24 backdrop-blur-sm">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            {/* Photo Collage - Responsive */}
            <div className="order-2 lg:order-1">
              <div className="grid grid-cols-2 gap-2 sm:gap-4 h-full max-w-2xl mx-auto lg:mx-0">
                <div className="space-y-6 sm:space-y-6">
                  <Image 
                    src="/api/placeholder/400/500" 
                    alt="Restaurant atmosphere" 
                    className="w-full h-32 sm:h-48 md:h-64 object-cover rounded-lg shadow-md transition-transform hover:scale-105 bg-white"
                  />
                  <Image
                    src="/api/placeholder/400/300" 
                    alt="African cuisine" 
                    className="w-full h-24 sm:h-32 md:h-48 object-cover rounded-lg shadow-md transition-transform hover:scale-105 bg-white"
                  />
                </div>
                <div className="space-y-6 sm:space-y-6 pt-4 sm:pt-8">
                  <Image
                    src="/api/placeholder/400/300" 
                    alt="Customer experience" 
                    className="w-full h-24 sm:h-32 md:h-48 object-cover rounded-lg shadow-md transition-transform hover:scale-105 bg-white"
                  />
                  <Image
                    src="/api/placeholder/400/500" 
                    alt="Food preparation" 
                    className="w-full h-32 sm:h-48 md:h-64 object-cover rounded-lg shadow-md transition-transform hover:scale-105 bg-white"
                  />
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="order-1 lg:order-2 space-y-4 sm:space-y-6 mb-8 lg:mb-0">
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-gray-900">
                About Tweeps™
              </h2>
              <div className="space-y-3 sm:space-y-4 text-base sm:text-lg text-gray-600">
                <p className="leading-relaxed">
                  Food is what brings people together. At Tweeps™, we ensure top-notch customer service 
                  and also get to know each other not only as customers but also as a network, building 
                  a sense of family.
                </p>
                <p className="leading-relaxed">
                  Our focus is on creating good moments. At Tweeps™ fast food kitchen, we achieve this 
                  by offering a variety of nutritious meals at affordable prices. We infuse an African 
                  touch into our recipes, menu, and spices, embracing a natural feeling in our delicacies.
                </p>
                <p className="leading-relaxed">
                  Surrounded by a serene environment filled with people of great diversity and culture, 
                  we aim to make you feel at home, even when you&apos;re far away from home.
                </p>
                <p className="text-lg sm:text-xl font-semibold text-[#f2ae2a]">
                  So, have you been served yet? Usisonge hapo!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutSection;
