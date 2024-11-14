'use client';
import { useEffect, useRef, useState } from 'react';

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
          <img src="/loader.gif" alt="Loading animation"/>
        </div>
      )}
    </div>
  );
}
