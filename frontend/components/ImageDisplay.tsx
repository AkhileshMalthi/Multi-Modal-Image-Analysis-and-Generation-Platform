'use client';

import Image from 'next/image';

interface ImageDisplayProps {
  src: string;
  alt: string;
  caption?: string;
  className?: string;
}

export default function ImageDisplay({ src, alt, caption, className = '' }: ImageDisplayProps) {
  return (
    <div className={`rounded-lg overflow-hidden border border-gray-200 ${className}`}>
      <div className="relative w-full h-64">
        <Image
          src={src}
          alt={alt}
          fill
          className="object-contain bg-gray-50"
          unoptimized // For external URLs like S3
        />
      </div>
      {caption && (
        <div className="p-3 bg-gray-50 border-t border-gray-200">
          <p className="text-sm text-gray-700">{caption}</p>
        </div>
      )}
    </div>
  );
}
