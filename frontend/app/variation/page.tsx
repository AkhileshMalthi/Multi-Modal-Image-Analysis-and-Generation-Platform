'use client';

import { useState } from 'react';
import Link from 'next/link';
import ImageUpload from '@/components/ImageUpload';
import ImageDisplay from '@/components/ImageDisplay';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import { apiService, JobStatus } from '@/lib/api';

export default function VariationPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string>('');

  const handleImageSelected = (selectedFile: File, previewUrl: string) => {
    setFile(selectedFile);
    setPreview(previewUrl);
    setGeneratedImage(null);
    setError(null);
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !prompt.trim()) return;

    setLoading(true);
    setError(null);
    setGeneratedImage(null);
    setJobStatus('Uploading image...');

    try {
      // Upload image
      const uploadResult = await apiService.uploadImage(file);
      const imageUrl = uploadResult.data.url;
      setUploadedUrl(imageUrl);
      setJobStatus('Starting variation generation...');

      // Start generation job
      const jobResult = await apiService.generateVariation(imageUrl, prompt);
      const jobId = jobResult.data.job_id;
      setJobStatus('Processing...');

      // Poll for completion
      const finalStatus = await apiService.pollJobStatus(
        jobId,
        (status: JobStatus) => {
          setJobStatus(`Status: ${status.data.status}`);
        }
      );

      if (finalStatus.data.status === 'completed' && finalStatus.data.result_image_url) {
        setGeneratedImage(finalStatus.data.result_image_url);
        setJobStatus('');
      } else {
        throw new Error(finalStatus.data.error || 'Generation failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setJobStatus('');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setPrompt('');
    setGeneratedImage(null);
    setError(null);
    setJobStatus('');
    setUploadedUrl(null);
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Image Variation</h1>
          <p className="text-gray-600 mb-8">Create variations of your images with custom modifications</p>

          <form onSubmit={handleGenerate} className="space-y-6">
            <ImageUpload 
              onImageSelected={handleImageSelected}
              disabled={loading}
            />

            <div>
              <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
                Modification Description
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe how you want to modify the image..."
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                disabled={loading}
              />
              <p className="mt-2 text-xs text-gray-500">
                Examples: "make it more colorful", "add a sunset background", "in a watercolor style"
              </p>
            </div>

            {preview && !loading && !generatedImage && (
              <button
                type="submit"
                disabled={!prompt.trim()}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Generate Variation
              </button>
            )}
          </form>

          {loading && (
            <div className="py-8 mt-6">
              <LoadingSpinner message={jobStatus || 'Generating variation...'} size="lg" />
              <p className="text-center text-sm text-gray-500 mt-4">
                This may take 20-40 seconds
              </p>
            </div>
          )}

          {error && (
            <div className="mt-6">
              <ErrorMessage message={error} onRetry={() => handleGenerate(new Event('submit') as any)} />
            </div>
          )}

          {generatedImage && uploadedUrl && (
            <div className="space-y-4 mt-6">
              <div className="border-t pt-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Result</h2>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <p className="text-sm font-medium text-blue-900 mb-2">Modification:</p>
                  <p className="text-blue-800">{prompt}</p>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Original</h3>
                    <ImageDisplay src={uploadedUrl} alt="Original image" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Variation</h3>
                    <ImageDisplay src={generatedImage} alt="Generated variation" />
                  </div>
                </div>
              </div>

              <button
                onClick={handleReset}
                className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Generate Another Variation
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
