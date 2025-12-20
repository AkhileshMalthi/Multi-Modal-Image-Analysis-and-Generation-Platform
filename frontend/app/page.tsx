import Link from 'next/link';

export default function Home() {
  const features = [
    {
      title: 'Caption Generation',
      description: 'Automatically generate descriptive captions for your images',
      href: '/caption',
      icon: '📝',
    },
    {
      title: 'Visual Q&A',
      description: 'Ask questions about your images and get AI-powered answers',
      href: '/vqa',
      icon: '❓',
    },
    {
      title: 'Object Detection',
      description: 'Identify and list objects present in your images',
      href: '/object-detection',
      icon: '🔍',
    },
    {
      title: 'Text-to-Image',
      description: 'Generate images from text descriptions',
      href: '/text-to-image',
      icon: '🎨',
    },
    {
      title: 'Image Variation',
      description: 'Create variations of existing images',
      href: '/variation',
      icon: '🔄',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Multi-Modal AI Platform
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Analyze and generate images using cutting-edge AI models
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {features.map((feature) => (
            <Link
              key={feature.href}
              href={feature.href}
              className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow border border-gray-200 hover:border-blue-500"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {feature.title}
              </h2>
              <p className="text-gray-600">{feature.description}</p>
            </Link>
          ))}
        </div>

        <div className="mt-12 text-center text-sm text-gray-500">
          <p>Powered by Google Gemini & HuggingFace Stable Diffusion</p>
        </div>
      </div>
    </div>
  );
}
