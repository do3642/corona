"""empty message

Revision ID: 6f53c23c72cd
Revises: aae9a5069b17
Create Date: 2024-12-10 13:11:04.894612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f53c23c72cd'
down_revision = 'aae9a5069b17'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('country_translation',
    sa.Column('country_code', sa.String(length=10), nullable=False),
    sa.Column('country_korean', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('country_code')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('country_translation')
    # ### end Alembic commands ###
