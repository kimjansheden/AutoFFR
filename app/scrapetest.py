from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import gspread
from google.oauth2.service_account import Credentials

# Disable the browser window opening, i.e. enable headless mode
options = webdriver.ChromeOptions()
options.add_argument('--headless')

# Set up Selenium webdriver
driver_path = "./chromedriver"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(3)

try:
    # Navigate to the website
    driver.get("https://www.mgex.com/quotes.html?j1_module=futureDetail&j1_symbol=ZQH25&j1_override=&j1_region=")

    # Find the element by XPATH
    element = driver.find_element(By.XPATH, "//*[@id=\"futureDetail\"]/div[2]/div[2]/div[1]")
    
    # Delete the "s" at the end and the dollar sign in the beginning. Convert the result to a float.
    text = float(element.text.replace("s", "").replace("$", ""))

    # Print the extracted text and the type.
    print(text)
    print(type(text))
finally:
    # Close the driver
    driver.quit()

# Authenticate with Google Sheets
creds_file = Credentials.from_service_account_file('./creds.json')
client = gspread.authorize(creds_file)

# Open the sheet and get the first worksheet
ss = client.open('Placeringar')
Datatabell = ss.get_worksheet_by_id(338938079)

# Write the extracted text to cell A1
Datatabell.update_cell(27, 19, text)