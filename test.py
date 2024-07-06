# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# import time

# # 브라우저 꺼짐 방지 옵션 설정
# chrome_options = Options()
# chrome_options.add_experimental_option("detach", True)

# # Chrome 웹 드라이버 초기화
# driver = webdriver.Chrome(options=chrome_options)

# #홈페이지로 이동
# url = 'https://www.historyexam.go.kr/mypage/exam/examAreaListPopup.do?netfunnel_key=7A26481B35E07F18162B0ECBF98E4FB2D0107F38E3209FB9F6F8EB69B91729EF2C918DAB9C0D0767AD84033AD75CBE8616DFE34241063750088460AFAA19C7D76BC326631A0D65E24EA3BAC1034BDD2E50065359E3BB58BA1683B652D53F0FEF1F0EEC2239FD024581E21E8C4DC950B22C37342C30&pageIndex=1&testlevel=1&dspsn=N&lo_code=11&exam_area_code=71'
# driver.get(url)

# #해당 xpath 클릭
# //*[@id="searchVO"]/table/tbody/tr/td[4]/a/img

# #해당 xpath 클릭
# /html/body/div/div[2]/div[3]/table/tbody/tr[3]/td[4]/img

# 해당 활동 무한 반복 

import pymysql

try:
    # 데이터베이스 접속
    conn = pymysql.connect(host='10.198.137.118', port=4567, user='root', password='1234', db='Graduate', charset='utf8')
    
    # 커서 생성
    cursor = conn.cursor()
    
    # 데이터베이스 버전 확인 쿼리 실행
    cursor.execute("SELECT VERSION()")
    
    # 쿼리 결과 가져오기
    version = cursor.fetchone()
    
    # 결과 출력
    print("Database version:", version[0])
    
except pymysql.Error as e:
    print("Error connecting to MySQL database", e)
    
finally:
    # 데이터베이스 접속 종료
    if conn:
        conn.close()