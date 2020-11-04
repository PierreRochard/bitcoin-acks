from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from bitcoin_acks.database.base import Base
from bitcoin_acks.models.bounties import Bounties
from bitcoin_acks.models.users import Users


class Invoices(Base):
    __tablename__ = 'invoices'

    id = Column(String, primary_key=True)
    status = Column(String)
    url = Column(String)
    data = Column(JSONB)

    bounty_id = Column(String,
                       ForeignKey('bounties.id'),
                       nullable=False)

    bounty = relationship(Bounties, backref='invoices')

    recipient_user_id = Column(String)
    recipient = relationship(Users,
                             primaryjoin=recipient_user_id == Users.id,
                             foreign_keys='[Invoices.recipient_user_id]',
                             backref='invoices_receivable'
                             )

    payer_user_id = Column(String)
    payer = relationship(Users,
                         primaryjoin=payer_user_id == Users.id,
                         foreign_keys='[Invoices.payer_user_id]',
                         backref='invoices_payable'
                         )

    def __repr__(self):
        return f'( {self.id} {self.status} )'
