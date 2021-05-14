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


profile_list = []

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

def scrap_profiles():
    driver = set_driver()
    driver.get('https://entreprise.pole-emploi.fr/recherche-profil/rechercheprofil')
    wait = WebDriverWait(driver, 20)
    action = ActionChains(driver)
    more_buttons = True
    counter = 0
    try:
        wait.until(EC.presence_of_all_elements_located((By.ID, 'footer_tc_privacy')))
        popover = driver.find_element_by_id('footer_tc_privacy_button_2')
        popover.click()
    except:
        print('No popover')

    input_field = driver.find_element_by_id('token-input-champsMultitagQuoi')
    input_field.send_keys('banque assurance')
    submit_button = driver.find_element_by_id('lancerRechercheCv')
    submit_button.click()

    while more_buttons and counter < 10:
        try:
            time.sleep(3)
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'btn')))
            container = driver.find_element_by_id('divParenteBtVoirPlus')
            button_plus = container.find_element_by_tag_name('button')
            action.move_to_element(to_element = button_plus)
            button_plus.click()
            counter += 1
        except Exception as e:
            print(e)
            more_buttons = False
            counter += 1
        if more_buttons == False or counter == 10:
            break
            
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'list-unstyled')))
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'cv-result')))
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'cv-result')))
    cards_container = driver.find_element_by_id('zoneAfficherTrancheCv1')
    ul_container = cards_container.find_element_by_tag_name('ul')
    cards = ul_container.find_elements_by_tag_name('li')
    for item in cards:
        try:
            #action.move_to_element(to_element = item)
            title_to_click = item.find_element_by_class_name('text-entreprise')
            driver.execute_script("arguments[0].scrollIntoView();", title_to_click)
            driver.execute_script("arguments[0].click();", title_to_click)
            
            #title_to_click.click()
        except Exception as prb:
            print(prb)
            print('No clicl on title or no movement')

        wait.until(EC.presence_of_element_located((By.ID, 'zoneAfficherDetailProfil')))
        modal = driver.find_element_by_id('zoneAfficherDetailProfil')
        time.sleep(5)
        try:
            title = modal.find_element_by_class_name('text-entreprise').text.strip()
            resume = modal.find_element_by_tag_name('blockquote').text.strip()
        except:
            print("No title and resume")
            pass
        strengths = []
        try:
            ul_list = modal.find_element_by_class_name('media-body-more').find_element_by_tag_name('ul').find_elements_by_class_name('competence')
            for i in ul_list:
                span = i.find_element_by_tag_name('span')
                strengths.append(span.text.strip())
        except:
            print('No strengths')
        
        final_experiences = []
        try:
            body_profile = modal.find_element_by_class_name('profil-bd-content')
            list_experiences = body_profile.find_element_by_class_name('list-event').find_elements_by_tag_name('li')
            for experience in list_experiences:
                experience_title = experience.find_element_by_class_name('title').text.strip()
                company = experience.find_element_by_class_name('place').text.strip()
                description_container = experience.find_element_by_class_name('collapse-container')
                experience_description = description_container.find_element_by_tag_name('p').text.strip()
                experience_competences = description_container.find_element_by_tag_name('ul').find_elements_by_tag_name('li')
                experience_competences_list = []
                for comp in experience_competences:
                    text = comp.get_attribute('title')
                    experience_competences_list.append(text)
                experience_item = {
                    'title': experience_title,
                    'company': company,
                    'description': experience_description,
                    'competences': experience_competences_list
                }
                final_experiences.append(experience_item)
        except:
            print('No experiences')
        
        competences = []
        try:
            zone_competences = modal.find_element_by_id('zoneAfficherCompetences')
            competences_list = zone_competences.find_element_by_class_name('list-tag-group-container').find_elements_by_tag_name('li')
            for competence in competences_list:
                elements_list = competence.find_element_by_tag_name('ul').find_elements_by_tag_name('li')
                for li in elements_list:
                    text_competence = li.get_attribute('title')
                    competences.append(text_competence)
        except:
            print('No competences')
        
        button_close = driver.find_element_by_class_name('modal-details-close')
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'modal-details-close')))
        button_close.click()

        profile = {
            'title': title,
            'resume': resume,
            'strengths': strengths,
            'expriences': final_experiences,
            'competences': competences
        }

        profile_list.append(profile)
        time.sleep(5)

    driver.close()
    driver.quit()

scrap_profiles()
df = pd.DataFrame(profile_list)
print(df.head())
df.to_csv('profiles.csv')
            
