'use client';

import { useState } from 'react';
import Link from 'next/link';
import ImageUpload from '@/components/ImageUpload';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import { apiService } from '@/lib/api';

export default function CaptionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [caption, setCaption] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const handleImageSelected = (selectedFile: File, previewUrl: string) => {
    setFile(selectedFile);
    setPreview(previewUrl);
    setCaption(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setCaption(null);

    try {
      // Upload image
      const uploadResult = await apiService.uploadImage(file);
      const uploadedUrl = uploadResult.data.url;
      setImageUrl(uploadedUrl);

      // Generate caption
      const result = await apiService.analyzeCaption(uploadedUrl);
      setCaption(result.data.caption || 'No caption generated');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setCaption(null);
    setError(null);
    setImageUrl(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-6">
          <Link href="/" className="text-blue-600 hover:text-blue-700 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Caption Generation</h1>
          <p className="text-gray-600 mb-8">Upload an image to generate a descriptive caption</p>

          <div className="space-y-6">
            <ImageUpload 
              onImageSelected={handleImageSelected}
              disabled={loading}
            />

            {preview && !loading && !caption && (
              <button
                onClick={handleAnalyze}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Generate Caption
              </button>
            )}

            {loading && (
              <div className="py-8">
                <LoadingSpinner message="Generating caption..." />
              </div>
            )}

            {error && (
              <ErrorMessage message={error} onRetry={handleAnalyze} />
            )}

            {caption && imageUrl && (
              <div className="space-y-4">
                <div className="border-t pt-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Generated Caption</h2>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-900">{caption}</p>
                  </div>

                  <button
                    onClick={handleReset}
                    className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                  >
                    Analyze Another Image
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
