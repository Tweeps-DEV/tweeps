'use client';
import { useEffect, useState } from 'react';
import Image from 'next/image';

export default function LottiePlayer({ onLoadComplete }: { onLoadComplete: () => void }) {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
      onLoadComplete();
    }, 3000);

    return () => clearTimeout(timer);  
  }, [onLoadComplete]);

  return (
    <div className="relative w-full max-w-[800px] mx-auto">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <Image src="/loader.gif" alt="Loading animation"/>
        </div>
      )}
    </div>
  );
}
