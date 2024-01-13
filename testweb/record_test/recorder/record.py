from selenium import webdriver
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import threading
import record_js

get_clicked_element_info_script = record_js.get_xpath()

class EventListeners(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        print("before_navigate_to %s" % url)

    def after_navigate_to(self, url, driver):
        print("after_navigate_to %s" % url)

    def after_navigate_forward(self, driver):
        print("after_navigate_forward")

    def before_navigate_forward(self, driver):
        print("before_navigate_forward")

    def after_navigate_back(self, driver):
        print("after_navigate_back")

    def before_navigate_back(self, driver):
        print("before_navigate_back")


class MouseThread(threading.Thread):
    def __init__(self, driver, script):
        super().__init__()
        self.driver = driver
        self.script = script

    def run(self):
        def on_click(x, y, button, pressed):
            if pressed:
                print("Navigation to: %s" % self.driver.current_url)
                xpath = self.driver.execute_script(self.script)

        with MouseListener(on_click=on_click) as mouse_listener:
            mouse_listener.join()

class KeyboardThread(threading.Thread):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver

    def run(self):
        def on_key_press(key):
            try:
                print(f"Key pressed: {key.char}")
            except AttributeError:
                print(f"Special key pressed: {key}")
                print("Navigation to: %s" % self.driver.current_url)

        with KeyboardListener(on_press=on_key_press) as keyboard_listener:
            keyboard_listener.join()

def selenium_start():
    b = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    d = EventFiringWebDriver(b, EventListeners())
    mouse_thread = MouseThread(d, get_clicked_element_info_script)
    keyboard_thread = KeyboardThread(d)

    mouse_thread.start()
    keyboard_thread.start()
    d.get('https://www.google.co.kr')
    d.implicitly_wait(20)
    mouse_thread.join()
    keyboard_thread.join()

    d.quit()


