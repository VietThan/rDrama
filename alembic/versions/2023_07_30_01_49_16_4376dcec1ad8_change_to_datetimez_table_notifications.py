"""Change to datetimez table notifications

Revision ID: 4376dcec1ad8
Revises: 84e02ade75a8
Create Date: 2023-07-30 01:49:16.238320+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.functions import now


# revision identifiers, used by Alembic.
revision = '4376dcec1ad8'
down_revision = '84e02ade75a8'
branch_labels = None
depends_on = None

table_name = 'notifications'
from_column = 'created_utc'
to_column = 'created_datetimez'

def upgrade():
    op.add_column(table_name, sa.Column(to_column, sa.DateTime(timezone=True), nullable=True, server_default=now()))
    op.execute(f"""
        UPDATE {table_name} 
        SET {to_column} = 
            CASE 
                WHEN {from_column} > 0 THEN 
                    (timestamp 'epoch' + {from_column} * interval '1 second') at time zone 'utc' 
                ELSE NULL 
            END
    """)
    op.alter_column(table_name, to_column, nullable=False)
    op.drop_column(table_name, from_column)


def downgrade():
    """
    Downgrade will truncate the milliseconds.
    """
    op.add_column(table_name, sa.Column('created_utc', sa.Integer(), server_default=sa.text('0'), nullable=True))
    op.execute(f"""
        UPDATE {table_name} 
        SET created_utc = 
            COALESCE(
                EXTRACT(EPOCH FROM {to_column})::integer,
                0
            )
        """)
    op.alter_column(table_name, from_column, nullable=False)
    op.drop_column(table_name, to_column)
