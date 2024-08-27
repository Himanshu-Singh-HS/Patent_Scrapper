# services.py
import re
import requests
from bs4 import BeautifulSoup
import json
import os
from models import LeafClassifications

leaf_classifications_dict = LeafClassifications(classifications={})
done_patents = set()

def get_first_column_as_list(file_path: str) -> list:
    import pandas as pd
    dataframe = pd.read_excel(file_path)
    first_column_series = dataframe.iloc[:, 0]
    return first_column_series.tolist()

def separate_string(s: str) -> tuple:
    pattern = re.compile(r'^([A-Za-z]*)(\d+)$')
    match = pattern.match(s)
    return (match.group(1), match.group(2)) if match else (None, None)

def test_pattern(text: str) -> tuple:
    text1 = re.sub(r'[\W_]+', '', text).upper().strip()
    pattern = r"([A-Z]{2})([A-Z]?[0-9]+)([A-Z]{0,1}[0-9]*)"
    match = re.match(pattern, text1, re.IGNORECASE)
    return match.groups() if match else None

def get_first_leaf_classification(url: str, ucid: str) -> None:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    found = False

    for li in soup.find_all('li', itemprop='classifications'):
        meta_leaf = li.find('meta', itemprop='Leaf', content='true')
        if meta_leaf:
            code_span = li.find('span', itemprop='Code')
            if code_span:
                code = code_span.get_text(strip=True)
                parts = code.split('/')
                if parts[0] not in leaf_classifications_dict.classifications:
                    leaf_classifications_dict.classifications[parts[0]] = [ucid]
                else:
                    leaf_classifications_dict.classifications[parts[0]].append(ucid)
                found = True
                break

    if not found:
        if 'no_classification_data' not in leaf_classifications_dict.classifications:
            leaf_classifications_dict.classifications['no_classification_data'] = [ucid]
        else:
            leaf_classifications_dict.classifications['no_classification_data'].append(ucid)

def format_number_with_padding(reference_number_str: str, target_number: int) -> str:
    reference_length = len(reference_number_str)
    target_number_str_length = len(str(target_number))
    
    if reference_length > target_number_str_length:
        padding_needed = reference_length - target_number_str_length
        return "0" * padding_needed + str(target_number)
    return str(target_number)

def extract_and_save_leaf_codes(base_url: str, co_doc_kind: tuple, count: int) -> None:
    alphabets, numbers = separate_string(co_doc_kind[1])
    numbers_int = int(numbers)
    
    for i in range(numbers_int, numbers_int - count, -1):
        final_number = format_number_with_padding(numbers, i)
        patent_number = f"{co_doc_kind[0]}{alphabets or ''}{final_number}"
        if patent_number in done_patents:
            print(f'Patent number {patent_number} has already been scrapped. Continuing with the next item.')
            continue
        done_patents.add(patent_number)
        url = base_url.format(patent_number)
        print(f"Processing {patent_number}...")
        get_first_leaf_classification(url, patent_number)

        if len(done_patents) % 10 == 0:
            with open('leaf_classifications_dict.json', 'w') as file:
                json.dump(leaf_classifications_dict.dict(), file, indent=4)
            print("Progress saved.")
    print(f'Co-document kind {"".join(co_doc_kind)} has been scrapped with a descending count of 10.')
