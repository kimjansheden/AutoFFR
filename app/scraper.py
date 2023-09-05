# Imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException

from bs4 import BeautifulSoup

import gspread
from google.oauth2.service_account import Credentials
from helpers import column_name_to_index, Helper
import os

# Program

class GetPrices:
    def __init__(self, of: enumerate, tickers="all", source="MGEX"):
        self.of=of
        self.tickers = tickers
        self.helper=Helper()    
        
        # Read the configuration file
        self.config = self.helper.config

        self.source: str = self.config['Sources'][source]

        # Set up Selenium webdriver

        # Instantiate ChromeOptions object to customize the behavior of the browser.
        options = Options()

        # Add the '--headless' argument to the options. This disables the browser window opening.
        # In other words, it enables "headless" mode, where the browser runs in the background without a visible window.
        options.add_argument('--headless')

        # Create the Chrome WebDriver instance
        # Try first with Selenium built in function
        try:
            self.driver = webdriver.Chrome(options=options)

        # Use JSON endpoint as fall-back method
        except SessionNotCreatedException as e:
            print(f"An SessionNotCreatedException was raised.\n\nTrying to download the latest version via Google's JSON Endpoint instead.")
            # Get the latest chromedriver
            latest_from_json = self.helper.get_latest_from_json()
            service = Service(latest_from_json)
            self.driver = webdriver.Chrome(options=options, service=service)

    def start(self):
        self.driver.implicitly_wait(3)

        # Load the tickers
        tickers = self.get_tickers(self.tickers)
        price_list = []

        for ticker in tickers:
            try:
                # Navigate to the URL with the current ticker.
                futureDetail = "https://www.mgex.com/quotes.html?j1_module=futureDetail&j1_symbol=" + ticker + "&j1_override=&j1_region="
                self.driver.get(futureDetail)

                # Find the element by XPATH
                element = self.driver.find_element(By.XPATH, "//*[@id=\"futureDetail\"]/div[2]/div[2]/div[1]")
                
                # Delete the "s" at the end and the dollar sign in the beginning. Convert the result to a float.
                found = float(element.text.replace("s", "").replace("$", ""))
                price_list.append(found)

                # Print the extracted text and the type.
                print(ticker, found)
                print(type(found))
            except Exception as e:
                print(f"Error retrieving price for {ticker}. {e}")

        # Print the price list to verify the results.
        print(price_list)

        # Close the webdriver.
        self.driver.quit()

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
        start_row = 4
        end_row = start_row + len(price_list) - 1

        cell_range = Datatabell.range(start_row, column, end_row, column)

        for i in range(len(price_list)):
            cell_range[i].value = price_list[i]

        Datatabell.update_cells(cell_range)
    
    def get_tickers(self, tickers):
        if tickers == "all":
            self.driver.get(self.source)

            page_source = self.driver.page_source

            soup = BeautifulSoup(page_source, "html.parser")
            ticker_tags = soup.select(".table.table-striped tbody tr td.text-left")

            seen = set()  # This set keeps track of tickers we've already added

            tickers = []
            for link in ticker_tags:
                ticker_link = link.find("a")
                if ticker_link:
                    ticker_text = ticker_link.text.strip()
                ticker = ticker_text.split(" ")[0]
                
                # Only add this ticker if we haven't added it before
                if ticker not in seen:
                    tickers.append(ticker)
                    seen.add(ticker)
            
            print(tickers)
            return tickers