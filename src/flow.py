from src.dbmanager import dbmanager


def print_result(result, msg):
    print(msg)
    for line in result:
        print(line)
    print()


def flow():

    dbmanager.create_db()
    dbmanager.create_tables()
    employers = dbmanager.get_employers()
    for employer in employers:
        vacancies = dbmanager.get_vacancies(employer.vacancies_url)
        employer_id = dbmanager.insert_values(employer, 'employers')
        for vacancy in vacancies:
            vacancy.employer_id = employer_id
            dbmanager.insert_values(vacancy, 'vacancies')

    msg = 'список всех компаний и количество вакансий у каждой компании ↓'
    print_result(dbmanager.get_companies_and_vacancies_count(), msg)
    msg = 'список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию ↓'
    print_result(dbmanager.get_all_vacancies(), msg)
    msg = 'средняя зарплата по вакансиям ↓'
    print_result(dbmanager.get_avg_salary(), msg)
    msg = 'список всех вакансий, у которых зарплата выше средней по всем вакансиям ↓'
    print_result(dbmanager.get_vacancies_with_higher_salary(), msg)
    input_keyword = input('Введите запрос:')
    msg = 'список всех вакансий, в названии которых содержатся переданные в метод слова ↓'
    print_result(dbmanager.get_vacancies_with_keyword(input_keyword), msg)
