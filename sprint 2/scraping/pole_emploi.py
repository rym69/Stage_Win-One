from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
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
    driver = webdriver.Chrome(os.getcwd() + '/' + chrome_driver, options=chrome_options)
    driver.maximize_window()
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def scrap_pole_emploi():
    driver = set_driver()
    driver.get('https://candidat.pole-emploi.fr/offres/recherche?domaine=C&lieux=01P&motsCles=assurances,banque&offresPartenaires=true&range=0-19&rayon=10&tri=0')
    wait = WebDriverWait(driver, 20)
    action = ActionChains(driver)
    more_buttons = True
    try:
        wait.until(EC.presence_of_all_elements_located((By.ID, 'footer_tc_privacy')))
        popover = driver.find_element_by_id('footer_tc_privacy_button_2')
        popover.click()
    except:
        print('No popover')
    while more_buttons:
        print('in if')
        try:
            time.sleep(3)
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'btn')))
            container = driver.find_element_by_id('zoneAfficherPlus')
            button_plus = container.find_element_by_tag_name('a')
            action.move_to_element(to_element = button_plus)
            button_plus.click()
            print('in try')
        except Exception as e:
            print(e)
            more_buttons = False
            print('in except')
        if more_buttons == False:
            break
    
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'result')))
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'result')))
    cards = driver.find_elements_by_class_name('result')
    for item in cards:
        try:
            action.move_to_element(to_element = item)
            item.click()
        except:
            pass

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'modal-content')))
        wait.until(EC.presence_of_element_located((By.ID, 'detailOffreVolet')))
        wait.until(EC.element_to_be_clickable((By.ID, 'detailOffreVolet')))
        modal = driver.find_element_by_class_name('modal-content')
        time.sleep(5)
        try:
            detailed_offer = driver.find_element_by_id('detailOffreVolet')
            title = detailed_offer.find_element_by_tag_name('h2').text.strip()
            divDescription = detailed_offer.find_element_by_class_name('description')
            description = divDescription.find_element_by_tag_name('p').text.strip().replace('\n', ' ').replace('\r', '')
        except:
            title = "No title",
            description = "No description"
            pass
        button = driver.find_element_by_class_name('modal-details-close')
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'modal-details-close')))
        button.click()

        job = {
            'title': title,
            'description': description
        }

        joblist.append(job)
        time.sleep(5)

    driver.close()
    driver.quit()



scrap_pole_emploi()
df = pd.DataFrame(joblist)
print(df.head())
df.to_csv('first.csv')
