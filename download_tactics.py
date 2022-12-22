import argparse
import sys
import time
import math
import os
import os.path as osp
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

# Parse Arguments
parser = argparse.ArgumentParser(description='Given the links to FMBase tactics, extract all the metadata and download all tactics.')
parser.add_argument('--input', help='Path to input CSV file storing tactic metadata', required=True)
parser.add_argument('--output', help='which folder to save into', required=True)
args = parser.parse_args()

# Read DataFrame
df = pd.read_csv(args.input)
df['filename'] = [x.split('/')[-1] + '.FMF' for x in df['tactic_href'].values]

import os.path as osp
import os
import concurrent.futures

def download_from_url(url, download_path):
    with open(download_path, 'wb') as handle:
        response = requests.get(url, stream=True)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

import requests
os.makedirs(osp.join(args.output,'download'),exist_ok=True)

def download_file(fname, download_link):
    fname = osp.join(args.output,'download',fname)
    if not osp.isfile(fname):
        download_from_url(download_link, fname)

i = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future_to_file = {executor.submit(download_file, fname, download_link): (fname, download_link) for fname, download_link in zip(df['filename'].values,df['download_href'].values)}
    for future in concurrent.futures.as_completed(future_to_file):
        fname, download_link = future_to_file[future]
        try:
            future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (fname, exc))
        else:
            print('%r was downloaded successfully' % fname)
