import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def get_all_vacancy(driver, link):
    all_link_vacancy = []
    driver.get(link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_vacancies = soup.find('div', {'data-qa': 'vacancy-serp__results'})
    vacancies = all_vacancies.find_all('div', {'class': 'vacancy-serp-item__layout'})
    for index, vacancy in enumerate(vacancies):
        vacancy_link = vacancy.find('a', {'class': 'bloko-link'})['href']
        all_link_vacancy.append(vacancy_link)
    return all_link_vacancy

def get_salary(soup):
    page = soup.findAll('div', {'class':'bloko-text bloko-text_large'})
    stp_page = str(page[0])
    if '<div class="wrapper-flat--H4DVL_qLjKLCo1sytcNI">' in stp_page:
        if 'vacancy-salary-compensation-type-net' in stp_page:
            salary = soup.find('div', {'class': 'wrapper-flat--H4DVL_qLjKLCo1sytcNI'}).find('span', {
                'data-qa': 'vacancy-salary-compensation-type-net'}).text
            return salary
        elif 'vacancy-salary-compensation-type-gross' in stp_page:
            salary = soup.find('div', {'class': 'wrapper-flat--H4DVL_qLjKLCo1sytcNI'}).find('span', {
                'data-qa': 'vacancy-salary-compensation-type-gross'}).text
            return salary
        else:
            salary = 'Зарплатная вилка не указана'
            return salary
    else:
        salary = 'Зарплатная вилка не указана'
        return salary

def get_company(soup):
    company = soup.find('div', {"class": "vacancy-company-redesigned"}).find('span', {
        "class": "bloko-header-section-2 bloko-header-section-2_lite"}).next.text.replace(' ', ' ')
    return company

def get_skill_list(soup):
    page = soup.findAll('div', {'class': 'bloko-text bloko-text_large'})
    if '<div class="bloko-tag-list">' in str(page[0]):
        key_skills = soup.find('div', {"class": "bloko-tag-list"}).find_all('div',{"class": "bloko-tag bloko-tag_inline"})
        print(key_skills)
        clr_skill = ''
        for skill in key_skills:
            if not isinstance(skill, str):
                clr_skill += f"{skill.text.replace(' ', ' ') + ' '}"
    else:
        clr_skill = 'Навыки не указаны'
    return clr_skill

def get_city_address(soup):
    try:
        city = soup.find('p', {"data-qa": "vacancy-view-location"}).text
    except AttributeError:
        city = soup.find('span', {"data-qa": "vacancy-view-raw-address"}).text
    return city

def get_vacancy_detail(driver,list_link):
    flask_django_vacancy = []
    print(list_link)
    for vacancy_link in list_link:
        print(vacancy_link)
        driver.get(vacancy_link)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        EC.element_to_be_clickable((By.CLASS_NAME, 'bloko-link.bloko-link_pseudo'))
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        salary = get_salary(soup)
        print(salary)
        company_name = get_company(soup)
        city = get_city_address(soup)
        clr_skill = get_skill_list(soup)
        if 'Django' in clr_skill or 'Flask' in clr_skill:
            vacancy = {
                "link": vacancy_link,
                "salary": salary,
                "company_name": company_name,
                "city": city
            }
            print(vacancy)
            flask_django_vacancy.append(vacancy)
    return flask_django_vacancy


if __name__ == '__main__':

    driver = webdriver.Chrome()
    all_vacancy = get_all_vacancy(driver,'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2')
    data = get_vacancy_detail(driver, all_vacancy)

    with open('result.json', 'w', encoding='utf-8') as f:
        content = json.dump(data, f, indent=4, ensure_ascii=False)


