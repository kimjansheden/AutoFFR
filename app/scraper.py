# Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import gspread
from google.oauth2.service_account import Credentials
from helpers import column_name_to_index, Helper

# Program

class GetPrices:
    def __init__(self, of: enumerate, tickers="", source="mgex"):
        self.of=of
        self.source=source
        self.helper=Helper()    # In case I need a helper for each instance. Otherwise, delete this in the
                                #future.
        
        # If value is passed in the repopulate_from variable, initialize the instance with data from the previous
        # instance. The previous instance is thus recreated.
        if tickers != "":
            self.repopulate(tickers)

    def start(self):
        # Disable the browser window opening, i.e. enable headless mode
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')

        # Set up Selenium webdriver
        driver_path = "./chromedriver"
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)

        # Load the tickers
        # Det ska vara såhär när det är klart:
        # Hämta alla tickers från https://www.mgex.com/data_charts.html?j1_module=futureMarketOverview&j1_root=ZQ&j1_section=financials&
        # och ladda in dem i listan. Låt användaren vilja vilka som ska vara kvar.
        tickers = {"ZQH25":"ZQH25"}

        try:
            # Navigate to the website
            # Jag behöver loopa igenom listan med tickers och för varje ticker ska jag hämta priset och spara priserna i en prislista som jag sedan skriver ut i min range i sheeten.
            futureDetail = "https://www.mgex.com/quotes.html?j1_module=futureDetail&j1_symbol=" + tickers["ZQH25"] + "&j1_override=&j1_region="
            driver.get(futureDetail)

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
        creds_file = Credentials.from_service_account_file('./creds.json', scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        print(creds_file.has_scopes("https://www.googleapis.com/auth/spreadsheets"))
        client = gspread.authorize(creds_file)

        # Open the sheet and get the first worksheet
        ss = client.open('Placeringar')
        Datatabell = ss.get_worksheet_by_id(338938079)

        # Write the extracted text to cell S27
        column = column_name_to_index('S')
        row = 27
        Datatabell.update_cell(row, column, text)