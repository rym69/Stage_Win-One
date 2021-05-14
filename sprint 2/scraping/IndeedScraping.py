from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from google_trans_new import google_translator 
import pandas as pd
import codecs
import requests, time, random, csv, os, sys
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
# pip install beautifulsoup4
# pip install requests
# pip install selenium



##scrapinf appel d'offre sur indeed secteur banque et assurances

def extract (page):
    headers= {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}
    #url = f'https://fr.indeed.com/emplois?q=banque%20assurance&l=france&advn=9344337646366269&vjk=e81eb77f7922d735={page}'
    url = f'https://fr.indeed.com/emplois?q=banque%20assurance&l=france&start={page}'
    r= requests.get(url, headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def set_driver():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_driver = 'chromedriver'
    driver = webdriver.Chrome(os.getcwd() + '/' + chrome_driver, options=chrome_options)
    driver.maximize_window()
    return driver


def get_jobs_description(wait, id, driver):
    #wait = WebDriverWait(driver, 10)
    #driver.get(url)
    try:
        popover = driver.find_element_by_class_name('popover-x-button-close')
        popover.click()
    except:
        print('No popover')

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jobsearch-SerpJobCard')))
    click = driver.find_element_by_id(id)
    job = click.find_element_by_class_name('summary')
    wait.until(EC.element_to_be_clickable((By.ID, id)))
    try:
        job.click()
        wait.until(EC.presence_of_element_located((By.ID, 'vjs-content')))
        scraped_description = driver.find_element_by_id('vjs-content').text
    except (ElementClickInterceptedException, TimeoutException):
        #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #job.click()
        #wait.until(EC.presence_of_element_located((By.ID, 'vjs-content')))
        #scraped_description = driver.find_element_by_id('vjs-content').text
        scraped_description = "No description"
        print('No element')

    
    return scraped_description


def transform(soup):
    divs = soup.find_all('div', class_ = 'jobsearch-SerpJobCard')
    driver = set_driver()
    wait = WebDriverWait(driver, 10)
    driver.get('https://fr.indeed.com/emplois?q=banque%20assurance&l=france&start=0')
    
    for item in divs:
        title = item.find('a').text.strip()
        company = item.find('span', class_ = 'company').text.strip()
        try:
            salary = item.find('span', class_='salaryText').text.strip()
        except: 
            salary =''
        summary = item.find('div', {'class': 'summary'}).text.strip().replace('\n', '')
        summaryID = item.get('id')
        #url = 'https://fr.indeed.com/emplois?q=banque%20assurance&l=france&advn=9344337646366269'
        description = get_jobs_description(wait, summaryID, driver)
        
        job = {
            'title': title,
            'company': company,
            'salary': salary,
            'summary' : description   
        }
        joblist.append(job)
        time.sleep(2)

    driver.close()
    driver.quit()
    return

joblist = []

nbPage = 0
for i in range(0,2,1):
    print(f'Getting page, {i}')
    c = extract(nbPage)
    transform(c)
    nbPage += 10
    
df = pd.DataFrame(joblist)
print(df.head())
df.to_csv('jobsBanque7.csv')