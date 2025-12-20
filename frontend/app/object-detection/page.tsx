'use client';

import { useState } from 'react';
import Link from 'next/link';
import ImageUpload from '@/components/ImageUpload';
import ImageDisplay from '@/components/ImageDisplay';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import { apiService } from '@/lib/api';

export default function ObjectDetectionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [objects, setObjects] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const handleImageSelected = (selectedFile: File, previewUrl: string) => {
    setFile(selectedFile);
    setPreview(previewUrl);
    setObjects(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setObjects(null);

    try {
      // Upload image
      const uploadResult = await apiService.uploadImage(file);
      const uploadedUrl = uploadResult.data.url;
      setImageUrl(uploadedUrl);

      // Detect objects
      const result = await apiService.analyzeObjects(uploadedUrl);
      setObjects(result.data.objects || 'No objects detected');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setObjects(null);
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Object Detection</h1>
          <p className="text-gray-600 mb-8">Upload an image to identify objects present in it</p>

          <div className="space-y-6">
            <ImageUpload 
              onImageSelected={handleImageSelected}
              disabled={loading}
            />

            {preview && !loading && !objects && (
              <button
                onClick={handleAnalyze}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Detect Objects
              </button>
            )}

            {loading && (
              <div className="py-8">
                <LoadingSpinner message="Detecting objects..." />
              </div>
            )}

            {error && (
              <ErrorMessage message={error} onRetry={handleAnalyze} />
            )}

            {objects && imageUrl && (
              <div className="space-y-4">
                <div className="border-t pt-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Detected Objects</h2>
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <p className="text-purple-900 whitespace-pre-wrap">{objects}</p>
                  </div>
                </div>

                <button
                  onClick={handleReset}
                  className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                >
                  Analyze Another Image
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
