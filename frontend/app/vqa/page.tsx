'use client';

import { useState } from 'react';
import Link from 'next/link';
import ImageUpload from '@/components/ImageUpload';
import ImageDisplay from '@/components/ImageDisplay';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import { apiService } from '@/lib/api';

export default function VQAPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const handleImageSelected = (selectedFile: File, previewUrl: string) => {
    setFile(selectedFile);
    setPreview(previewUrl);
    setAnswer(null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !question.trim()) return;

    setLoading(true);
    setError(null);
    setAnswer(null);

    try {
      // Upload image
      const uploadResult = await apiService.uploadImage(file);
      const uploadedUrl = uploadResult.data.url;
      setImageUrl(uploadedUrl);

      // Get answer
      const result = await apiService.analyzeVQA(uploadedUrl, question);
      setAnswer(result.data.answer || 'No answer generated');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setQuestion('');
    setAnswer(null);
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Visual Question Answering</h1>
          <p className="text-gray-600 mb-8">Upload an image and ask questions about it</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <ImageUpload 
              onImageSelected={handleImageSelected}
              disabled={loading}
            />

            <div>
              <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
                Your Question
              </label>
              <input
                id="question"
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., What color is the car?"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                disabled={loading}
              />
            </div>

            {preview && !loading && !answer && (
              <button
                type="submit"
                disabled={!question.trim()}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Get Answer
              </button>
            )}
          </form>

          {loading && (
            <div className="py-8 mt-6">
              <LoadingSpinner message="Analyzing image..." />
            </div>
          )}

          {error && (
            <div className="mt-6">
              <ErrorMessage message={error} onRetry={() => handleSubmit(new Event('submit') as any)} />
            </div>
          )}

          {answer && imageUrl && (
            <div className="space-y-4 mt-6">
              <div className="border-t pt-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Result</h2>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <p className="text-sm font-medium text-blue-900 mb-2">Question:</p>
                  <p className="text-blue-800">{question}</p>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <p className="text-sm font-medium text-green-900 mb-2">Answer:</p>
                  <p className="text-green-800">{answer}</p>
                </div>
                <ImageDisplay src={imageUrl} alt="Analyzed image" />
              </div>

              <button
                onClick={handleReset}
                className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Ask Another Question
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
