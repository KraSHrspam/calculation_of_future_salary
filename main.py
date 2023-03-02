import requests
from pprint import pprint
import os
from dotenv import load_dotenv


def get_vacansies_hh(language):
    salaries = []
    url = "https://api.hh.ru/vacancies"
    page = 0
    pages_number = 1
    while page < pages_number:
        page_response = requests.get(url, params={'page': page})
        page_response.raise_for_status()
        payload = {"text": language,
                   "area": "1",
                   "page": page}
        page_payload = page_response.json()
        pages_number = page_payload["pages"]
        page += 1
        vacansies_found = page_payload['found']
        for vacansy in page_payload['items']:
            if vacansy['salary']:
                predicted_salary = predict_rub_salary(vacansy['salary']['from'], vacansy['salary']['to'], vacansy['salary']['currency'])
                if predicted_salary:
                    salaries.append(predicted_salary)
        vacancies_processed = len(salaries)
        if vacancies_processed:
            average_salary = sum(salaries)//vacancies_processed
        else:
            average_salary = 0
        return {
            "vacancies_found": vacansies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary
        }

def get_vacansies_sj(sj_secret_key):
    headers = {"X-Api-App-Id":sj_secret_key,
               "Content-Type": "application/x-www-form-urlencoded"}
    url = "https://api.superjob.ru/2.0/vacancies/"
    payload = {
        "town":4,
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    vacansies = response.json()["objects"]
    for vacansy in vacansies:
        pprint(vacansy["profession"])


def predict_rub_salary(salary_from, salary_to, salary_currency):
    if salary_currency != 'RUR':
        return
    if salary_from and salary_to:
        return (salary_from+salary_to)/2
    elif salary_from:
        return salary_from*1.2
    elif salary_to:
        return salary_to*0.8


if __name__ == "__main__":
    load_dotenv()
    languages = ["Python", "Java", "Scala", "Shell", "JavaScript", "C++", "C#"]
    sj_secret_key = os.getenv("SECRET_KEY")
    language_params = {
    }
    for language in languages:
        language_params[language] = get_vacansies_hh(language)
    get_vacansies_sj(sj_secret_key)
    