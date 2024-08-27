
import re,time,json,os
import requests
import pandas as pd
from bs4 import BeautifulSoup
 

leaf_classifications_dict = {}
done_patents=set()
def get_first_column_as_list(file_path):
    
    dataframe = pd.read_excel(file_path)
    first_column_series = dataframe.iloc[:, 0]
    first_column_list = first_column_series.tolist()
    
    return first_column_list

def separate_string(s):
    
    pattern = re.compile(r'^([A-Za-z]*)(\d+)$')
    match = pattern.match(s)
    if match:
        alphabets = match.group(1)
        numbers = match.group(2)
        return alphabets, numbers
    else:
        return None, None

def test_pattern(text):
    text1 = re.sub(r'[\W_]+', '', text).upper().strip()
    pattern = r"([A-Z]{2})([A-Z]?[0-9]+)([A-Z]{0,1}[0-9]*)"
    match = re.match(pattern, text1, re.IGNORECASE)
    if match is not None:
        x = "-".join(filter(None, match.groups()))
        return match.groups()
    else:
        print(match,text)
        return None


def get_first_leaf_classification(url,ucid):
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    found = False

    # Find all list items that have a meta tag with itemprop="Leaf" and content="true"
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
                    leaf_classifications_dict[parts[0]].append(ucid) # For codes without '/'
                
                found = True
                break
    if not found:
        leaf_classifications_dict['no_classification_data'].append(ucid)

    return None

def format_number_with_padding(reference_number_str, target_number):
    reference_length = len(reference_number_str)
    target_number_str_length = len(str(target_number))
    
    if reference_length > target_number_str_length:
        padding_needed = reference_length - target_number_str_length
        if abs(padding_needed) != padding_needed:
            return None
        padded_number = "0" * padding_needed + str(target_number)
        return padded_number
    else:
        return str(target_number)


    
def extract_and_save_leaf_codes(base_url, co_doc_kind, count):
    
    alphabets, numbers = separate_string(co_doc_kind[1]) 
    numbers_int = int(numbers)
    for i in range(numbers_int, numbers_int - count, -1):
        if abs(i) != i:
            break
        final_number = format_number_with_padding(numbers, i)
        if alphabets:
            patent_number = "".join([co_doc_kind[0],alphabets,final_number])
        else:
            patent_number = "".join([co_doc_kind[0],final_number])
        print(patent_number)
        if patent_number in done_patents:
            print(f'Patent number {patent_number} has already been scrapped. Continuing with the next item.')
            continue
        done_patents.add(patent_number)
        url = base_url.format(patent_number)
        print(f"Processing {patent_number}...")
        leaf_code = get_first_leaf_classification(url,patent_number)
        
        if len(done_patents) % 10 == 0:   
            with open('leaf_classifications_dict.json', 'w') as file:
                json.dump(leaf_classifications_dict, file, indent=4)
            print("Progress saved.")
    print(f'Co-document kind {"".join(co_doc_kind)} has been scrapped with a descending count of 10.')

    return None



file_path = 'UCIDs List.xlsx'
first_column_list = get_first_column_as_list(file_path)


try:
    for ucid in first_column_list:
         
        with open('last_patent_number','w') as file_save:
            file_save.write(ucid)      
        co_doc_kind= test_pattern(ucid)
        base_url = 'https://patents.google.com/patent/{}/en'
        count=10
        extract_and_save_leaf_codes(base_url, co_doc_kind, count)
        time.sleep(10)
        

except Exception as error:
    raise error
     
finally:

    with open('leaf_classifications_dict.json', 'w') as file:
        json.dump(leaf_classifications_dict, file, indent=4)
    print(leaf_classifications_dict)
    print(len(done_patents))







 

