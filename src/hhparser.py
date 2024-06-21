import requests
from src.constants import HH_URL
from typing import Any


class HhParser():
    """Класс для осуществления подключения к API службе внешнего источника данных согласно заданных параметров"""

    def __init__(self):
        self.url_emp = HH_URL
        self.params = {
            'text': '',
            'page': 0,
            'per_page': 100}

    @staticmethod
    def __api_request(url):
        response = requests.get(url)
        return response.json()

    def employer_parser(self, employer_ids: list) -> list[dict[str, Any]]:
        result = []
        for employer_id in employer_ids:
            url = f'{self.url_emp}{employer_id}'
            result.append(self.__api_request(url))
        return result

    def vacancies_parser(self, url):
        return self.__api_request(url)['items']


hh_api = HhParser()
