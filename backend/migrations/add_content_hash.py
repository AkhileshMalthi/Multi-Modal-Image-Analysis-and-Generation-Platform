"""Add content_hash to ImageMeta for deduplication

Revision ID: add_content_hash
Revises: 
Create Date: 2025-12-20

"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    """Add content_hash and file_size columns to images table"""
    # Add content_hash column (SHA256 hash, 64 characters)
    op.add_column('images', 
        sa.Column('content_hash', sa.String(64), nullable=True)
    )
    
    # Add file_size column
    op.add_column('images',
        sa.Column('file_size', sa.Integer(), nullable=True)
    )
    
    # Create unique index on content_hash for deduplication
    op.create_index('ix_images_content_hash', 'images', ['content_hash'], unique=True)


def downgrade():
    """Remove content_hash and file_size columns"""
    op.drop_index('ix_images_content_hash', table_name='images')
    op.drop_column('images', 'file_size')
    op.drop_column('images', 'content_hash')
