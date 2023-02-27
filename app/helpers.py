import configparser

class Helper:
    def __init__(self):
        # Read the configuration file
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    # In case I want to access the method through the class.
    # If not, this can be deleted in the future.
    def column_name_to_index(self, column_name):
        return column_name_to_index(column_name)

    def setup_launch_agent(self):
        import os
        import shutil
        import subprocess

        # Define the label and interval for the LaunchAgent.
        label = "com.kimjansheden.auto-quotes"
        interval = 600 # Every 10 min for now, but user should decide.

        # Get the script's directory.
        script_dir = os.path.dirname(__file__)

        # Set the full paths to the script and the .plist file.
        script_path = os.path.abspath(os.path.join(script_dir, "getprices_script.py"))
        #script_path = os.path.join(cwd, "getprices_script.py")
        plist_path = os.path.join(script_dir, label + ".plist")

        # Find the path to the user's installed version of Python3.
        python3_path = subprocess.check_output(["which", "python3"]).strip().decode("utf-8")

        # Create the .plist file.
        with open(plist_path, "w") as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
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
                        <string>{python3_path}</string>
                        <string>{script_path}</string>
                    </array>
                    <key>StartInterval</key>
                    <integer>{interval}</integer>
                </dict>
            </plist>
            """)

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
            index += (ord(c.upper()) - ord('A') + 1) * (26 ** i)
        return index