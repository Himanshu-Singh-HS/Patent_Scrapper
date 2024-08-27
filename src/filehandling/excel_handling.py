def get_first_column_as_list(file_path: str) -> list:
    import pandas as pd
    dataframe = pd.read_excel(file_path)
    first_column_series = dataframe.iloc[:, 0]
    return first_column_series.tolist()