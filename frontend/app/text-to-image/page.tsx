'use client';

import { useState } from 'react';
import Link from 'next/link';
import ImageDisplay from '@/components/ImageDisplay';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import { apiService, JobStatus } from '@/lib/api';

export default function TextToImagePage() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string>('');

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    setGeneratedImage(null);
    setJobStatus('Starting generation...');

    try {
      // Start generation job
      const jobResult = await apiService.generateTextToImage(prompt);
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
    setPrompt('');
    setGeneratedImage(null);
    setError(null);
    setJobStatus('');
  };

  const examplePrompts = [
    'A serene mountain landscape at sunset',
    'A futuristic city with flying cars',
    'A cozy coffee shop on a rainy day',
    'An astronaut riding a horse on mars',
  ];

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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Text-to-Image Generation</h1>
          <p className="text-gray-600 mb-8">Generate images from text descriptions using AI</p>

          <form onSubmit={handleGenerate} className="space-y-6">
            <div>
              <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
                Image Description
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the image you want to generate..."
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                disabled={loading}
              />
            </div>

            {!generatedImage && (
              <>
                <div className="flex flex-wrap gap-2">
                  <span className="text-sm text-gray-600">Try:</span>
                  {examplePrompts.map((example) => (
                    <button
                      key={example}
                      type="button"
                      onClick={() => setPrompt(example)}
                      disabled={loading}
                      className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-full transition-colors disabled:opacity-50"
                    >
                      {example}
                    </button>
                  ))}
                </div>

                <button
                  type="submit"
                  disabled={!prompt.trim() || loading}
                  className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Generate Image
                </button>
              </>
            )}
          </form>

          {loading && (
            <div className="py-8 mt-6">
              <LoadingSpinner message={jobStatus || 'Generating image...'} size="lg" />
              <p className="text-center text-sm text-gray-500 mt-4">
                This may take 15-30 seconds
              </p>
            </div>
          )}

          {error && (
            <div className="mt-6">
              <ErrorMessage message={error} onRetry={() => handleGenerate(new Event('submit') as any)} />
            </div>
          )}

          {generatedImage && (
            <div className="space-y-4 mt-6">
              <div className="border-t pt-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Generated Image</h2>
                <ImageDisplay src={generatedImage} alt="Generated image" showDownload={true} />
              </div>

              <button
                onClick={handleReset}
                className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Generate Another Image
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
