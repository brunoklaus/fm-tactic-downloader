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
parser.add_argument('--input', help='Path to input text file, each line is a link to an FMBase tactic')
parser.add_argument('--output', help='which folder to save into')
args = parser.parse_args()

def fmbase_stat_generator(driver, page):
    """ Generator that returns the driver after clicking on overall, subtop, underdog stats."""
    driver.get(page)
    for mode in ["Overall","Subtop","Underdog"]:
        # Find button named 'Next'
        el = driver.find_element(By.XPATH,f"//button[text()='{mode}']")
         # Wait until element is clickable, in case we are rapidly loading the page
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable(el))
        el.click()
        cond = f"//button[text()='{mode}' and @class='btn hover:btn-primary btn-sm mt-2 svelte-hjycpp btn-primary']"
        wait.until(EC.presence_of_element_located((By.XPATH,cond)))

        cond = f"//div/div[@class='stat place-items-center place-content-center svelte-hjycpp']"
        stats = driver.find_elements(By.XPATH,cond)
        yield mode, stats

# Store hrefs for every tactic
with open(args.input,'r') as f:
    tactic_hrefs = f.readlines()
tactic_hrefs = [x.replace('\n','') for x in tactic_hrefs]

# Initialize driver
driver = webdriver.Firefox()

# A list of dictionaries , one for each tactic.
all_dicts = []
for href in tactic_hrefs:
    tactic_dct = {'tactic_href': href}

    # First, we use our stat generator to capture stats (Overall, Subtop, Underdog)
    for mode, stats in fmbase_stat_generator(driver, href):
        cond_key = ".//div[@class='stat-title uppercase svelte-hjycpp']"
        cond_value = ".//div[@class='stat-value svelte-hjycpp' or @class='stat-value text-2xl svelte-hjycpp']"

        # Extract stats
        stat_dct = {k.find_element(By.XPATH,cond_key):k.find_element(By.XPATH,cond_value) for k in stats}
        stat_dct = {k.text:v.text for k,v in stat_dct.items()}
        stat_dct = {k:v for k,v in stat_dct.items() if not k=='FORMATION'}
        stat_dct = {mode + ' ' + k: v for k,v in stat_dct.items()}

        # Append to main dict
        tactic_dct.update(stat_dct)
        
    # use Xpath to get other elements such as the download link, author and so on
    tactic_dct['download_href'] = driver.find_element(By.XPATH,"//div//a[text()='Download']").get_attribute('href')
    tactic_dct['Author'] = driver.find_element(By.XPATH,"//a[@class='flex items-center']//p").text
    tactic_dct['Name'] = driver.find_element(By.XPATH,"//div[@class='bg-primary text-black svelte-hjycpp']").text
    for key in ['Formation', 'Game Version', 'Date Tested']:
        tactic_dct[key] = driver.find_element(By.XPATH,f"//div[text()='{key}']").\
                                        find_element(By.XPATH,"./following-sibling::div").text
    # Append to list
    all_dicts.append(tactic_dct)

# Create DataFrame with pandas, save to CSV
pd.DataFrame.from_records(all_dicts).to_csv(osp.join(args.output, 'metadata.csv'))

