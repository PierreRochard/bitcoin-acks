from bitcoin.core import COIN
from btcpay import BTCPayClient
from flask import url_for

from bitcoin_acks.logging import log


class RecipientBTCPay(object):
    client: BTCPayClient

    def __init__(self, client: BTCPayClient):
        self.client = client

    def get_pull_request_invoice(self, amount: int, bounty_id: str, pull_request_number: int):
        notification_url = url_for('payment_notification', _external=True)
        if 'localhost' in notification_url:
            notification_url = notification_url.replace('localhost', 'webapp')

        payload = {
            'price': amount / COIN,
            'currency': 'BTC',
            'orderId': bounty_id,
            'itemDesc': f'Payment for pull request {pull_request_number}',
            'redirectURL': url_for('bounties-payable.index_view', _external=True),
            'notificationURL': notification_url,
            'extendedNotifications': True
        }
        log.debug('btcpay client request', payload=payload)
        invoice_data = self.client.create_invoice(payload=payload)
        log.debug('btcpay server response', invoice_data=invoice_data)
        return invoice_data
