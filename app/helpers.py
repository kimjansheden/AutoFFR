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

        # Define the label and interval for the LaunchAgent.
        label = "com.kimjansheden.auto-quotes"
        interval = 600 # Every 10 min for now, but user should decide.

        # Get the current working directory.
        cwd = os.getcwd()

        # Set the paths to the script and the .plist file
        script_path = os.path.join(cwd, "getprices_script.py")
        plist_path = os.path.join(cwd, label + ".plist")

        # Create the .plist file.
        with open(plist_path, "w") as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
                "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
                <dict>
                    <key>Label</key>
                    <string>{label}</string>
                    <key>ProgramArguments</key>
                    <array>
                        <string>/usr/bin/python3</string>
                        <string>{script_path}</string>
                    </array>
                    <key>StartInterval</key>
                    <integer>{interval}</integer>
                </dict>
            </plist>
            """)

        # Copy the .plist file to the LaunchAgents directory.
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        dest_path = os.path.join(launch_agents_dir, plist_path)
        shutil.move(plist_path, dest_path)

        # Load the LaunchAgent.
        os.system(f"launchctl load {dest_path}")

        # Tell the config file that a LaunchAgent has been created.
        self.config["LaunchAgent"]["exists"] = "True"



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