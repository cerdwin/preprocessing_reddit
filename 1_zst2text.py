import zstandard
import os
import json
import sys
from datetime import datetime
import logging.handlers
from tqdm import tqdm 

log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

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

keywords = ['nterest rat', 'nflation', 'mploy', 'overnment', 'anking syst', 'limate chang', "kraine", 'nternational coop', ]
if __name__ == "__main__":
    min_account_age = 30 * 24 * 60 * 30  # 15 days in seconds
    min_karma = 10
    file_path = sys.argv[1]
    file_size = os.stat(file_path).st_size
    file_lines = 0
    file_bytes_processed = 0
    created = None
    bad_lines = 0
    bodies = []
    data = {}
    for line, file_bytes_processed in tqdm(read_lines_zst(file_path), desc="Processing lines"):
        try:
            obj = json.loads(line)
            #If an account is less than 14 days old, we don't want to consider it
            if obj['author_created_utc']:
                account_age = obj['created_utc'] - obj['author_created_utc']
                if account_age < min_account_age:
                    continue
            if not any(keyword in obj["body"] for keyword in keywords):
                continue

            #if 'bot' in obj["author"] or account_age < min_account_age or obj["body"] == '[removed]':
             #   continue
            if obj['subreddit'] not in data.keys():
                data[obj['subreddit']] = []
            #print("OBJ IS: ")
            #print(obj)
            data[obj['subreddit']].append(obj["body"])
            bodies.append(obj["body"])
            created = datetime.utcfromtimestamp(int(obj['created_utc']))
        except (KeyError, json.JSONDecodeError) as err:
            print(" _________________________- FOUND A BAD LINE")
            bad_lines += 1
        file_lines += 1
        if file_lines % 100000 == 0:
            log.info(
                f"{created.strftime('%Y-%m-%d %H:%M:%S')} : {file_lines:,} : {bad_lines:,} : {file_bytes_processed:,}:{(file_bytes_processed / file_size) * 100:.0f}%")
    current_body = ""
    adjusted_bodies = []
    log.info(f"Created subreddits count:{len(data.keys())} and their names {data.keys()}")

    for k,v in data.items():
        for post in v:
            if len(current_body)+len(post)>512:
                adjusted_bodies.append(current_body)
                current_body = post
            else:
                current_body = current_body + ' '+post
    #for i in bodies:
        #i = i.replace("[deleted]", "").replace("\n", "")
    #    if len(current_body) + len(i) > 512 and len(current_body) > 0:
    #        adjusted_bodies.append(current_body)
    #        current_body = i
    #    else:
    #        current_body += i


    new_name = 'updated_'+file_path.split('.')[0] + '.txt'
    f = open(new_name, "w")
    for i in adjusted_bodies:
        f.write(i)
        #f.write('\n')
    log.info(f"Complete : {file_lines:,} : {bad_lines:,}")

