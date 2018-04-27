import logging
import sys

from bitcoin_acks.webapp.run import create_app

logging.basicConfig(stream=sys.stderr)

app = create_app('bitcoin_acks.webapp.settings.Config')
