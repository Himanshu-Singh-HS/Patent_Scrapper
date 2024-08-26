import os
import json
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from models import LeafClassificationsDict, Checkpoint

# Load and Save Checkpoint Functions
def load_checkpoint(checkpoint_file):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as file:
            return Checkpoint.parse_obj(json.load(file))
    return Checkpoint()

def save_checkpoint(checkpoint_data, checkpoint_file):
    with open(checkpoint_file, 'w') as file:
        json.dump(checkpoint_data.dict(), file, indent=4)

# Data Processing Functions
def get_first_column_as_list(file_path):
    dataframe = pd.read_excel(file_path)
    first_column_series = dataframe.iloc[:, 0]
    return first_column_series.tolist()

def separate_string(s):
    pattern = re.compile(r'^([A-Za-z]*)(\d+)$')
    match = pattern.match(s)
    if match:
        return match.group(1), match.group(2)
    return None, None

def test_pattern(text):
    text1 = re.sub(r'[\W_]+', '', text).upper().strip()
    pattern = r"([A-Z]{2})([A-Z]?[0-9]+)([A-Z]{0,1}[0-9]*)"
    match = re.match(pattern, text1, re.IGNORECASE)
    if match:
        return match.groups()
    print(match, text)
    return None

# Function to get the first leaf classification from URL
def get_first_leaf_classification(url, ucid, leaf_classifications_dict):
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
        leaf_classifications_dict.no_classification_data.append(ucid)

def format_number_with_padding(reference_number_str, target_number):
    reference_length = len(reference_number_str)
    target_number_str_length = len(str(target_number))
    
    if reference_length > target_number_str_length:
        padding_needed = reference_length - target_number_str_length
        return "0" * padding_needed + str(target_number)
    return str(target_number)

# Function to extract and save leaf codes
def extract_and_save_leaf_codes(base_url, co_doc_kind, count, done_patents, leaf_classifications_dict):
    alphabets, numbers = separate_string(co_doc_kind[1])
    numbers_int = int(numbers)
    for i in range(numbers_int, numbers_int - count, -1):
        if abs(i) != i:
            break
        final_number = format_number_with_padding(numbers, i)
        patent_number = "".join([co_doc_kind[0], alphabets or '', final_number])
        if patent_number in done_patents:
            print(f'Patent number {patent_number} has already been scrapped. Continuing with the next item.')
            continue
        done_patents.add(patent_number)
        url = base_url.format(patent_number)
        print(f"Processing {patent_number}...")
        get_first_leaf_classification(url, patent_number, leaf_classifications_dict)
    print(f'Co-document kind {"".join(co_doc_kind)} has been scrapped with a descending count of 10.')

def split_and_save_data(leaf_classifications_dict, output_dir):
    leaf_classifications_items = list(leaf_classifications_dict.classifications.items())
    for i in range(0, len(leaf_classifications_items), 1000):
        chunk = dict(leaf_classifications_items[i:i + 1000])
        file_name = os.path.join(output_dir, f'leaf_classifications_chunk_{i // 1000 + 1}.json')
        with open(file_name, 'w') as file:
            json.dump(chunk, file, indent=4)
    print(leaf_classifications_dict.dict())
