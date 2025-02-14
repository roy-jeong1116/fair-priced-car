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

if __name__ == "__main__":
    main()