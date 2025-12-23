from sqlalchemy import String, DateTime, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime
from typing import Optional
import enum


class ImageMeta(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, index=True)
    s3_url: Mapped[str] = mapped_column(String)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True, nullable=True)  # SHA256 hash for deduplication
    file_size: Mapped[Optional[int]] = mapped_column(nullable=True)  # File size in bytes
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_id: Mapped[int] = mapped_column(index=True)  # Foreign key to ImageMeta
    image_url: Mapped[str] = mapped_column(String)
    analysis_type: Mapped[str] = mapped_column(String, index=True)  # 'caption', 'vqa', 'object-detection'
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # For VQA questions
    result: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationRequest(Base):
    __tablename__ = "generation_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(String, unique=True, index=True)  # UUID for tracking
    task_type: Mapped[str] = mapped_column(String)  # 'text-to-image', 'image-variation'
    prompt: Mapped[str] = mapped_column(Text)
    source_image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # For variations
    result_image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Generated image S3 URL
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String, default="huggingface")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
