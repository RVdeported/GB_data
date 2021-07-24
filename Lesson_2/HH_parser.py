import os
import requests
import pandas as pd
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup as BS
import time

load_dotenv("../.env")

HEADER = {
    "User-Agent": "91.0.4472.124 (Official Build) (64-bit) (cohort: Stable)"
}

MAIN_URL_HH = "https://hh.ru"
SUB_URL_HH = "/search/vacancy"
MAIN_URL_SJ = "https://www.superjob.ru/"
SUB_URL_SJ = "/vacancy/search"

#------------- Universal http tools----------------

def get_html(url, header=None, params=None):
    response = requests.get(url, headers=header, params=params)
    if response.status_code != 200:
        print(f'Status code is {response.status_code}, aborting...')
        raise Exception
    return response.text


def get_dom(html):
    return BS(html, "html.parser")

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

    elif text.find("–") != -1:
        #text = text.replace("\u202f","")
        salary["min_sal"] = get_only_nums(text[:text.find(" – ")])
        salary["max_sal"] = get_only_nums(text[text.find(" – ") + 3:])
    
    elif text.find("—") != -1:
       #text = text.replace("\u202f","")
        salary["min_sal"] = get_only_nums(text[:text.find("—")])
        salary["max_sal"] = get_only_nums(text[text.find("—") + 1:])  

    return salary

def get_info_from(main_url, sub_url, header, 
                     func_get_info, func_get_next_page, func_params,
                     source, input = "Аналитик"):
    url = main_url+sub_url
    params = func_params(input)

    out = []
    page = get_html(url,header, params)
    while page is not None:
        time.sleep(1)
        out += func_get_info(page, source)
        page = func_get_next_page(page, header, main_url)
        print("Next_page... " + str(len(out)))
    return out
        
    return page

def get_info_from_hh_sj(input):
    res = get_info_from(MAIN_URL_HH, SUB_URL_HH, HEADER,
                              get_info_from_page_hh, get_page_next_hh,generate_params_hh,
                              "https://hh.ru", input)
    res += get_info_from(MAIN_URL_SJ, SUB_URL_SJ, HEADER, 
                           get_info_from_page_sj, get_page_next_sj, generate_params_sj,
                           "https://www.superjob.ru/" ,input)
    
    with open(".\jobs.json", "w") as f:
        json.dump(res, f)

#----------------------- Site funcs ---------------------------

def get_info_from_page_hh(html, source):
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
        item["source"] = source

        res.append(item)
        item = {}
    return res

def get_page_next_hh(html, header, main_url):
    """ Get html from hh web-site and return either next page or None """
    soup = get_dom(html)
    next_page_el = soup.find(attrs={
        "class": "bloko-button",
        "data-qa": "pager-next"
    })
    if next_page_el is None:
        print("End of pages")
        return None
    return get_html(main_url+next_page_el["href"], header)

def get_info_from_page_sj(html, source):
    soup = get_dom(html)
    items = soup.findAll(attrs={"class": "_31XDP iJCa5 f-test-vacancy-item _1fma_ _2nteL"})
    res = []
    item = {}
    for n in items:
        item["name"] = n.find(attrs={"class": "_1h3Zg _2rfUm _2hCDz _21a7u"}).findChildren("a")[0].text

        item.update(get_salary_from_item(
            n.find('span', attrs={"class": "_1h3Zg _2Wp8I _2rfUm _2hCDz _2ZsgW"})
        ))

        item["ref"] = source + n.find("a")["href"]
        item["source"] = source

        res.append(item)
        item = {}

    return res

def get_page_next_sj(html, header, main_url):
    """ Get html from hh web-site and return either next page or None """
    soup = get_dom(html)
    next_page_el = soup.find(attrs={
        "class": "icMQ_ bs_sM _3ze9n f-test-button-dalshe f-test-link-Dalshe",
    })
    if next_page_el is None:
        print("End of pages")
        return None
    return get_html(main_url+next_page_el["href"], header)

def generate_params_hh(input):
    return {
        "area": 1,
        "fromSearchLine": "true",
        "st": "searchVacancy",
        "from": "suggest_post",
        "text": input,
        "page": 1
    }

def generate_params_sj(input):
    return {
        "keywords": input,
        "page": 1
    }
    
#-------------- Other Utils -----------------------

def get_only_nums(string): # there is more efficient way
    out = ""
    for n in string:
        if n.isdigit():
            out += n
    if len(out) == 0:
        return "Not stated"
    return int(out)

if __name__ == "__main__":
    print("Print keywords forsearch:")
    get_info_from_hh_sj(input())
    data = pd.read_json(".\jobs.json")
    

    
    
    