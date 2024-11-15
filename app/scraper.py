# Imports
from enum import Enum
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException

from bs4 import BeautifulSoup

import gspread
from gspread.utils import ValueInputOption
from google.oauth2.service_account import Credentials
from helpers import column_name_to_index, Helper
from datetime import datetime
import locale

# Program

class GetPrices:
    def __init__(self, of: Enum, tickers_to_get="all", source="MGEX"):
        self.of=of
        self.tickers_to_get = tickers_to_get
        self.helper=Helper()
        self.page_source = None
        self.source_name = source
        self.price_list = []
        self.tickers_list = []
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.creds_file_path = os.path.join(self.script_dir, "creds.json")
        self.config = self.helper.config
        self.source: str = self.config['Sources'][source]

        # Set up Selenium webdriver

        # Instantiate ChromeOptions object to customize the behavior of the browser.
        options = Options()

        options.add_argument('--headless')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        # Create the Chrome WebDriver instance
        # Try first with Selenium built in function
        try:
            self.driver = webdriver.Chrome(options=options)

        # Use JSON endpoint as fall-back method
        except SessionNotCreatedException as e:
            print(f"An SessionNotCreatedException was raised.\n\nTrying to download the latest version via Google's JSON Endpoint instead.")
            # Get the latest chromedriver
            latest_from_json = self.helper.get_latest_from_json()
            if latest_from_json:
                service = Service(latest_from_json)
            self.driver = webdriver.Chrome(options=options, service=service)
        
        try:
            print(f"Surfing to page {self.source} …")
            self.driver.get(self.source)
            self.page_source = self.driver.page_source
            # print(self.page_source)
        except Exception as e:
            print("Error:", e)

    def start(self):
        self.driver.implicitly_wait(3)

        if self.source_name == "MGEX":
            print(f"Getting prices from {self.source_name}")
            self.get_mgex()
        elif self.source_name == "INVESTING":
            print(f"Getting prices from {self.source_name}")
            self.get_investing()
        else:
            print("No valid source detected. Quitting.")
        
        self.update_gsheets()
    
    def get_tickers(self, tickers_to_get, source="MGEX"):
        if tickers_to_get == "all" and self.page_source:
            soup = BeautifulSoup(self.page_source, "html.parser")
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
        
    def get_mgex(self):
        # Load the tickers
        tickers = self.get_tickers(tickers_to_get=self.tickers_to_get, source=self.source_name)
        if not tickers:
            print("No tickers found. Quitting.")
            return
        for ticker in tickers:
            try:
                # Navigate to the URL with the current ticker.
                futureDetail = "https://www.mgex.com/quotes.html?j1_module=futureDetail&j1_symbol=" + ticker + "&j1_override=&j1_region="
                self.driver.get(futureDetail)

                # Find the element by XPATH
                element = self.driver.find_element(By.XPATH, "//*[@id=\"futureDetail\"]/div[2]/div[2]/div[1]")
                
                # Delete the "s" at the end and the dollar sign in the beginning. Convert the result to a float.
                found = float(element.text.replace("s", "").replace("$", ""))
                self.price_list.append(found)

                # Print the extracted text and the type.
                print(ticker, found)
                print(type(found))
            except Exception as e:
                print(f"Error retrieving price for {ticker}. {e}")

        # Print the price list to verify the results.
        print(self.price_list)

        # Close the webdriver.
        self.driver.quit()

    def get_investing(self):
        if not self.page_source:
            print("No page source found. Quitting.")
            return
        
        try:
            # Wait a few seconds and then click on the Accept buttin with button id="onetrust-accept-btn-handler"
            print("Waiting for Accept button")
            accept_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept_button.click()

            # Update page_source after we got rid of the cookies dialogue
            self.page_source = self.driver.page_source
        except TimeoutException as e:
            print("No Accept button found. Continuing.")

        soup = BeautifulSoup(self.page_source, "html.parser")
        # print(soup)

        # Find the table with the id 'BarchartDataTable'
        table = soup.find('table', {'id': 'BarchartDataTable'})

        if not table:
            print("No table found. Quitting.")
            return

        # Extract all the rows within the table
        rows = table.find_all('tr')

        # Loop through each row to find and extract data
        for row in rows:
            # Find all cells in each row
            cells = row.find_all('td')

            if len(cells) > 2:  # Make sure the row has enough cells
                month = cells[1].text.strip()  # The month is in the second cell
                price = cells[2].text.strip()  # The price is in the third cell

                price = price.replace("s", "").replace(".", ",")

                print(month, price)
                self.price_list.append(price)
                self.tickers_list.append(month)

        # Close the webdriver.
        self.driver.quit()
    
    def update_gsheets(self):
        # Authenticate with Google Sheets.
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

        creds_file = Credentials.from_service_account_file(self.creds_file_path, scopes=scopes)
        client = gspread.authorize(creds_file)

        # Get the worksheet ID from the configuration file
        worksheet_id = int(self.config['Google']['worksheet_id'])

        # Open the sheet and get the first worksheet
        ss = client.open('Placeringar')
        Datatabell = ss.get_worksheet_by_id(worksheet_id)

        column_month_letter = 'P'

        # Write the extracted prices to the sheet, starting from cell S22.
        column_date = column_name_to_index('O')
        column_price = column_name_to_index('S')
        column_month = column_name_to_index(column_month_letter)
        
        start_row = 4
        end_row = start_row + len(self.price_list) - 1

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cell_range_prices = Datatabell.range(start_row, column_price, end_row, column_price)
        cell_range_months = Datatabell.range(start_row, column_month, end_row, column_month)
        cell_range_dates = Datatabell.range(start_row, column_date, end_row, column_date)

        # Mapping from English month abbreviations to Swedish month names
        month_mapping = {
        "Jan": "januari", "Feb": "februari", "Mar": "mars",
        "Apr": "april", "May": "maj", "Jun": "juni",
        "Jul": "juli", "Aug": "augusti", "Sep": "september",
        "Oct": "oktober", "Nov": "november", "Dec": "december"
        }

        # Mapping from month abbreviations to full English month names
        month_abbr_to_full = {
            "Jan": "January", "Feb": "February", "Mar": "March",
            "Apr": "April", "May": "May", "Jun": "June",
            "Jul": "July", "Aug": "August", "Sep": "September",
            "Oct": "October", "Nov": "November", "Dec": "December"
        }

        for i in range(len(self.price_list)):
            cell_range_prices[i].value = self.price_list[i]
            cell_range_dates[i].value = current_datetime
            
            ticker = self.tickers_list[i]
            if ticker[0].isalpha():  # Check if the string starts with a letter
                month_abbr, year_suffix = ticker.split('\xa0')
                year = "20" + year_suffix  # Convert to full year

                # # Get Swedish month name from the mapping
                # month_name = month_mapping.get(month_abbr, "")

                # Convert month abbreviation to full name
                month_full = month_abbr_to_full.get(month_abbr, "")
                
                formatted_date = datetime.strptime(f"1 {month_full} {year}", "%d %B %Y").strftime("%Y-%m-%d")
                
                cell_range_months[i].value = formatted_date
            else:
                cell_range_months[i].value = ticker

        Datatabell.update_cells(cell_range_prices)
        Datatabell.update_cells(cell_range_months, ValueInputOption.user_entered)
        Datatabell.update_cells(cell_range_dates, ValueInputOption.user_entered)

        Datatabell.format(f"{column_month_letter}4:{column_month_letter}{end_row}", {"numberFormat": {"type": "DATE", "pattern": "mmmm yyyy"}})