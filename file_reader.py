import pandas as pd

def excel_reader(file_path):
    """
    Reads an Excel file and returns a DataFrame.
    :param file_path: Path to the Excel file.
    :return: Pandas DataFrame containing the file data.
    """
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.astype(str)
        df = df.astype(str)  # <-- Add this

        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def csv_reader(file_path):
    """
    Reads a CSV file and returns a DataFrame.
    :param file_path: Path to the CSV file.
    :return: Pandas DataFrame containing the file data.
    """
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.astype(str)
        df = df.astype(str)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None