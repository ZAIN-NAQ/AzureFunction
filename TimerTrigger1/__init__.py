import sys
import os
sys.path.append(os.path.abspath(""))
import datetime
import logging
from .crawler import webcrawler
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    print("Crawler is working!!!")
    webcrawler() 
    print("Crawler Stopped")
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
