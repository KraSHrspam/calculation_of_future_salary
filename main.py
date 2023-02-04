import requests
from pprint import pprint


def get_vacansies_hh(language):
    payload = {"text": language,
               "area": "1",}
    url = "https://api.hh.ru/vacancies"
    response = requests.get(url, params=payload)
    response.raise_for_status()
    for vacansy in response.json()['items']:
        if vacansy['salary']:
            predicted_salary = predict_rub_salary(vacansy['salary']['from'], vacansy['salary']['to'], vacansy['salary']['currency'])
            pprint(predicted_salary)
    return response.json()

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
    languages = ["Python", "Java", "Scala", "Shell", "JavaScript", "C++", "C#"]
    language_params = {
    }
    for language in languages:
        language_params[language] = get_vacansies_hh(language)["found"]

    pprint(language_params)