from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from .database import Base
import enum


class ImageMeta(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    s3_url = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, index=True)  # Foreign key to ImageMeta
    image_url = Column(String)
    analysis_type = Column(String, index=True)  # 'caption', 'vqa', 'object-detection'
    prompt = Column(Text, nullable=True)  # For VQA questions
    result = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationRequest(Base):
    __tablename__ = "generation_requests"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)  # UUID for tracking
    task_type = Column(String)  # 'text-to-image', 'image-variation'
    prompt = Column(Text)
    source_image_url = Column(String, nullable=True)  # For variations
    result_image_url = Column(String, nullable=True)  # Generated image S3 URL
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    error_message = Column(Text, nullable=True)
    provider = Column(String, default="huggingface")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
