import os
from time import sleep

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_vacancies_statistics_hh(language, request_delay_time):
    salaries = []
    url = "https://api.hh.ru/vacancies"
    moscow_area_number = 1
    page = 0
    pages_number = 1
    while page < pages_number:
        payload = {"text": language,
                   "area": moscow_area_number,
                   "page": page}
        page_response = requests.get(url, params=payload)
        sleep(request_delay_time)
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload["pages"]
        page += 1
        vacancies_found = page_payload['found']
        for vacansy in page_payload['items']:
            if vacansy['salary']:
                predicted_salary = predict_rub_salary(
                    vacansy['salary']['from'],
                    vacansy['salary']['to'],
                    vacansy['salary']['currency']
                )
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


def get_vacancies_statistics_sj(sj_secret_key, language):
    salaries = []
    url = "https://api.superjob.ru/2.0/vacancies/"
    moscow_town_number = 4
    page = 1
    while True:
        headers = {"X-Api-App-Id": sj_secret_key,
                   "Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "town": moscow_town_number,
            "keyword": language,
            "page": page,
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
        table_content.append([
            language,
            languages_params["vacancies_found"],
            languages_params["vacancies_processed"],
            languages_params["average_salary"]
        ])
    table = AsciiTable(table_content, title)
    return table.table


if __name__ == "__main__":
    load_dotenv()
    request_delay_time = 0.2
    languages = ["Python", "Java", "JavaScript"]
    sj_secret_key = os.getenv("SJ_SECRET_KEY")
    language_params_hh = {}
    language_params_sj = {}
    for language in languages:
        language_params_hh[language] = get_vacancies_statistics_hh(language, request_delay_time)
        language_params_sj[language] = get_vacancies_statistics_sj(sj_secret_key, language)
    print(make_table(language_params_sj, "SuperJob"))
    print(make_table(language_params_hh, "HeadHunter"))
