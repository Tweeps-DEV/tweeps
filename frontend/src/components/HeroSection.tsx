import { motion } from 'framer-motion';
import { Button } from './ui/Button';
import { useEffect, useState } from 'react';
import _ from 'lodash';
import Link from 'next/link';

const WaveDivider = () => (
  <div className="absolute bottom-0 left-0 w-full overflow-hidden rotate-180">
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

const HeroSection: React.FC = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  
  useEffect(() => {
    const handleMouseMove = _.debounce((e: MouseEvent) => {
      const { clientX, clientY } = e;
      const x = (clientX / window.innerWidth) * 100;
      const y = (clientY / window.innerHeight) * 100;
      setMousePosition({ x, y });
    }, 16); // Approximately 60fps

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      handleMouseMove.cancel();
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  const BLOB_ANIMATION = {
    x: mousePosition.x * 0.3,
    y: mousePosition.y * 0.3,
    scale: [1, 1.1, 1],
  }
  

  return (
    <div className="relative h-screen flex items-center overflow-visible">
      <motion.div
        className="absolute pointer-events-none"
        animate={{
          x: mousePosition.x * 0.3,
          y: mousePosition.y * 0.3,
          scale: [1, 1.1, 1],
        }}
        transition={{
          x: { type: "spring", stiffness: 50, damping: 25 },
          y: { type: "spring", stiffness: 50, damping: 25 },
          scale: {
            duration: 8,
            repeat: Infinity,
            repeatType: "reverse",
          },
        }}
        style={{
          width: '100vw',
          height: '100vh',
          position: 'absolute',
          top: '-50%',
          left: '-25%',
          zIndex: 0,
        }}
      >
        <svg
          className="w-full h-full"
          viewBox="0 0 500 500"
          xmlns="http://www.w3.org/2000/svg"
        >
          <motion.path
            fill="#F2AE2A"
            opacity="0.1"
            animate={{
              d: [
                "M228.5,-232.1C340.4,-223.9,456.1,-118.3,464.8,-5.9C473.5,106.4,375.3,225.5,267.2,288.1C159.1,350.8,41.1,357,23.1,363.6C5.2,370.1,-12.6,376.9,-18.7,367.6C-24.7,358.3,-19,233,-19.3,118.1C-19.6,3.2,-26,-91.3,-25.8,-194.9C-25.6,-298.6,-18.9,-411.5,-13.5,-420.9C-8.1,-430.2,-4,-446,22.1,-448.6C48.3,-451.1,116.5,-240.3,228.5,-232.1Z",
                "M254.9,-240.1C360.4,-233.9,486.1,-128.3,494.8,-15.9C503.5,96.4,395.3,215.5,277.2,278.1C159.1,340.8,31.1,347,13.1,353.6C-4.9,360.1,-32.6,366.9,-48.7,357.6C-64.7,348.3,-69,223,-69.3,108.1C-69.6,-6.8,-86,-111.3,-75.8,-204.9C-65.6,-298.6,-28.9,-381.5,-3.5,-390.9C21.9,-400.2,149.4,-246.3,254.9,-240.1Z",
                "M228.5,-232.1C340.4,-223.9,456.1,-118.3,464.8,-5.9C473.5,106.4,375.3,225.5,267.2,288.1C159.1,350.8,41.1,357,23.1,363.6C5.2,370.1,-12.6,376.9,-18.7,367.6C-24.7,358.3,-19,233,-19.3,118.1C-19.6,3.2,-26,-91.3,-25.8,-194.9C-25.6,-298.6,-18.9,-411.5,-13.5,-420.9C-8.1,-430.2,-4,-446,22.1,-448.6C48.3,-451.1,116.5,-240.3,228.5,-232.1Z"
              ],
              rotate: [0, 360],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "linear",
            }}
          />
        </svg>
      </motion.div>

      <div className="container mx-auto px-4 lg:px-8 relative">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 lg:gap-32 items-center">
          <motion.div
            className="relative z-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl lg:text-7xl font-bold leading-tight tracking-tighter">
              Have You Been
              <span className="text-[#f2ae2a]"> Served Yet?</span>
            </h1>
            <p className="text-2xl text-gray-600 max-w-lg tracking-tight mt-8 mb-8">
              Welcome to Tweeps, where every dish tells a story and every meal becomes a memory.
              Get your meals delivered to your doorstep at your own convenience.
            </p>
            <Link href="/login" passHref>
              <Button variant="primary" size="lg" className="tracking-tight">
                Order now
              </Button>
            </Link>
          </motion.div>

          <div className="relative hidden lg:block">
            <motion.div
              className="absolute pointer-events-none"
              style={{
                width: '100%',
                height: '100%',
                position: 'absolute',
                top: '-20%',
                right: '-20%',
                zIndex: 0,
              }}
              animate={{
                rotate: [0, 360],
                scale: [0.9, 1.1, 0.9],
              }}
              transition={{
                duration: 20,
                repeat: Infinity,
                repeatType: "reverse",
                ease: "linear",
              }}
            >
              <img 
                src="/blob.svg" 
                alt="" 
                className="w-full h-full opacity-10"
              />
            </motion.div>

            <motion.img
              src="/heroImage.png"
              alt="Decorative right SVG"
              className="w-[500px] h-auto relative z-10"
              initial={{ opacity: 0, x: 50 }}
              animate={{ 
                opacity: 3, 
                x: 0,
                y: [0, -10, 0]
              }}
              transition={{
                opacity: { duration: 0.8 },
                x: { duration: 0.8 },
                y: { 
                  duration: 4,
                  repeat: Infinity,
                  repeatType: "reverse",
                  ease: "easeInOut"
                }
              }}
            />
          </div>
        </div>
      </div>
      
      {/* Added Wave Divider */}
      <WaveDivider />
    </div>
  );
};

export default HeroSection;
