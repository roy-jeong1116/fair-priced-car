import time, random, re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# 각 차량 상세 페이지의 시퀀스 번호 크롤링
def get_sequence_list(driver):
    sequence = []
    page_num = 1
    
    while True:
        url = f'https://www.kbchachacha.com/public/search/main.kbc#!?countryOrder=2&page={page_num}&sort=-orderDate&useCode=002006'
        driver.get(url)
        time.sleep(random.uniform(2, 5))
        items = driver.find_elements(By.CSS_SELECTOR, '.area')
        
        if not items:
            break
        
        for item in items:
            seq = item.get_attribute('data-car-seq')
            if seq is not None:
                sequence.append(seq)
        
        page_num += 1
    
    return sequence

# 차량별 상세 정보 크롤링
def crawl_car_info(driver, sequence):
    data = []

    for seq in sequence:
        temp = []

        try:
            url = f'https://www.kbchachacha.com/public/car/detail.kbc?carSeq={seq}'
            driver.get(url)
            time.sleep(random.uniform(2, 5))
            
            # 지역
            place = driver.find_element(By.CSS_SELECTOR, '.txt-info > span:nth-of-type(4)').text
            # 모델명
            name = driver.find_element(By.CSS_SELECTOR, '.car-buy-name').text.replace('\n', ' ')
            name = re.sub(r"^\([^)]*\)", "", name).strip()
            # 가격
            price = driver.find_element(By.CSS_SELECTOR, '.car-buy-price > div > dl > dd > strong').text
            # 시세안심지수
            relief = driver.find_element(By.CSS_SELECTOR, '.price-tooltip-wrap > strong > strong').text
            # 번호판, 연식, 주행거리, 연료, 변속기, 색상
            info_list = driver.find_elements(By.CSS_SELECTOR, '.detail-info01 > table > tbody > tr > td')
            info = [data.text for data in info_list]
            info = info[:5] + [info[8]]
            # 차량 이미지
            car_image = driver.find_element(By.CSS_SELECTOR, '#bx-pager > .page01 > a:nth-child(1) > img')
            image_url = car_image.get_attribute('src')
            
            temp.append(seq)
            temp.append(name)
            temp.append(place)
            temp.append(price)
            temp.append(relief)
            temp.extend(info)
            temp.append(image_url)
            
            data.append(temp)

        except TimeoutException:
            print(f"TimeoutException 발생 - {seq} 페이지 로드 실패")
            time.sleep(10)

        except StaleElementReferenceException:
            print(f"StaleElementReferenceException 발생 - {seq} 페이지 요소 오류")
            time.sleep(5)

        except Exception as e:
            print(f"알 수 없는 오류 발생 - {seq} : {e}")
    
    return data

# 데이터를 csv 파일로 저장
def save_to_csv(data, filename, columns):
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(filename, encoding='utf-8-sig', index_label='번호')