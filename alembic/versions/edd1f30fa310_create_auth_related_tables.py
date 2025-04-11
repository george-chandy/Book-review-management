"""create auth-related tables

Revision ID: edd1f30fa310
Revises: 
Create Date: 2025-04-09 18:05:22.597149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'edd1f30fa310'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create gender_enum type
    gender_enum = postgresql.ENUM('male', 'female', 'other', name='gender_enum')
    gender_enum.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('gender', gender_enum, nullable=False),
        sa.Column('dob', sa.DateTime(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('is_email_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column('deactivated_at', sa.DateTime(), nullable=True),
    )

    # Create email_verification_token table
    op.create_table(
        'email_verification_token',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('token', sa.String(255), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create password_reset_token table
    op.create_table(
        'password_reset_token',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('token', sa.String(255), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table('password_reset_token')
    op.drop_table('email_verification_token')
    op.drop_table('users')
    op.execute('DROP TYPE gender_enum')