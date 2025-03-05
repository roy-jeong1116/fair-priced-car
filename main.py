from utils import *

def main():
    driver = webdriver.Chrome()
    
    try:
        sequence = get_sequence_list(driver)
        save_to_csv(sequence, 'seq_data.csv', ['시퀀스'])
        
        car_data = crawl_car_info(driver, sequence)
        columns = ['시퀀스', '모델명', '지역', '가격', '시세안심지수', '번호판', '연식', '주행거리', '연료', '변속기', '색상', '사진']
        save_to_csv(car_data, 'car_data.csv', columns)
        
    finally:
        driver.quit()

    create_table_if_not_exists()  # 테이블이 없으면 생성
    insert_csv_to_db()  # CSV 파일 데이터를 DB에 저장

if __name__ == "__main__":
    main()