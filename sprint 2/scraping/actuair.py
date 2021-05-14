from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
import codecs
import requests, time, random, csv, os, sys
from random import randint

jobList = []

userAgents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Roku4640X/DVP-7.70 (297.70E04154A)',
    'Mozilla/5.0 (Linux; U; Android 4.2.2; he-il; NEO-X5-116A Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30',
    'AppleTV6,2/11.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
]

def set_driver():
    randomNbForUsrAgent = randint(0, len(userAgents) - 1)
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument(f"user-agent={userAgents[randomNbForUsrAgent]}")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_driver = 'chromedriver'
    driver = webdriver.Chrome(os.getcwd() + '/' + chrome_driver, options=chrome_options)
    driver.maximize_window()
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver



def scrap_actuair():
    driver = set_driver()
    driver.get('https://www.optioncarriere.com/emploi-actuaire.html')
    wait = WebDriverWait(driver, 20)
    action = ActionChains(driver)
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'li')))
    wait.until(EC.element_to_be_clickable((By.TAG_NAME, 'li')))
    jobs_list = driver.find_element_by_class_name('jobs')
    jobs = jobs_list.find_elements_by_tag_name('article')
    jobs[0].click()
    for i in range(173):
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'main')))
        time.sleep(1)
        title = driver.find_element_by_tag_name('h1').text.strip()
        company = driver.find_element_by_class_name('company').text.strip()
        content = driver.find_element_by_class_name('content').text.strip().replace('\n', ' ').replace('\r', '')
        job = {
            'title': title,
            'company': company,
            'description': content
        }
        jobList.append(job)
        print('Job ok ', i)
        button = driver.find_element_by_class_name('next')
        button.click()

    driver.close()
    driver.quit()

scrap_actuair()
df = pd.DataFrame(jobList)
print(df.head())
df.to_csv('actuair.csv')
