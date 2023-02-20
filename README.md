# AutoFFR
AutoFFR is a Python script that extracts Fed futures prices from a site of the user's choice, currently the Minneapolis Grain Exchange (MGEX) website, saves them to a Google Sheet, and optionally sets up a launch agent on a macOS system to run the script automatically at specified intervals.

## Dependencies
AutoFFR requires Python 3 and the following packages:

Selenium
gspread
google-auth
google-auth-oauthlib
google-auth-httplib2

The script also uses the chromedriver binary for web scraping. The version of chromedriver must match the version of the Google Chrome web browser installed on the system.

## How To Install
To install AutoFFR, perform the following steps:

1. You need to create a Google Cloud Account, Enable Google Sheets & Google Drive APIs and generate a key with your credentials and save it to creds.json and place it as the same folder as the app.
1. Then you need to give permission to the email address of your Cloud Account (it's in the credentials file).
1. Clone the repository from GitHub.
1. Install the required Python packages using pip: pip install -r requirements.txt.
1. Download the chromedriver binary and place it in the root directory of the project.
1. Fill in the necessary configuration options in the config file.

## Usage
To run the script, execute getprices_script.py:
`python getprices_script.py`

To modify the list of futures, edit the tickers dictionary in scraper.py. In the future the script is going to collect all available futures and let the user choose which ones to get.

## Options
The script accepts the following command line options:

- `--of`: The futures contract to extract prices for.
- `--source`: The source of the prices.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions to this project are welcome. Please see the CONTRIBUTING.md file for guidelines.