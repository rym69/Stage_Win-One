from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from google_trans_new import google_translator 
import pandas as pd
import codecs
import requests, time, random, csv, os, sys
from random import randint


joblist = []

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
    #randomNbForIpAdd = randint(0, len(proxies) - 1) 
    #webdriver.DesiredCapabilities.CHROME['proxy'] = {
    #    "httpProxy":proxies[randomNbForIpAdd],
    #    "httpsProxy":proxies[randomNbForIpAdd],
    #    "ftpProxy":proxies[randomNbForIpAdd],
    #    "sslProxy":proxies[randomNbForIpAdd],
    #    "noProxy":None,
    #    "proxyType":"MANUAL",
    #    "class":"org.openqa.selenium.Proxy",
    #    "autodetect":False
    #}
    driver = webdriver.Chrome(os.getcwd() + '/' + chrome_driver, options=chrome_options)
    driver.maximize_window()
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrapIndeed(page):
    driver = set_driver()
    driver.get(f'https://fr.indeed.com/emplois?q=banque%20assurance&l=france&start={page}')
    wait = WebDriverWait(driver, 20)
    try:
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'popover-x-button-close')))
            popover = driver.find_element_by_class_name('popover-x-button-close')
            popover.click()
        except:
            print('No popover')

        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jobsearch-SerpJobCard')))
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'jobsearch-SerpJobCard')))
        divs = driver.find_elements_by_class_name('jobsearch-SerpJobCard')
        action = ActionChains(driver)
        for item in divs:
            action.move_to_element(to_element = item)
            title = item.find_element_by_tag_name('a').text.strip()
            company = item.find_element_by_class_name('company').text.strip()
            try:
                salary = item.find_element_by_class_name('salaryText').text.strip()
            except: 
                salary =''
            
            try:
                item.click()
                wait.until(EC.presence_of_element_located((By.ID, 'vjs-content')))
                description = driver.find_element_by_id('vjs-content').text.strip()
                description = description.replace('\n', ' ').replace('\r', '')
            except Exception as e: 
                description = 'Pas de description'
                print('failed')
                print(e)
            
            job = {
                'title': title,
                'company': company,
                'salary': salary,
                'summary' : description   
            }
            
            joblist.append(job)
            time.sleep(5)

        driver.close()
        driver.quit()
    except Exception as ex:
        print('An error occured')
        print(ex)
        return

for i in range(0, 10, 10):
    try:
        print(f"Scrapping page {(i - 10)/10}")
        scrapIndeed(i)
    except Exception as e:
        print(e)
        break

df = pd.DataFrame(joblist)
print(df.head())
df.to_csv('demo.csv')
