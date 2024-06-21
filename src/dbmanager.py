import psycopg2
from src.config import config
from src.hhparser import hh_api
from src.schemas import Employer, Vacancies
from src.constants import EMPLOYER_IDS


class DBmanager:
    """Класс для работы с БД PostgreSQL"""
    def __init__(self, config, api, dbname='hh_info'):
        self.config = config
        self.dbname = dbname
        self.conn = None
        self.api = api
        self.temp_result = []

    def close_connection(self):
        """метод закрытия подключения к БД"""
        if self.conn:
            self.conn.close()

    def get_employers(self):
        """метод получения списка работодателей"""
        employers = self.api.employer_parser(EMPLOYER_IDS)
        return [Employer(**employer) for employer in employers]

    def get_vacancies(self, url):
        """метод получения списка вакансий"""
        vacancies = self.api.vacancies_parser(url)
        return [Vacancies(**vacancy) for vacancy in vacancies]

    def create_db(self):
        """метод создания и подключения к БД"""
        connection = psycopg2.connect(**self.config)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {self.dbname}")
            cursor.execute("CREATE DATABASE hh_info;")
        cursor.close()
        self.close_connection()

    def create_tables(self):
        """метод создания таблиц"""
        self.config['dbname'] = self.dbname
        self.conn = psycopg2.connect(**self.config)
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS employers
                (
                    id SERIAL PRIMARY KEY,
                    employer_name VARCHAR(100) NOT NULL,
                    vacancies_url VARCHAR(255) NOT NULL,
                    open_vacancies INT NOT NULL
                );
                """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS vacancies(
                    id SERIAL PRIMARY KEY,
                    vacancy_name VARCHAR(250) NOT NULL,
                    salary_from FLOAT,
                    salary_to FLOAT,
                    alternate_url VARCHAR(255),
                    employer_id INT,
                    FOREIGN KEY (employer_id) REFERENCES employers (id)
                );
                """)
        self.conn.commit()
        self.close_connection()

    def insert_values(self, value, key):
        """метод внесения данных в таблицы"""
        try:
            self.conn = psycopg2.connect(**self.config)  # !!!!
            if key == 'employers':
                with self.conn.cursor() as cur:
                    insert_employer_query = """
                    INSERT INTO employers (employer_name, vacancies_url, open_vacancies)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                    """
                    cur.execute(insert_employer_query, (
                        value.name,
                        value.vacancies_url,
                        value.open_vacancies
                    ))
                    employer_id = cur.fetchone()[0]
                self.conn.commit()
                self.close_connection()
                return employer_id

            if key == 'vacancies':
                with self.conn.cursor() as cur:
                    insert_vacancies_query = """
                    INSERT INTO vacancies (vacancy_name, salary_from, salary_to, alternate_url, employer_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cur.execute(insert_vacancies_query, (
                        value.name,
                        value.salary.from_ if value.salary else None,
                        value.salary.to if value.salary else None,
                        value.alternate_url,
                        value.employer_id
                    ))
                self.conn.commit()
                self.close_connection()
                return True
            return False
        except Exception as e:
            print(e)
            self.close_connection()

    def get_example(self, *args, **kwargs):
        """вспомогательный метод для работы с запросами"""
        self.conn = psycopg2.connect(**self.config)
        with self.conn.cursor() as cur:
            cur.execute(*args, **kwargs)
            result = cur.fetchall()
        self.close_connection()
        return result

    def get_companies_and_vacancies_count(self):
        """метод получает список всех компаний и количество вакансий у каждой компании."""
        query = 'SELECT employer_name, open_vacancies FROM employers;'
        return self.get_example(query)

    def get_all_vacancies(self):
        """метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию."""
        query = """
            SELECT employer_name, vacancy_name, salary_from, salary_to, alternate_url
            FROM vacancies
            INNER JOIN employers ON vacancies.employer_id=employers.id;
            """
        return self.get_example(query)

    def get_avg_salary(self):
        """метод получает среднюю зарплату по вакансиям."""
        query = """
            SELECT (AVG(salary_from) + AVG(salary_to))/2 AS avg_salary
            FROM vacancies;
            """
        return self.get_example(query)

    def get_vacancies_with_higher_salary(self):
        """метод получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        query = """
            SELECT vacancy_name, salary_from, alternate_url FROM vacancies
            WHERE salary_from > (SELECT AVG(salary_from) FROM vacancies)
            ORDER BY salary_from DESC
            """
        return self.get_example(query)

    def get_vacancies_with_keyword(self, keyword):
        """получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        query = """
            SELECT * FROM vacancies
            WHERE vacancy_name ILIKE %s
            ORDER BY vacancy_name
            """
        return self.get_example(query, ('%' + keyword + '%',))


dbmanager = DBmanager(config, hh_api)
"""Вызов экземпляра класса"""
