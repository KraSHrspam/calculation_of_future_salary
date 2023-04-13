import requests
from pprint import pprint
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv
from time import sleep


def get_vacancies_hh(language):
    salaries = []
    url = "https://api.hh.ru/vacancies"
    page = 0
    pages_number = 1
    while page < pages_number:
        payload = {"text": language,
                   "area": "1",
                   "page": page}
        page_response = requests.get(url, params=payload)
        sleep(0.2)
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload["pages"]
        page += 1
        vacancies_found = page_payload['found']
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
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }

def get_vacancies_sj(sj_secret_key, language):
    salaries = []
    url = "https://api.superjob.ru/2.0/vacancies/"
    page = 1
    while True:
        headers = {"X-Api-App-Id":sj_secret_key,
                   "Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "town":4,
            "keyword":language,
            "page":page,
        }
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        vacancies_found = response.json()["total"]
        vacancies = response.json()["objects"]
        page += 1
        for vacansy in vacancies:
            predicted_salary = predict_rub_salary(vacansy["payment_from"], vacansy["payment_to"], vacansy["currency"])
            if predicted_salary:
                salaries.append(predicted_salary)
        if not response.json()["more"]:
            break
    vacancies_processed = len(salaries)
    if vacancies_processed:
        average_salary = sum(salaries) // vacancies_processed
    else:
        average_salary = 0
    return {
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }

def predict_rub_salary(salary_from, salary_to, salary_currency):
    if salary_currency != "RUR" and salary_currency != "rub":
        return
    if salary_from and salary_to:
        return (salary_from+salary_to)/2
    elif salary_from:
        return salary_from*1.2
    elif salary_to:
        return salary_to*0.8

def make_table(languages_params, title):
    table_content = [
        ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"],
    ]
    for language, languages_params in languages_params.items():
        table_content.append([language, languages_params["vacancies_found"], languages_params["vacancies_processed"], languages_params["average_salary"]])
    table = AsciiTable(table_content,title)
    print(table.table)


if __name__ == "__main__":
    load_dotenv()
    languages = ["Python", "Java", "JavaScript"]
    sj_secret_key = os.getenv("SECRET_KEY")
    language_params_hh = {
    }
    language_params_sj = {
    }
    for language in languages:
        language_params_hh[language] = get_vacancies_hh(language)
        language_params_sj[language] = get_vacancies_sj(sj_secret_key, language)
    make_table(language_params_sj, "SuperJob")
    make_table(language_params_hh, "HeadHunter")