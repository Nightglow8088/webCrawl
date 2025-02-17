import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


# send request by requests.Session then get the cookie, and used the header founded in network to send get request
def fetch_parcel_data(ain):

    session = requests.Session()
    # header info found in network page
    common_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    # GET /api/parceldetail?ain=2004013020 HTTP/1.1
    # Accept: application/json, text/plain, */*
    # Accept-Encoding: gzip, deflate, br, zstd
    # Accept-Language: en,zh-CN;q=0.9,zh;q=0.8
    # Connection: keep-alive
    # Host: portal.assessor.lacounty.gov
    # Origin: https://assessor.lacounty.gov
    # Referer: https://assessor.lacounty.gov/
    # Sec-Fetch-Dest: empty
    # Sec-Fetch-Mode: cors
    # Sec-Fetch-Site: same-site
    # User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36
    # sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"
    # sec-ch-ua-mobile: ?0
    # sec-ch-ua-platform: "Windows"

    # 1) visit web to get the Cookie and check the status code works or not
    home_url = "https://assessor.lacounty.gov/"
    home_headers = dict(common_headers)
    resp_home = session.get(home_url, headers=home_headers)
    print("common status code:", resp_home.status_code)

    # 2) visit API
    api_url = f"https://portal.assessor.lacounty.gov/api/parceldetail?ain={ain}"
    api_headers = dict(common_headers)
    api_headers["Host"] = "portal.assessor.lacounty.gov"
    api_headers["Referer"] = "https://assessor.lacounty.gov/"
    api_headers["Origin"] = "https://assessor.lacounty.gov"
    response = session.get(api_url, headers=api_headers)

    try:
        data = response.json()
        print("Json: ", data)
    except Exception as e:
        print("failed be parse as JSON:")
        print(response.text)
        data = None

    return data


def assessor_ID_finder():
    # Open the page by Selenium and extract 1st Assessor(6th col), and remove all "-" chars

    driver = webdriver.Chrome() 
    assessor_id = None
    try:
        data_url = "https://data.lacounty.gov/datasets/lacounty::assessor-parcel-data-rolls-2021-present/explore"
        driver.get(data_url)
        # assume the page will be rendered in 10s
        time.sleep(10)  
        first_row = driver.find_element(By.CSS_SELECTOR, "table tbody tr")
        cells = first_row.find_elements(By.TAG_NAME, "td")
        assessor_id = cells[5].text.strip().replace("-", "")
        print("ssessor ID:", assessor_id)
    except Exception as e:
        print("Error: ", e)
    finally:
        driver.quit()
    return assessor_id


def flatten_json(y, parent_key='', sep='_'):
    items = {}
    if isinstance(y, dict):
        for k, v in y.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_json(v, new_key, sep=sep))
    elif isinstance(y, list):
        if not y:
            items[parent_key] = ""
        else:
            for idx, item in enumerate(y):
                new_key = f"{parent_key}{sep}{idx}"
                items.update(flatten_json(item, new_key, sep=sep))
    else:
        items[parent_key] = y
    return items



# save the result in output.txt file with (key-val) pair
def save_data_to_txt(data, filename="output.txt"):
    flat_data = flatten_json(data)
    try:
        with open(filename, "w", encoding="utf-8") as txtfile:
            for key, value in flat_data.items():
                txtfile.write(f"{key}: {value}\n")
        print(f"Done in file: {filename}")
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    # get assessor_ID and use it to search in LA property search
    assessor_ID = assessor_ID_finder()
    parcel_data = fetch_parcel_data(assessor_ID)
    if parcel_data:
        save_data_to_txt(parcel_data, "output.txt")
    else:
        print("Not found")
