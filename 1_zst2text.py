import zstandard
import os
import json
import sys
from datetime import datetime
import logging.handlers
from tqdm import tqdm 
import re

log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
DEBUG = False
KEYWORD_FILTERING = False
keywords = ['nterest rat', 'nflation', 'eflation', 'mploy', 'overnment', 'anking syst', 'limate chang', "kraine", 'nternational coop' ]
min_account_age = 30 * 24 * 60 * 30  # 15 days in seconds
min_karma = -9999 # minimal score of a comment

def read_and_decode(reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0):

    chunk = reader.read(chunk_size)
    bytes_read += chunk_size
    if previous_chunk is not None:
        chunk = previous_chunk + chunk
    try:
        return chunk.decode()
    except UnicodeDecodeError:
        if bytes_read > max_window_size:
            raise UnicodeError(f"Unable to decode frame after reading {bytes_read:,} bytes")
        log.info(f"Decoding error with {bytes_read:,} bytes, reading another chunk")
        return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)

def read_lines_zst(file_name):
    with open(file_name, 'rb') as file_handle:
        buffer = ''
        reader = zstandard.ZstdDecompressor(max_window_size=2 ** 31).stream_reader(file_handle)
        while True:
            chunk = read_and_decode(reader, 2 ** 27, (2 ** 29) * 2)
            if not chunk:
                break
            lines = (buffer + chunk).split("\n")
            for line in lines[:-1]:
                yield line, file_handle.tell()
            buffer = lines[-1]
        reader.close()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = sys.argv[1] # .zst file on input
    file_size = os.stat(file_path).st_size 
    file_lines = 0
    file_bytes_processed = 0
    created = None
    bad_lines = 0
    file_name = os.path.basename(file_path)
    file_name_no_ext = os.path.splitext(file_name)[0]
    new_file_name = file_name_no_ext + '.txt'
    new_path = os.path.join(script_dir, new_file_name)
    
    with open(new_path, "w") as f:
        for line, file_bytes_processed in tqdm(read_lines_zst(file_path), desc="Processing lines"):
            try:
                obj = json.loads(line)
                if not obj['score'] > min_karma:
                    continue
                if obj['author_created_utc']:
                    account_age = obj['created_utc'] - obj['author_created_utc']
                    if account_age < min_account_age:
                        continue
                
                if KEYWORD_FILTERING and not any(keyword in obj["body"] for keyword in keywords):
                    continue

                # Write the text of each comment
                f.write(obj["body"] + '\n')
                if DEBUG:
                    print(obj["body"] + '\n')
                created = datetime.utcfromtimestamp(int(obj['created_utc']))
            except (KeyError, json.JSONDecodeError) as err:
                print(" _________________________- FOUND A BAD LINE")
                bad_lines += 1
            file_lines += 1

            if file_lines % 10000 == 0:  # Adjust this number as needed
                log.info(f"Processed {file_lines:,} lines. Bad lines: {bad_lines:,}. Progress: {(file_bytes_processed / file_size) * 100:.0f}%")

            if DEBUG and file_lines>20:
                break

    log.info(f"Complete : {file_lines:,} : {bad_lines:,}")

