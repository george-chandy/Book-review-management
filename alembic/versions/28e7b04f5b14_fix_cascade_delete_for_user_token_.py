"""Fix cascade delete for user-token relationship

Revision ID: 28e7b04f5b14
Revises: 2d263caa7385
Create Date: 2025-03-13 13:12:54.118245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '28e7b04f5b14'
down_revision: Union[str, None] = '2d263caa7385'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('email_verification_token_user_id_key', 'email_verification_token', type_='unique')
    op.drop_constraint('email_verification_token_user_id_fkey', 'email_verification_token', type_='foreignkey')
    op.create_foreign_key(None, 'email_verification_token', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.alter_column('users', 'gender',
               existing_type=postgresql.ENUM('male', 'female', 'other', name='gender_enum'),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('users', 'dob',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'dob',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=False)
    op.alter_column('users', 'gender',
               existing_type=sa.String(),
               type_=postgresql.ENUM('male', 'female', 'other', name='gender_enum'),
               existing_nullable=False)
    op.drop_constraint(None, 'email_verification_token', type_='foreignkey')
    op.create_foreign_key('email_verification_token_user_id_fkey', 'email_verification_token', 'users', ['user_id'], ['id'])
    op.create_unique_constraint('email_verification_token_user_id_key', 'email_verification_token', ['user_id'])
    # ### end Alembic commands ###
