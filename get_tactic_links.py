import argparse
import sys
import time
import math
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Parse Arguments
parser = argparse.ArgumentParser(description='Get the list of links to all tactics listed on FMBase Tactic Tester page.')
parser.add_argument('--link', help='Link to FMBase Tactic Tester page')
parser.add_argument('--output', help='Path to be created for the output file')
args = parser.parse_args()

def fmbase_page_generator(driver, page):
    """ Generator that returns the driver after loading each page on FMBase."""
    driver.get(page)
    while True:
        try:
            # Find button named 'Next'
            el = driver.find_element(By.XPATH,"//a[text()='Next']")
            
            
            # Wait until element is clickable, in case we are rapidly loading the page
            wait = WebDriverWait(driver, 10)
            wait.until(EC.element_to_be_clickable(el))
            
            # Calculate href for the button that will replace 'Next' after we click on it.
            h = el.get_attribute('href')
            h = h.split('/')[-2:]
            h[-1] = str( int(h[-1]) + 1)
            h = '/'.join(h)
            href_cond = f"//a[text()='Next'  and  contains(@href, '{h}')]"
            
            # Yield the driver as is, so that we can extract further info about the page on this state
            yield driver

            # Check if we are at the last page
            if el.get_attribute("class") == 'btn btn-disabled':
                break

            #Click
            el.click()
            # Wait until button updates
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH,href_cond)))

        except NoSuchElementException:
            break

driver = webdriver.Firefox()
tactic_hrefs = []
for i, page in enumerate(fmbase_page_generator(driver,args.link)):
    print("Page ",i + 1)
    # Add link to each tactic
    tactic_hrefs += [x.get_attribute('href') for x in driver.find_elements(By.XPATH,"//a[text()='Show tactic']")]

with open(args.output, 'w') as f:
    f.write('\n'.join(tactic_hrefs))
