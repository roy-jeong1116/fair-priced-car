import time, random, re, pymysql, csv
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

# MySQL 연결
def connect_to_db():
    return pymysql.connect(
        host='localhost',  # 데이터베이스 서버 주소
        user='root',  # 사용자명
        password='royjeong1116',  # 비밀번호
        database='UsedCarDB'  # 사용할 데이터베이스 이름
    )

# 테이블 생성 함수
def create_table_if_not_exists():
    connection = connect_to_db()
    cursor = connection.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS Cars (
        id INT AUTO_INCREMENT PRIMARY KEY,
        car_model VARCHAR(255),
        location VARCHAR(255),
        price VARCHAR(50),
        price_condition VARCHAR(50),
        car_number VARCHAR(50),
        model_year VARCHAR(20),
        mileage VARCHAR(50),
        fuel_type VARCHAR(50),
        transmission VARCHAR(50),
        color VARCHAR(50),
        image_url TEXT
    );
    """
    
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    connection.close()

# CSV 데이터를 MySQL 테이블에 삽입하는 함수
def insert_csv_to_db():
    connection = connect_to_db()
    cursor = connection.cursor()

    # CSV 파일 열기
    with open('./car_data.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # 첫 번째 행은 헤더이므로 건너뛰기

        for row in csv_reader:
            car_model = row[2]
            location = row[3]
            price = row[4]
            price_condition = row[5]
            car_number = row[6]
            model_year = row[7]
            mileage = row[8]
            fuel_type = row[9]
            transmission = row[10]
            color = row[11]
            image_url = row[12]

            insert_query = """
            INSERT INTO cars (car_model, location, price, price_condition, car_number, 
                              model_year, mileage, fuel_type, transmission, color, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            cursor.execute(insert_query, (car_model, location, price, price_condition, car_number, 
                                          model_year, mileage, fuel_type, transmission, color, image_url))

    connection.commit()
    cursor.close()
    connection.close()