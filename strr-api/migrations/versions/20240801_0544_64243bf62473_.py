"""empty message

Revision ID: 64243bf62473
Revises: ac23b69c2c1a
Create Date: 2024-08-01 05:44:20.264084

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '64243bf62473'
down_revision = 'ac23b69c2c1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('certificates', schema=None) as batch_op:
        batch_op.drop_constraint('certificates_registration_number_key', type_='unique')
        batch_op.drop_column('registration_number')
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('registration_number', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_registrations_registration_number'), ['registration_number'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_registrations_registration_number'))
        batch_op.drop_column('registration_number')

    with op.batch_alter_table('certificates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('registration_number', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.create_unique_constraint('certificates_registration_number_key', ['registration_number'])
    # ### end Alembic commands ###