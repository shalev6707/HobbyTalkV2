import json


class DBManager:

    @staticmethod
    def read(db_name: str) -> dict or None:
        """
          Reads a JSON file and returns the data as a Python object (dict).
          :param db_name: Path to the JSON file.
          :return: Parsed data from the file.
          """

        try:
            with open(db_name, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"Error: File '{db_name}' not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error: File '{db_name}' contains invalid JSON.")
            return None

    @staticmethod
    def write(db_name: str, data: dict) -> None:
        """
        Writes Python data (dict) to a JSON file.
        :param db_name: Path to the JSON file.
        :param data: Python object (dict or list) to write.
        """
        try:
            with open(db_name, 'w') as f:
                json.dump(data, f)
            print(f"Data written to successfully in '{db_name}'.")
        except FileNotFoundError:
            print(f"Error: File '{db_name}' not found.")
