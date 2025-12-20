# Multi-Modal Image Analysis and Generation Platform

A full-stack web application that leverages cutting-edge AI models for image analysis and generation. Built with FastAPI (backend) and Next.js (frontend).

## 🚀 Features

### Image Analysis (3 Features)
- **Caption Generation** - Automatically generates descriptive captions for images
- **Visual Question Answering (VQA)** - Ask questions about images and get AI-powered answers
- **Object Detection** - Identifies and lists objects present in images

### Image Generation (2 Features)
- **Text-to-Image** - Generate images from text descriptions
- **Image Variation** - Create variations of existing images with custom modifications

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (Database ORM)
- Google Gemini 2.5 Flash (Vision analysis)
- HuggingFace Stable Diffusion XL (Image generation)
- AWS S3 (Image storage)
- SQLite/PostgreSQL (Database)

**Frontend:**
- Next.js 16 (React framework)
- TypeScript
- Tailwind CSS
- App Router

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- AWS Account (S3 bucket)
- Google AI Studio API Key
- HuggingFace API Token

## 🔧 Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
uv sync
```

3. Create `.env` file:
```env
# AI API Keys
GOOGLE_API_KEY=your_google_api_key
HUGGINGFACE_TOKEN=your_huggingface_token

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=ap-southeast-1
AWS_BUCKET_NAME=your-bucket-name

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./app.db

# Generation Provider (optional)
GENERATION_PROVIDER=huggingface
```

4. Start the backend server:
```bash
uv run uvicorn app.main:app --reload --port 8000
```

Backend will be available at http://127.0.0.1:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

4. Start the development server:
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## 🎯 Usage

1. Start both backend and frontend servers
2. Open http://localhost:3000 in your browser
3. Select a feature from the home page
4. Upload images or enter prompts
5. View AI-generated results

## 🏗️ Application Architecture

### High-Level Overview

```
┌─────────────┐      HTTP/REST      ┌──────────────┐
│   Next.js   │◄───────────────────►│   FastAPI    │
│   Frontend  │     (CORS enabled)   │   Backend    │
│  (Port 3000)│                      │  (Port 8000) │
└─────────────┘                      └──────┬───────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
              ┌─────▼──────┐         ┌─────▼──────┐         ┌─────▼──────┐
              │   Google   │         │ HuggingFace│         │   AWS S3   │
              │  Gemini    │         │   Stable   │         │   Storage  │
              │ 2.5 Flash  │         │ Diffusion  │         │            │
              │  (Vision)  │         │    (Gen)   │         │ (Presigned │
              └────────────┘         └────────────┘         │    URLs)   │
                                                            └─────┬──────┘
                                                                  │
                                                            ┌─────▼──────┐
                                                            │  SQLite/   │
                                                            │ PostgreSQL │
                                                            │  Database  │
                                                            └────────────┘
```

### Component Breakdown

**Frontend Layer (Next.js)**
- **UI Components**: Reusable React components (ImageUpload, LoadingSpinner, etc.)
- **Pages**: Route-specific pages for each feature (/caption, /vqa, etc.)
- **API Service**: TypeScript client for backend communication with type safety
- **State Management**: React hooks for local state and async operations

**Backend Layer (FastAPI)**
- **API Endpoints**: RESTful endpoints for analysis and generation
- **AI Service**: Integration layer for AI model APIs (Gemini, HuggingFace)
- **Database Models**: SQLAlchemy models for data persistence
- **S3 Service**: Image upload/storage with presigned URL generation
- **Background Tasks**: Async job processing for image generation

**Data Flow**
1. User uploads image → Frontend sends to `/upload` endpoint
2. Backend uploads to S3 → Returns presigned URL
3. User triggers analysis/generation → API calls AI services
4. Results stored in database → Returned to frontend
5. Frontend displays results with images from S3

## 📖 API Usage Examples

### Example 1: Caption Generation

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analyze/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://your-bucket.s3.amazonaws.com/uploads/image.png"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "caption": "A serene mountain landscape with clouds at sunset",
    "created_at": "2025-12-20T10:30:00"
  }
}
```

### Example 2: Visual Question Answering

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analyze/vqa" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://your-bucket.s3.amazonaws.com/uploads/image.png",
    "question": "What color is the car?"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "question": "What color is the car?",
    "answer": "The car is red",
    "created_at": "2025-12-20T10:31:00"
  }
}
```

### Example 3: Text-to-Image Generation (Async)

**Step 1 - Start Generation:**
```bash
curl -X POST "http://127.0.0.1:8000/api/generate/text-to-image" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic city with flying cars at night"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Image generation job started",
  "data": {
    "job_id": "abc123",
    "status": "pending",
    "check_status_url": "/api/jobs/abc123"
  }
}
```

**Step 2 - Check Status (Poll every 3-5 seconds):**
```bash
curl -X GET "http://127.0.0.1:8000/api/jobs/abc123"
```

**Response (completed):**
```json
{
  "success": true,
  "data": {
    "job_id": "abc123",
    "task_type": "text_to_image",
    "status": "completed",
    "result_image_url": "https://your-bucket.s3.amazonaws.com/generated/result.png",
    "created_at": "2025-12-20T10:32:00",
    "completed_at": "2025-12-20T10:32:25"
  }
}
```

## 🔑 API Key Configuration Guide

### 1. Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key" → "Create API key"
4. Copy the key and add to backend `.env`:
   ```
   GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

### 2. HuggingFace API Token

1. Visit [HuggingFace Tokens](https://huggingface.co/settings/tokens)
2. Sign in or create an account
3. Click "New token" → Select "Read" access
4. Copy the token and add to backend `.env`:
   ```
   HUGGINGFACE_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

### 3. AWS S3 Configuration

1. Log into [AWS Console](https://console.aws.amazon.com/)
2. Navigate to IAM → Users → Create User
3. Attach policy: `AmazonS3FullAccess` (or custom policy)
4. Create Access Key → Download credentials
5. Create an S3 bucket in your preferred region
6. Add credentials to backend `.env`:
   ```
   AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
   AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   AWS_REGION=ap-southeast-1
   AWS_BUCKET_NAME=your-bucket-name
   ```

**Note:** For production, use IAM roles and restrict S3 bucket policies appropriately.

## 🎯 Usage

```
Multi-Modal-Image-Analysis-and-Generation-Platform/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app & endpoints
│   │   ├── ai_service.py     # AI model integration
│   │   ├── models.py         # Database models
│   │   ├── database.py       # Database configuration
│   │   └── s3_service.py     # S3 upload handling
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   │   ├── page.tsx          # Home page
│   │   ├── caption/          # Caption generation page
│   │   ├── vqa/              # Visual Q&A page
│   │   ├── object-detection/ # Object detection page
│   │   ├── text-to-image/    # Text-to-image page
│   │   └── variation/        # Image variation page
│   ├── components/           # Shared React components
│   ├── lib/
│   │   └── api.ts            # API service layer
│   └── package.json
└── EVALUATION.md             # Testing documentation

```

## 📊 API Endpoints

### Analysis Endpoints
- `POST /upload` - Upload image to S3
- `POST /api/analyze/caption` - Generate image caption
- `POST /api/analyze/vqa` - Visual question answering
- `POST /api/analyze/object-detection` - Detect objects

### Generation Endpoints (Async)
- `POST /api/generate/text-to-image` - Generate image from text
- `POST /api/generate/variation` - Create image variation
- `GET /api/jobs/{job_id}` - Check generation job status

## ✅ Testing

All features have been tested and verified working. See [EVALUATION.md](EVALUATION.md) for detailed test results and examples.

**Test Results:** 6/6 features passing (100%)

## 🎥 Demo

**Demo Video:** [Link](https://drive.google.com/file/d/1FOWHpteljL-o8sXI5QSHYFLOnuS5LIJs/view?usp=sharing)  

To create a demo video:
1. Record a 5-minute walkthrough showing all features
2. Upload to YouTube, Loom, or similar platform
3. Add the link above

## 🔐 Security Notes

- S3 bucket uses presigned URLs (7-day expiry)
- CORS enabled for frontend access
- API keys managed via environment variables
- Database credentials secured

## 📝 License

This project is for educational purposes.

## 👨‍💻 Author

Akhilesh Malthi

---

**Note:** Make sure both backend and frontend servers are running for the application to work properly.
