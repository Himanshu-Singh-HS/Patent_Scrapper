
import re
import time
import json
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
 
leaf_classifications_dict = {"no_classification_data": []}
done_patents = set()

checkpoint_file = 'checkpoint.json'


 ##---------------------------------------------------------
# Function to load the checkpoint
def load_checkpoint():
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as file:
            return json.load(file)
    return {}

# Function to save the checkpoint
def save_checkpoint(checkpoint_data):
    with open(checkpoint_file, 'w') as file:
        json.dump(checkpoint_data, file, indent=4)

##---------------------------------------------






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
def get_first_leaf_classification(url, ucid):
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
                if parts[0] not in leaf_classifications_dict:
                    leaf_classifications_dict[parts[0]] = [ucid]
                else:
                    leaf_classifications_dict[parts[0]].append(ucid)
                found = True
                break
    if not found:
        leaf_classifications_dict['no_classification_data'].append(ucid)

 
def format_number_with_padding(reference_number_str, target_number):
    reference_length = len(reference_number_str)
    target_number_str_length = len(str(target_number))
    
    if reference_length > target_number_str_length:
        padding_needed = reference_length - target_number_str_length
        return "0" * padding_needed + str(target_number)
    return str(target_number)

# Function to extract and save leaf codes
def extract_and_save_leaf_codes(base_url, co_doc_kind, count):
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
        get_first_leaf_classification(url, patent_number)
    print(f'Co-document kind {"".join(co_doc_kind)} has been scrapped with a descending count of 10.')

 
output_dir = 'output_data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load checkpoint
checkpoint = load_checkpoint()
last_processed_ucid = checkpoint.get('last_processed_ucid', None)

file_path = 'UCIDs List.xlsx'
first_column_list = get_first_column_as_list(file_path)

try:
    start_processing = False if last_processed_ucid else True

    for ucid in set(first_column_list):
        if not start_processing:
            if ucid == last_processed_ucid:
                start_processing = True
            continue

        co_doc_kind = test_pattern(ucid)
        if co_doc_kind:
            base_url = 'https://patents.google.com/patent/{}/en'
            count = 10
            extract_and_save_leaf_codes(base_url, co_doc_kind, count)
            # Update checkpoint after processing each UCID
            checkpoint_data = {'last_processed_ucid': ucid}
            save_checkpoint(checkpoint_data)
            time.sleep(10)

except Exception as error:
    raise error

finally:
    # Split data into chunks of 1000 and save as JSON files
    leaf_classifications_items = list(leaf_classifications_dict.items())
    for i in range(0, len(leaf_classifications_items), 1000):
        chunk = dict(leaf_classifications_items[i:i + 1000])
        file_name = os.path.join(output_dir, f'leaf_classifications_chunk_{i // 1000 + 1}.json')
        with open(file_name, 'w') as file:
            json.dump(chunk, file, indent=4)
    print(leaf_classifications_dict)
    print(len(done_patents))



