import os
import time
from service import load_checkpoint, save_checkpoint, get_first_column_as_list, test_pattern, extract_and_save_leaf_codes, split_and_save_data
from models import LeafClassificationsDict, Checkpoint

def main():
    checkpoint_file = 'checkpoint.json'
    output_dir = 'output_data'
    file_path = 'UCIDs List.xlsx'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load checkpoint
    checkpoint = load_checkpoint(checkpoint_file)
    last_processed_ucid = checkpoint.last_processed_ucid

    first_column_list = get_first_column_as_list(file_path)

    leaf_classifications_dict = LeafClassificationsDict()
    done_patents = set()

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
                extract_and_save_leaf_codes(base_url, co_doc_kind, count, done_patents, leaf_classifications_dict)
                # Update checkpoint after processing each UCID
                checkpoint_data = Checkpoint(last_processed_ucid=ucid)
                save_checkpoint(checkpoint_data, checkpoint_file)
                time.sleep(10)

    except Exception as error:
        raise error

    finally:
        # Split data into chunks of 1000 and save as JSON files
        split_and_save_data(leaf_classifications_dict, output_dir)

if __name__ == "__main__":
    main()
