from selenium import webdriver
import time
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import threading

get_clicked_element_info_script = """
var blackBar = document.createElement('div');
blackBar.style.position = 'fixed';
blackBar.style.top = '0';
blackBar.style.left = '0';
blackBar.style.width = '100%';
blackBar.style.height = '30px';
blackBar.style.backgroundColor = 'black';
blackBar.style.color = 'white';
blackBar.style.padding = '5px';
blackBar.style.boxSizing = 'border-box';
blackBar.style.zIndex = '9999';
blackBar.innerText = 'Element XPath: ';
document.body.appendChild(blackBar);

document.addEventListener('mousedown', function (event) {
var clickedElement = event.target;

var xpath = getXPath(clickedElement);

console.log('Clicked Element XPath:', xpath);
return xpath;
});
document.addEventListener('mouseover', function (event) {
    var clickedElement = event.target;

    var xpath = getXPath(clickedElement);
    
    blackBar.innerText = 'Current Element XPath: ' + xpath;
    return xpath;
});

function getXPath(element) {
    if (element.id !== '')
        return 'id("' + element.id + '")';
    if (element === document.body)
        return element.tagName;

    var siblings = element.parentNode.childNodes;
    for (var i = 0; i < siblings.length; i++) {
        var sibling = siblings[i];
        if (sibling === element)
            return getXPath(element.parentNode) + '/' + element.tagName + '[' + (i + 1) + ']';
    }
}
"""

b = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

class EventListeners(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        print("before_navigate_to %s" % url)

    def after_navigate_to(self, url, driver):
        print("after_navigate_to %s" % url)

    def after_navigate_forward(self, driver):
        print("after_navigate_forward");

    def before_navigate_forward(self, driver):
        print("before_navigate_forward")

    def after_navigate_back(self, driver):
        print("after_navigate_back")

    def before_navigate_back(self, driver):
        print("before_navigate_back")


class MouseThread(threading.Thread):
    def run(self):
        def on_click(x, y, button, pressed):
            if pressed:
                print("Navigation to: %s" % d.current_url)
                xpath = b.execute_script(get_clicked_element_info_script)
                print(xpath)
                
            
        with MouseListener(on_click=on_click) as mouse_listener:
            mouse_listener.join()

class KeyboardThread(threading.Thread):
    def run(self):
        def on_key_press(key):
            try:
                print(f"Key pressed: {key.char}")
            except AttributeError:
                print(f"Special key pressed: {key}")
                print("Navigation to: %s" % d.current_url)

        with KeyboardListener(on_press=on_key_press) as keyboard_listener:
            keyboard_listener.join()
            

d = EventFiringWebDriver(b,EventListeners())
mouse_thead=MouseThread()
keyboard_thead=KeyboardThread()

mouse_thead.start()
keyboard_thead.start()
d.get('https://www.google.co.kr')
d.implicitly_wait(20)
mouse_thead.join()
keyboard_thead.join()

d.quit()