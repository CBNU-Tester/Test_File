from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pynput.mouse import Listener
import time

class EventListeners(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        print(f"before_navigate_to {url}")

    def after_navigate_to(self, url, driver):
        print(f"after_navigate_to {url}")

    def before_click(self, element, driver):
        print(f"before_click {element}")

    def after_click(self, element, driver):
        print(f"after_click {element}")

    def after_navigate_forward(self, driver):
        print("after_navigate_forward")

    def before_navigate_forward(self, driver):
        print("before_navigate_forward")

    def after_navigate_back(self, driver):
        print("after_navigate_back")

    def before_navigate_back(self, driver):
        print("before_navigate_back")

    def before_change_value_of(self, element, driver):
        print("before_change_value_of")

# ChromeDriver 초기화
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-infobars')
b = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# EventListeners 적용
event_listener = EventListeners()
b = EventFiringWebDriver(b, event_listener)

# 마우스 이벤트 감지
def on_click(x, y, button, pressed):
    if pressed:
        print('Mouse clicked')
        time.sleep(2)
        print("Navigation to: %s" % b.current_url)

with Listener(on_click=on_click) as listener:
    while True:
        pass
