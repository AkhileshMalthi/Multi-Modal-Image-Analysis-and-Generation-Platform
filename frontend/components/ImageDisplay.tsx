'use client';

import Image from 'next/image';

interface ImageDisplayProps {
  src: string;
  alt: string;
  caption?: string;
  className?: string;
  showDownload?: boolean;
}

export default function ImageDisplay({ src, alt, caption, className = '', showDownload = false }: ImageDisplayProps) {
  const handleDownload = async () => {
    try {
      // Try fetch with no-cors mode first (will work with presigned URLs)
      const response = await fetch(src, { mode: 'no-cors' });
      
      // If no-cors worked but we can't access the blob, fall back to direct link
      if (!response.ok && response.type === 'opaque') {
        // Fallback: Use anchor tag with direct URL (works with presigned URLs)
        const a = document.createElement('a');
        a.href = src;
        a.download = `image-${Date.now()}.png`;
        a.target = '_blank'; // Open in new tab as fallback
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        return;
      }
      
      // If CORS is properly configured, use blob method
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `image-${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
      // Fallback: Direct link download (works with presigned URLs even without CORS)
      const a = document.createElement('a');
      a.href = src;
      a.download = `image-${Date.now()}.png`;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

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
      {(caption || showDownload) && (
        <div className="p-3 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          {caption && <p className="text-sm text-gray-700">{caption}</p>}
          {showDownload && (
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              title="Download image"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
          )}
        </div>
      )}
    </div>
  );
}
