# Frontend - Multi-Modal AI Platform

Next.js web application for image analysis and generation.

## Features

- **Caption Generation** - Generate descriptive captions for images
- **Visual Q&A** - Ask questions about images and get AI-powered answers  
- **Object Detection** - Identify objects present in images
- **Text-to-Image** - Generate images from text descriptions
- **Image Variation** - Create variations of existing images

## Getting Started

First, install dependencies and run the development server:

```bash
npm install
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000).

**Important**: Make sure the backend API is running at `http://127.0.0.1:8000` before testing.

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Architecture

- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: Shared UI components in `/components`
- **API Client**: Service layer in `/lib/api.ts`
- **Pages**: Feature pages in `/app/*`

## Testing Flow

1. Start the backend server: `cd ../backend && uv run uvicorn app.main:app --reload --port 8000`
2. Start the frontend: `npm run dev`
3. Visit [http://localhost:3000](http://localhost:3000)
4. Test each feature from the home page

## Key Components

- `ImageUpload.tsx` - Image upload with preview and validation
- `ImageDisplay.tsx` - Display images from S3 URLs
- `LoadingSpinner.tsx` - Loading states with custom messages
- `ErrorMessage.tsx` - Error handling with retry functionality
- `api.ts` - TypeScript API client with job polling

## Features Details

### Analysis Features (Instant Results)
- Caption generation uses Gemini vision API
- VQA accepts custom questions about images
- Object detection lists all identified objects

### Generation Features (Async Jobs)
- Text-to-image and variation use job polling
- Real-time status updates every 3 seconds
- Typically complete in 15-40 seconds

- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
