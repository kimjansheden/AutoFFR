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

class Helper:
    def __init__(self):
        pass

    # In case I want to access the method through the class.
    # If not, this can be deleted in the future.
    @staticmethod
    def column_name_to_index(column_name):
        return column_name_to_index(column_name)