import time
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"

def launch_chrome(port=9222):
    subprocess.Popen(
        [
            CHROME_PATH,
            f"--remote-debugging-port={port}",
            "--user-data-dir=C:/selenium/chrome-profile"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        shell=True
    )
    print("[+] Chrome Launched Automatically")
    time.sleep(1.5)  # Wait for Chrome to launch fully

def attach_to_chrome():
    chrome_options = Options()
    chrome_options.debugger_address = "localhost:9222"

    driver = webdriver.Chrome(options=chrome_options)
    print("[+] Attached to Existing Chrome Session")
    return driver


def chrome_alive(port=9222):
    try:
        response = requests.get(f"http://localhost:{port}/json")
        return response.status_code == 200
    except:
        return False
    
def start(url="https://www.google.com"):
    launch_chrome()
    driver = attach_to_chrome()
    driver.get(url)
    driver.maximize_window()

# launch_chrome()
# driver = attach_to_chrome()
# driver.get("https://youtube.com")
# driver.maximize_window()
# while(True): # prevent Chrome from automatically closing
#     if not chrome_alive():
#         break
#     pass