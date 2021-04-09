from selenium import webdriver
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
    url = f'https://fr.indeed.com/emplois?q=banque%20assurance&l=france&advn=9344337646366269&vjk=e81eb77f7922d735={page}'
    r= requests.get(url, headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def transform(soup):
    divs = soup.find_all('div', class_ = 'jobsearch-SerpJobCard')
    for item in divs:
        title = item.find('a').text.strip()
        company = item.find('span', class_ = 'company').text.strip()
        try:
            salary = item.find('span', class_='salaryText').text.strip()
        except: 
            salary =''
        summary = item.find('div', {'class': 'summary'}).text.strip().replace('\n', '')
        
        job = {
            'title': title,
            'company': company,
            'salary': salary,
            'summary' : summary   
        }
        joblist.append(job)
    return

joblist = []

for i in range(0,1000,20):
    print(f'Getting page, {i}')
    c = extract(0)
    transform(c)
    
df = pd.DataFrame(joblist)
print(df.head())
df.to_csv('jobsBanque7.csv')