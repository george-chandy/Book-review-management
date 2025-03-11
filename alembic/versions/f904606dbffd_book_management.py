"""book_management

Revision ID: f904606dbffd
Revises: 1816c82693f4
Create Date: 2025-03-09 08:25:54.756657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f904606dbffd'
down_revision: Union[str, None] = '1816c82693f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'authors',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False)
    )
    
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False, unique=True)
    )
    
    op.create_table(
        'genres',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False, unique=True)
    )
    
    op.create_table(
        'languages',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False, unique=True)
    )
    
    op.create_table(
        'books',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('authors.id'), nullable=False),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=False),
        sa.Column('genre_id', sa.Integer(), sa.ForeignKey('genres.id'), nullable=False),
        sa.Column('language_id', sa.Integer(), sa.ForeignKey('languages.id'), nullable=False),
        sa.Column('coverimage_url', sa.String(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=False),
        sa.Column('isbn', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('is_featured', sa.Boolean(), default=False),
        sa.Column('is_published', sa.Boolean(), default=False),
        sa.Column('average_rating', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('book_id', sa.Integer(), sa.ForeignKey('books.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('reviews')
    op.drop_table('books')
    op.drop_table('languages')
    op.drop_table('genres')
    op.drop_table('categories')
    op.drop_table('authors')
