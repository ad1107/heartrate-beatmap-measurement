# Only the web scraping stuff.

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Setup Selenium stuff
options = Options()
options.add_argument("--headless")  # No GUI
driver = webdriver.Chrome(options=options)

code = input("Enter your HypeRate code: ")
if code.strip() == "" or len(code) != 4:
    print("Invalid code.")
    exit()

url = "https://app.hyperate.io/" + code.upper()

print("Scraping using the link: " + url)


# Scraping
def scrape_heart_rate():
    try:
        driver.get(url)
        time.sleep(5)  # Wait for the JavaScript to update

        # Extraction
        heart_rate_element = driver.find_element(By.CLASS_NAME, "heartrate")
        heart_rate = heart_rate_element.text.strip()

        return heart_rate

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Trying to do the accuracy
# (if it actually show the heart rate, or just spits out "0".)


valid = 0
zero = 0
none = 0
# Scraping forever until interrupt
while True:
    heart_rate_value = scrape_heart_rate()

    if heart_rate_value is not None:
        print(f"Heart Rate: {heart_rate_value}")

    # Testing reliability
    if heart_rate_value == "0":
        zero += 1
    else:
        valid += 1
    print("attempt:", valid + zero)
    print(
        "zero:", zero, "\nvalid:", valid, "\nratio (%): ", zero / (valid + zero) * 100
    )

driver.quit()
