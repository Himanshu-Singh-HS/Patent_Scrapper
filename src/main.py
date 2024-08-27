# main.py
import time
import json
import os
from service import get_first_column_as_list, test_pattern, extract_and_save_leaf_codes, leaf_classifications_dict

def main():

    file_path = 'UCIDs List.xlsx'
    first_column_list = get_first_column_as_list(file_path)

    try:
        for ucid in first_column_list:
            with open('last_patent_number', 'w') as file_save:
                file_save.write(ucid)
            co_doc_kind = test_pattern(ucid)
            base_url = 'https://patents.google.com/patent/{}/en'
            count = 10
            extract_and_save_leaf_codes(base_url, co_doc_kind, count)
            time.sleep(10)

    except Exception as error:
        raise error

    finally:
        with open('leaf_classifications_dict.json', 'w') as file:
            json.dump(leaf_classifications_dict.dict(), file, indent=4)
        print(leaf_classifications_dict)

if __name__ == "__main__":
    main()
