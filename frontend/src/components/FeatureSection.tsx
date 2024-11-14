import React from 'react';
import { Truck, CreditCard, Map, Utensils } from 'lucide-react';

const WaveDivider = () => (
  <div className="absolute top-0 left-0 w-full overflow-hidden">
    <svg
      className="w-full h-auto"
      viewBox="0 0 1440 320"
      preserveAspectRatio="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fill="#f2ae2a"
        fillOpacity="0.2"
        d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,218.7C672,235,768,245,864,234.7C960,224,1056,192,1152,176C1248,160,1344,160,1392,160L1440,160L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"
      ></path>
      <path
        fill="#f2ae2a"
        fillOpacity="0.15"
        d="M0,96L48,112C96,128,192,160,288,165.3C384,171,480,149,576,149.3C672,149,768,171,864,165.3C960,160,1056,128,1152,117.3C1248,107,1344,117,1392,122.7L1440,128L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"
      ></path>
    </svg>
  </div>
);

const FeatureCard = ({ icon: Icon, title, description, delay }) => (
  <div className="group relative bg-white rounded-2xl p-4 sm:p-6 md:p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 mb-4 sm:mb-0">
    <div className="flex flex-col items-center text-center space-y-3 sm:space-y-4 md:space-y-6">
      <div className="p-2 sm:p-3 md:p-4 bg-gradient-to-br from-[#f2ae2a]/20 to-[#f2ae2a]/10 rounded-full ring-2 ring-[#f2ae2a] group-hover:ring-4 transition-all duration-300">
        <Icon className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 text-[#f2ae2a] group-hover:scale-110 transition-transform duration-300" />
      </div>
      <h3 className="text-lg sm:text-xl md:text-2xl font-bold text-gray-800">{title}</h3>
      <p className="text-sm sm:text-base md:text-base text-gray-600 leading-relaxed">{description}</p>
    </div>
    <div className="absolute inset-0 bg-gradient-to-r from-[#f2ae2a]/5 to-transparent opacity-0 group-hover:opacity-100 rounded-2xl transition-opacity duration-300" />
  </div>
);

const FeaturesSection = () => {
  const features = [
    {
      icon: Truck,
      title: "Fast Delivery",
      description: "Swift and reliable delivery right to your doorstep, because great food shouldn't keep you waiting."
    },
    {
      icon: CreditCard,
      title: "Easy Checkout",
      description: "Seamless payments through M-Pesa or cash on delivery - whatever works best for you!"
    },
    {
      icon: Map,
      title: "Order Tracking",
      description: "Track your order in real-time and know exactly when your delicious meal will arrive."
    },
    {
      icon: Utensils,
      title: "Top-tier Food",
      description: "Experience culinary excellence with our carefully crafted dishes made from premium ingredients."
    }
  ];

  return (
    <div className="relative min-h-screen bg-white">
      <WaveDivider />
      <section className="py-8 sm:py-12 md:py-16 lg:py-24">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="text-center mb-8 sm:mb-12 md:mb-16 lg:mb-20">
            <h2 className="text-3xl sm:text-4xl md:text-4xl lg:text-5xl font-bold mb-8 sm:mb-12 md:mb-16 text-gray-900">
              Why Choose <span className="text-[#895B1E]">Tweeps™</span>?
            </h2>
            <p className="font-semibold text-base sm:text-2xl md:text-2xl lg:text-2xl text-gray-800 max-w-5xl mx-auto px-4">
              Experience the perfect blend of convenience, quality, and reliability with every order.
            </p>
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8 md:gap-10">
            {features.map((feature, index) => (
              <FeatureCard
                key={feature.title}
                {...feature}
                delay={index * 0.2}
              />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default FeaturesSection;
