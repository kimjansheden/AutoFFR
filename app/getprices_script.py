from scraper import GetPrices
from enum import Enum
from helpers import Helper
import os
import time

class Of(Enum):
    FFR=1,
    ACF=2

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Source(Enum):
    mgex=1

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


print(Of.FFR)

# Initialize the helper object
helper = Helper()

#If started for the first time, create config file.

# Set the path to the config file.
config_file_path = "config.ini"

# Check if the config file exists.
if not os.path.exists(config_file_path):
    # If it doesn't exist, create a new config file
    config = helper.config
    config["Google"] = {"worksheet_id": "<Replace with your worksheet id>"}
    config["LaunchAgent"] = {"exists": "False"}

    with open(config_file_path, "w") as f:
        config.write(f)

# Initialize the scraper object
ffr = GetPrices(Of.FFR, source=Source.mgex)

#If started for the first time, setup the LaunchAgent.
if not eval(ffr.config["LaunchAgent"]["exists"]):
    print("No LaunchAgent detected. Setting up.")
    helper.setup_launch_agent()
    

ffr.start()