import gevent.monkey; gevent.monkey.patch_all()
from gevent.pool import Pool

from datetime import datetime, timedelta
import copy 
import time 
import json 
import random 
import logging
from functools import partial
from traceback import format_exc
import argparse

import requests
import yaml
import s3plz
import json

import geo
import uber

INCLUDE_BOROS = ['Brooklyn', 'Manhattan']
CONCURRENT = 10


log = logging.getLogger()


def compute_trips(neighborhoods):
    """
    For each neighborhood, get a price estimate for travelling to all other neighborhoods
    """
    coords = []
    for i, hood in enumerate(neighborhoods):
        if hood['boroname'] in INCLUDE_BOROS:
            candidates = copy.copy(neighborhoods)
            del candidates[i]
            hood_coords = []
            for candidate in candidates:
                yield {
                    'from': hood, 
                    'to': candidate, 
                    'coords': hood['centroid'] + candidate['centroid']
                    }

def store(trip, s3):
    """
    store a trip on s3
    """
    params = {
        'from': trip['from']['ntacode'],
        'to': trip['to']['ntacode']
    }
    s3path = s3.put(trip, 'uber-trips/{@date_path}/{from}-{to}-{@timestamp}.json.gz', **params)
    return s3path

def slack_msg(msg, config):
    """
    """
    payload = {'text':msg, 'icon_emoji': ':taxi:','username': 'uber-scraper', 'channel':'#logs'}
    requests.post(config['SLACK_WEBHOOK_URL'], data=json.dumps(payload))

def worker(trip, config={}, s3=None):
    """
    Get an trip and compute price from uber API
    """
    msg = 'INFO: Estimating Trip FROM ' + trip['from']['ntaname'] +  \
          ' TO ' + trip['to']['ntaname']
    try:
        token = random.choice(config['UBER_SERVER_TOKENS'])
        print(msg)
        trip['prices'] = uber.get_estimate(*trip['coords']+[token])
        trip['time'] = datetime.utcnow().isoformat()
        s3path = store(trip, s3)
        print('INFO: Stored at {}'.format(s3path))

    except Exception as e:
        time.sleep(1)
        msg = ':thumbsdown:\n*Traceback:*\n```\n{}\n{}\n```\n'.format(msg, format_exc())
        slack_msg(msg, config)
        print('ERROR:\n' + format_exc())


def poll():
    """
    Get estimates for all trips concurrently
    """

    # parser
    parser = argparse.ArgumentParser('ubernyc')
    parser.add_argument('-g', '--geojson', type=str)
    parser.add_argument('-w', '--workers', type=int, default=1)
    parser.add_argument('-c', '--config', type=str)
    opts = parser.parse_args()

    # setup
    config = yaml.safe_load(open(opts.config))
    s3 = s3plz.connect('s3://brianabelson', 
        serializer='json.gz',
        key=config['AWS_ACCESS_KEY_ID'],
        secret=config['AWS_SECRET_ACCESS_KEY'])

    # compute trips
    shp = geo.read_geojson(opts.geojson)
    neighborhoods = list(geo.compute_centroids(shp))
    trips = list(compute_trips(neighborhoods))

    # scrape
    while True:
        random.shuffle(trips)
        msg = "INFO: Fetching prices for {} trips".format(len(trips))
        print(msg)
        msg = ':thumbsup:\n {}'.format(msg)
        slack_msg(msg, config)
        if opts.workers > 1:
            pool = Pool(CONCURRENT)
            wrkr = partial(worker, config=config, s3=s3)
            for trip in pool.imap_unordered(wrkr, trips): pass
        else:
            for trip in trips:
                worker(trip, config=config, s3=s3)
        msg = ':thumbsup:\n Finished estimating *{}* trips'.format(len(trips))
        slack_msg(msg)

