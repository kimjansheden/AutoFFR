import configparser
import os
import re
import shutil
import stat
import subprocess
import sys
import zipfile
import requests
import os
import subprocess


class Helper:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file_path = os.path.join(self.script_dir, "config.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)

    def setup_launch_agent(self):
        # Define the label and interval for the LaunchAgent.
        label = "com.kimjansheden.auto-quotes"
        interval = 600  # Every 10 min for now, but user should decide.

        # Get the script's directory.
        script_dir = os.path.dirname(__file__)

        # Set the full paths to the script and the .plist file.
        script_path = os.path.abspath(os.path.join(script_dir, "getprices_script.py"))
        plist_path = os.path.join(script_dir, label + ".plist")

        # Find the path to the Python interpreter running this script.
        python_path = sys.executable

        # Prepare the EnvironmentVariables string.
        env_vars = f"/usr/bin:/bin:/usr/sbin:/sbin:{python_path}"

        # Create the .plist file.
        with open(plist_path, "w") as f:
            f.write(
                f"""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
                "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
                <dict>
                    <key>Label</key>
                    <string>{label}</string>
                    <key>WorkingDirectory</key>
                    <string>{script_dir}</string>
                    <key>ProgramArguments</key>
                    <array>
                        <string>{python_path}</string>
                        <string>{script_path}</string>
                    </array>
                    <key>StartInterval</key>
                    <integer>{interval}</integer>
                    <key>EnvironmentVariables</key>
                    <dict>
                        <key>PATH</key>
                        <string>{env_vars}</string>
                    </dict>
                </dict>
            </plist>
            """
            )

        # Move the .plist file to the LaunchAgents directory.
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        dest_path = os.path.join(launch_agents_dir, f"{label}.plist")
        shutil.move(plist_path, dest_path)

        # Load the LaunchAgent.
        os.system(f"launchctl load {dest_path}")

        # Update the config object.
        self.config["LaunchAgent"]["exists"] = "True"

        # Write the updated config to the config file.
        with open("config.ini", "w") as f:
            self.config.write(f)

        print("LaunchAgent setup was successful.")

    def _get_chrome_version(self, pattern):
        print("Retrieving Chrome Version")

        # Path to the browser
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        # Run the command to fetch the version
        chrome_version_result = subprocess.run(
            [chrome_path, "--version"], stdout=subprocess.PIPE
        )

        # Print and return the version
        if chrome_version_result.returncode == 0:
            chrome_version_decoded = chrome_version_result.stdout.decode(
                "utf-8"
            ).strip()

            chrome_version = re.search(pattern, chrome_version_decoded).group()
            print(f"Chrome Version: {chrome_version}")
            return chrome_version
        else:
            print("Failed to retrieve Chrome version.")
            return None

    def _get_chromedriver_version(self, pattern, chromedriver_path):
        print("Retrieving ChromeDriver Version")

        # Check if chromedriver already exists
        if os.path.exists(chromedriver_path):
            print("Chromedriver is downloaded. Checking version.")

            chromedriver_version_result = subprocess.run(
                [chromedriver_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Print and return the version
            if chromedriver_version_result.returncode == 0:
                chromedriver_decoded = chromedriver_version_result.stdout.decode(
                    "utf-8"
                ).strip()

                chromedriver_version = re.search(pattern, chromedriver_decoded).group()
                print(f"ChromeDriver Version: {chromedriver_version}")
                return chromedriver_version
            else:
                print("Failed to retrieve ChromeDriver version.")
                return None
        else:
            print("ChromeDriver is not downloaded.")
            return None

    def _check_if_current(self, chrome_version, chromedriver_version):
        print("Checking if chromedriver is the latest version.")
        if chromedriver_version == chrome_version:
            print("You have the current version of chromedriver.")
            return True
        else:
            print("Your version of ChromeDriver is outdated or missing.")
            return False

    def _download_and_extract_chromedriver(self, chromedriver_path):
        # Desired channel and platform
        channel = "Stable"
        platform = "mac-arm64"

        # URL to the JSON file with the latest versions
        url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

        # Make a GET request to the URL
        response = requests.get(url)
        data = response.json()

        # Retrieve the download link for ChromeDriver for the selected channel and platform
        download_url = None
        for item in data["channels"][channel]["downloads"]["chromedriver"]:
            if item["platform"] == platform:
                download_url = item["url"]
                break

        # Check if the URL was found
        if download_url is not None:
            print(f"Downloading ChromeDriver from {download_url}")

            # Download the ZIP file
            response = requests.get(download_url)

            # Save the ZIP file to disk
            zip_path = "chromedriver.zip"
            with open(zip_path, "wb") as file:
                file.write(response.content)

            # Unpack the ZIP file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall("chromedriver")

            # Give the file permission to run for all users
            os.chmod(chromedriver_path, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            print(
                f"ChromeDriver has been downloaded and successfully extracted to {os.path.abspath(chromedriver_path)}"
            )
            return True
        else:
            print(
                f"Could not find ChromeDriver for the platform {platform} in the channel {channel}."
            )
            return False

    def get_latest_from_json(self):
        """
        Retrieves the latest version of ChromeDriver compatible with the installed Chrome browser
        for the specified channel and platform. If the current version is not up-to-date,
        it downloads and extracts the latest version.

        :return: The absolute path to the latest ChromeDriver if successful, None otherwise.
        """
        # Search pattern for the version numbers
        pattern = r"\d+\.\d+\.\d+\.\d+"

        # Path to the extracted ChromeDriver
        chromedriver_path = os.path.join(
            "chromedriver", "chromedriver-mac-arm64", "chromedriver"
        )
        chromedriver_path_abs = os.path.abspath(chromedriver_path)

        # Get Chrome Version
        chrome_version = self._get_chrome_version(pattern)

        # Get ChromeDriver Version
        chromedriver_version = self._get_chromedriver_version(
            pattern, chromedriver_path
        )

        # Check if ChromeDriver is the latest version
        is_current = self._check_if_current(chrome_version, chromedriver_version)

        if is_current:
            return chromedriver_path_abs

        # If not latest version
        success = self._download_and_extract_chromedriver(chromedriver_path)

        if success:
            return chromedriver_path_abs
        return None


def column_name_to_index(column_name):
    """
    Converts an alphanumeric column name to a numeric index.

    Parameters:
        column_name (str): A string representing an alphanumeric column name, e.g. "A", "B", "AA", "AB", etc.

    Returns:
        int: The numeric index of the column, where the first column "A" has index 1, "B" has index 2, etc.

    Raises:
        ValueError: If the input column_name is not a valid alphanumeric column name.

    Examples:
        >>> column_name_to_index("A")
        1
        >>> column_name_to_index("S")
        19
        >>> column_name_to_index("ZZ")
        702
    """
    index = 0
    for i, c in enumerate(reversed(column_name)):
        if not c.isalpha():
            raise ValueError(f"{column_name} is not a valid column name")
        index += (ord(c.upper()) - ord("A") + 1) * (26**i)
    return index
