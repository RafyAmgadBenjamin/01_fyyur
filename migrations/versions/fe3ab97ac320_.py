"""empty message

Revision ID: fe3ab97ac320
Revises: 68070783276d
Create Date: 2020-01-18 23:49:16.914478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe3ab97ac320'
down_revision = '68070783276d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    op.drop_column('Venue', 'seeking_venue')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_venue', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('Venue', 'seeking_talent')
    # ### end Alembic commands ###
