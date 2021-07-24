import os
import requests
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup as BS
import time

load_dotenv("../.env")

HEADER = {
    "User-Agent": "91.0.4472.124 (Official Build) (64-bit) (cohort: Stable)"
}

MAIN_URL = "https://hh.ru"
SUB_URL = "/search/vacancy"
#URL = "https://www.superjob.ru/"
INPUT = "Внутренний аудитор"
PARAMS = {
    "area": 1,
    "fromSearchLine": "true",
    "st": "searchVacancy",
    "from": "suggest_post",
    "text": "analytic",
    "page": 1
}


def get_html(url, header=None, params=None):
    response = requests.get(url, headers=header, params=params)
    print(response.url)
    if response.status_code != 200:
        print(f'Status code is {response.status_code}, aborting...')
        raise Exception
    return response.text


def get_dom(html):
    return BS(html, "html.parser")


def get_page_next(html, header):
    """ Get html from hh web-site and return either next page or None """
    soup = get_dom(html)
    next_page_el = soup.find(attrs={
        "class": "bloko-button",
        "data-qa": "pager-next"
    })
    if next_page_el is None:
        print("End of pages")
        return None
    return get_html(MAIN_URL+next_page_el["href"], header)


def get_info_from_page(html):
    soup = get_dom(html)
    items = soup.findAll(attrs={"class": "vacancy-serp-item"})
    res = []
    item = {}
    for n in items:
        item["name"] = n.find(attrs={"class": "resume-search-item__name"}).text
        item.update(get_salary_from_item(
            n.find(attrs={"class": "vacancy-serp-item__sidebar"}).find('span')
        ))
        item["ref"] = n.find(attrs={"data-qa": "vacancy-serp__vacancy-title"})["href"]
        item["source"] = MAIN_URL

        res.append(item)
        item = {}
    return res



def get_salary_from_item(hh_span):
    salary={
        "min_sal": "Not stated",
        "max_sal": "Not stated"
    }
    if hh_span is None:
        return salary

    text = hh_span.text
    if text[0:2] == "от":
        salary["min_sal"] = get_only_nums(text)

    elif text[0:2] == "до":
        salary["min_sal"] = get_only_nums(text)

    else:
        text = text.replace("\u202f","")
        salary["min_sal"] = get_only_nums(text[:text.find(" – ")])
        salary["max_sal"] = get_only_nums(text[text.find(" – ") + 3:])

    return salary

def get_info_from_hh(url, header, input = "Аналитик"):
    params = {
        "area": 1,
        "fromSearchLine": "true",
        "st": "searchVacancy",
        "from": "suggest_post",
        "text": input,
        "page": 1
    }

    out = []
    page = get_html(url,header, params)
    while page is not None:
        time.sleep(1)
        out += get_info_from_page(page)
        page = get_page_next(page, header)
    return out

#-------------- Utils -----------------------

def get_only_nums(string):
    out = ""
    for n in string:
        if n.isdigit():
            out += n
    return int(out)

if __name__ == "__main__":
    input = "Внутренний аудитор"
    hh_res = get_info_from_hh(MAIN_URL+SUB_URL, HEADER, input)

