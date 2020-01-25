import os
os.environ['APP_LIST'] = str([
                            'crawl',
                            'gsearch',
                            'gsearch.keyword'
                        ])

from base.settings.django import *

API_APP_LIST = [
                'gsearch.keyword',
            ]
