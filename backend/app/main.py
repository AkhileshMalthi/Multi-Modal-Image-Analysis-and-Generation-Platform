from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import hashlib

from .database import engine, Base, get_db
from .models import ImageMeta, AnalysisResult, GenerationRequest, JobStatus
from .s3_service import upload_file_to_s3
from .ai_service import analyze_image, generate_image_from_text
import tempfile
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Modal Image Analysis and Generation Platform")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === PYDANTIC MODELS ===
class AnalyzeRequest(BaseModel):
    image_url: str
    question: Optional[str] = None  # For VQA


class GenerateTextToImageRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None


class GenerateVariationRequest(BaseModel):
    image_url: str
    prompt: str  # Style/modification instructions
    provider: Optional[str] = None


# === ROOT ENDPOINT ===
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Multi-Modal Image Analysis and Generation Platform API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "analysis": {
                "caption": "/api/analyze/caption",
                "vqa": "/api/analyze/vqa",
                "object_detection": "/api/analyze/object-detection"
            },
            "generation": {
                "text_to_image": "/api/generate/text-to-image",
                "variation": "/api/generate/variation"
            },
            "jobs": "/api/jobs/{job_id}"
        }
    }


# === IMAGE UPLOAD ===
@app.post("/upload")
def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload an image to S3 and store metadata in database.
    Implements deduplication: if the same image (by content hash) already exists, 
    returns the existing URL instead of uploading again.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Read file content once
    file_content = file.file.read()
    file_size = len(file_content)
    
    # Calculate SHA256 hash of file content for deduplication
    content_hash = hashlib.sha256(file_content).hexdigest()
    
    # Check if this exact file already exists in database
    existing_image = db.query(ImageMeta).filter(ImageMeta.content_hash == content_hash).first()
    
    if existing_image:
        print(f"✓ Duplicate detected! Returning existing image: {existing_image.filename}")
        return {
            "message": "Image already exists (duplicate detected)",
            "duplicate": True,
            "data": {
                "id": existing_image.id,
                "url": existing_image.s3_url,
                "filename": existing_image.filename,
                "original_upload_date": existing_image.uploaded_at
            }
        }
    
    # File is new, proceed with upload
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"uploads/{content_hash[:16]}.{file_extension}"  # Use hash prefix for filename
    
    # Reset file pointer and upload to S3
    from io import BytesIO
    image_url = upload_file_to_s3(BytesIO(file_content), unique_filename)
    
    if not image_url:
        raise HTTPException(status_code=500, detail="Failed to upload image to storage")

    # Save Metadata to DB with hash
    new_image = ImageMeta(
        filename=unique_filename, 
        s3_url=image_url,
        content_hash=content_hash,
        file_size=file_size
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    
    print(f"✓ New image uploaded: {unique_filename} (hash: {content_hash[:16]}...)")

    return {
        "message": "Upload successful",
        "duplicate": False,
        "data": {
            "id": new_image.id,
            "url": new_image.s3_url,
            "filename": new_image.filename
        }
    }


# === ANALYSIS ENDPOINTS ===
@app.post("/api/analyze/caption")
def analyze_caption(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """Generate a caption for an uploaded image"""
    try:
        caption = analyze_image(request.image_url, prompt_type="caption")
        
        # Save result to database
        result = AnalysisResult(
            image_url=request.image_url,
            analysis_type="caption",
            result=caption
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return {
            "success": True,
            "data": {
                "id": result.id,
                "caption": caption,
                "created_at": result.created_at
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Caption generation failed: {str(e)}")


@app.post("/api/analyze/vqa")
def analyze_vqa(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """Answer a question about an image (Visual Question Answering)"""
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required for VQA")
    
    try:
        # Pass custom question to analyze_image
        answer = analyze_image(request.image_url, prompt_type="vqa", custom_question=request.question)
        
        # Save result to database
        result = AnalysisResult(
            image_url=request.image_url,
            analysis_type="vqa",
            prompt=request.question,
            result=answer
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return {
            "success": True,
            "data": {
                "id": result.id,
                "question": request.question,
                "answer": answer,
                "created_at": result.created_at
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VQA failed: {str(e)}")


@app.post("/api/analyze/object-detection")
def analyze_objects(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """Detect and list objects in an image"""
    try:
        objects = analyze_image(request.image_url, prompt_type="detection")
        
        # Save result to database
        result = AnalysisResult(
            image_url=request.image_url,
            analysis_type="object-detection",
            result=objects
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return {
            "success": True,
            "data": {
                "id": result.id,
                "objects": objects,
                "created_at": result.created_at
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Object detection failed: {str(e)}")


# === BACKGROUND TASK FOR IMAGE GENERATION ===
def process_image_generation(job_id: str, task_type: str, prompt: str, 
                            source_image_url: Optional[str], provider: str):
    """Background task to generate images and save to S3"""
    from .database import SessionLocal
    
    db = SessionLocal()
    job = None
    try:
        # Update status to processing
        job = db.query(GenerationRequest).filter(GenerationRequest.job_id == job_id).first()
        if job:
            job.status = JobStatus.PROCESSING
            db.commit()
        
        # Generate the image
        if task_type == "text-to-image":
            image = generate_image_from_text(prompt=prompt, task="text-to-image", provider=provider)
        elif task_type == "image-variation":
            image = generate_image_from_text(
                prompt=prompt, 
                task="image-variation", 
                image_url=source_image_url,
                provider=provider
            )
        else:
            raise ValueError(f"Unknown task type: {task_type}")
        
        if not image:
            raise Exception("Image generation returned None")
        
        # Save generated image to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            image.save(tmp_file, format="PNG")
            tmp_file_path = tmp_file.name
        
        # Upload to S3
        unique_filename = f"generated/{job_id}.png"
        with open(tmp_file_path, "rb") as f:
            result_url = upload_file_to_s3(f, unique_filename)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        if not result_url:
            raise Exception("Failed to upload generated image to S3")
        
        # Update job status
        if job:
            job.status = JobStatus.COMPLETED
            job.result_image_url = result_url
            job.completed_at = datetime.utcnow()
            db.commit()
            
    except Exception as e:
        # Update job status to failed
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        print(f"Generation job {job_id} failed: {e}")
    finally:
        db.close()


# === GENERATION ENDPOINTS ===
@app.post("/api/generate/text-to-image")
def generate_text_to_image(
    request: GenerateTextToImageRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate an image from text prompt (async)"""
    try:
        # Create job record
        job_id = str(uuid.uuid4())
        provider = request.provider or "huggingface"
        
        job = GenerationRequest(
            job_id=job_id,
            task_type="text-to-image",
            prompt=request.prompt,
            status=JobStatus.PENDING,
            provider=provider
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start background task
        background_tasks.add_task(
            process_image_generation,
            job_id=job_id,
            task_type="text-to-image",
            prompt=request.prompt,
            source_image_url=None,
            provider=provider
        )
        
        return {
            "success": True,
            "message": "Generation started",
            "data": {
                "job_id": job_id,
                "status": job.status.value,
                "check_status_url": f"/api/jobs/{job_id}"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {str(e)}")


@app.post("/api/generate/variation")
def generate_variation(
    request: GenerateVariationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate a variation of an existing image (async)"""
    try:
        # Create job record
        job_id = str(uuid.uuid4())
        provider = request.provider or "huggingface"
        
        job = GenerationRequest(
            job_id=job_id,
            task_type="image-variation",
            prompt=request.prompt,
            source_image_url=request.image_url,
            status=JobStatus.PENDING,
            provider=provider
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start background task
        background_tasks.add_task(
            process_image_generation,
            job_id=job_id,
            task_type="image-variation",
            prompt=request.prompt,
            source_image_url=request.image_url,
            provider=provider
        )
        
        return {
            "success": True,
            "message": "Variation generation started",
            "data": {
                "job_id": job_id,
                "status": job.status.value,
                "check_status_url": f"/api/jobs/{job_id}"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start variation: {str(e)}")


# === JOB STATUS ENDPOINT ===
@app.get("/api/jobs/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Check the status of a generation job"""
    job = db.query(GenerationRequest).filter(GenerationRequest.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response_data = {
        "job_id": job.job_id,
        "task_type": job.task_type,
        "status": job.status.value,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }
    
    if job.status == JobStatus.COMPLETED:
        response_data["result_image_url"] = job.result_image_url
    elif job.status == JobStatus.FAILED:
        response_data["error"] = job.error_message
    
    return {
        "success": True,
        "data": response_data
    }

