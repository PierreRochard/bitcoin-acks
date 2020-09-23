from bitcoin_acks.database import session_scope
from bitcoin_acks.logging import log
from bitcoin_acks.models import Invoices


class PaymentProcessor(object):
    @staticmethod
    def process_invoice_data(invoice_data):
        log.debug('process_invoice_data', invoice_data=invoice_data)
        with session_scope(echo=True) as db_session:
            invoice = db_session.query(Invoices).filter(Invoices.id == invoice_data['id']).one()
            invoice.status = invoice_data['status']
            invoice.data = invoice_data
