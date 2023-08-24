# Imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import gspread
from google.oauth2.service_account import Credentials
from helpers import column_name_to_index, Helper
import os

# Program

class GetPrices:
    def __init__(self, of: enumerate, tickers="", source="mgex"):
        self.of=of
        self.source=source
        self.helper=Helper()    # In case I need a helper for each instance. Otherwise, delete this in the
                                #future.
        # Read the configuration file
        self.config = self.helper.config
        
        # If value is passed in the repopulate_from variable, initialize the instance with data from the previous
        # instance. The previous instance is thus recreated.
        if tickers != "":
            self.repopulate(tickers)

    def start(self):
        # Set up Selenium webdriver

        # Instantiate ChromeOptions object to customize the behavior of the browser.
        options = Options()

        # Get the latest chromedriver
        latest_from_json = self.helper.get_latest_from_json()
        service = Service(latest_from_json)

        # Add the '--headless' argument to the options. This disables the browser window opening.
        # In other words, it enables "headless" mode, where the browser runs in the background without a visible window.
        options.add_argument('--headless')

        # Create the Chrome WebDriver instance
        driver = webdriver.Chrome(options=options, service=service)

        driver.implicitly_wait(3)

        # Load the tickers
        # Det ska vara såhär när det är klart:
        # Hämta alla tickers från https://www.mgex.com/data_charts.html?j1_module=futureMarketOverview&j1_root=ZQ&j1_section=financials&
        # och ladda in dem i listan. Låt användaren vilja vilka som ska vara kvar.
        tickers = {ticker: ticker for ticker in ["ZQV24" ,"ZQX24" ,"ZQZ24" ,"ZQF25" ,"ZQG25", "ZQH25", "ZQJ25", "ZQK25", "ZQM25", "ZQN25", "ZQQ25", "ZQU25", "ZQV25", "ZQX25", "ZQZ25"]}
        price_list = []

        for ticker in tickers.values():
            try:
                # Navigate to the URL with the current ticker.
                futureDetail = "https://www.mgex.com/quotes.html?j1_module=futureDetail&j1_symbol=" + ticker + "&j1_override=&j1_region="
                driver.get(futureDetail)

                # Find the element by XPATH
                element = driver.find_element(By.XPATH, "//*[@id=\"futureDetail\"]/div[2]/div[2]/div[1]")
                
                # Delete the "s" at the end and the dollar sign in the beginning. Convert the result to a float.
                found = float(element.text.replace("s", "").replace("$", ""))
                price_list.append(found)

                # Print the extracted text and the type.
                print(ticker, found)
                print(type(found))
            except:
                print(f"Error retrieving price for {ticker}")

        # Print the price list to verify the results.
        print(price_list)

        # Close the webdriver.
        driver.quit()

        # Authenticate with Google Sheets.
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

        creds_file = Credentials.from_service_account_file('./creds.json', scopes=scopes)
        client = gspread.authorize(creds_file)

        # Get the worksheet ID from the configuration file
        worksheet_id = int(self.config['Google']['worksheet_id'])

        # Open the sheet and get the first worksheet
        ss = client.open('Placeringar')
        Datatabell = ss.get_worksheet_by_id(worksheet_id)

        # Write the extracted prices to the sheet, starting from cell S22.
        column = column_name_to_index('S')
        #column = "S"
        start_row = 19
        end_row = start_row + len(price_list) - 1

        cell_range = Datatabell.range(start_row, column, end_row, column)

        for i in range(len(price_list)):
            cell_range[i].value = price_list[i]

        Datatabell.update_cells(cell_range)