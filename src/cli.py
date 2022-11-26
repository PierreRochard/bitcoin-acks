from tempfile import TemporaryDirectory
import traceback

from bitcoin_acks.github_data.polling_data import PollingData
from bitcoin_acks.github_data.pull_requests_data import PullRequestsData
from bitcoin_acks.logging import log
from bitcoin_acks.scripts.send_email import email


class Main(object):
    @staticmethod
    def update_pull_requests(manual_date=None):
        polling_data = PollingData('github')
        try:
            if polling_data.is_polling():
                raise Exception('GitHub is already being polled')
            polling_data.start()
            with TemporaryDirectory() as temporary_directory_path:
                pull_requests_data = PullRequestsData('bitcoin', 'bitcoin', temporary_directory_path)
                if manual_date:
                    pull_requests_data.update_from_manual_date()
                else:
                    pull_requests_data.update()
        except Exception as e:
            log.error('polling exception', exc_info=e)
            tb = traceback.format_exc()
            email.notify('Polling exception\n\n' + tb)
        else:
            log.debug('Successful poll')
        finally:
            polling_data.stop()


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Change the schema')

    parser.add_argument('-m',
                        dest='manual',
                        default=False,
                        action='store_true'
                        )
    args = parser.parse_args()
    Main.update_pull_requests(manual_date=args.manual)
