import psycopg2
import psycopg2.extras
import orjson
from elasticsearch import Elasticsearch, helpers
from datetime import datetime
import time
import os

# PostgreSQL config
db = psycopg2.connect(
    host='localhost',
    user='misskey-user',
    password='password',
    database='misskey',
    port=5432,
    cursor_factory=psycopg2.extras.DictCursor
)

# Elasticsearch config
es_url = "http://localhost:9200"
es_username = "elastic_user"  # Your Elasticsearch Username
es_password = "elastic_pwd"  # Your Elasticsearch Password

es = Elasticsearch(es_url,
    basic_auth=(es_username, es_password)
)

# decode unixtimestamp (include milliseconds) from aid.
# ref. https://github.com/misskey-dev/misskey/blob/4b295088fd6b4bead05087537415b10419eee78f/packages/backend/src/misc/id/aid.ts#L34
def parse_aid(id):
    TIME2000 = 946684800000
    t = int(int(id[:8], 36) + TIME2000)
    return t

lmt = 10000
batch_count = 0
batch_limit = 50

offset_file = 'offset.txt'
if os.path.exists(offset_file):
    with open(offset_file, 'r') as f:
        ofs = int(f.read().strip())
else:
    ofs = 0

def generate_index_name(batch_count):
    # e.g., "---notes-202410-1", "---notes-202410-2", etc.
    index_base = "---notes" + "-" + datetime.now().strftime("%Y%m")
    return index_base + f"-{batch_count // batch_limit + 1}"

index = generate_index_name(batch_count)

def save_offset(ofs):
    """ Save the current offset to a file """
    with open(offset_file, 'w') as f:
        f.write(str(ofs))

while True:
    notes = []
    try:
        with db.cursor() as cur:
            cur.execute('SELECT "id", "userId", "userHost", "channelId", "cw", "text", "tags" FROM "note" \
                        WHERE ("note"."text" IS NOT NULL) \
                        LIMIT %s OFFSET %s', (lmt, ofs))
            qnotes = cur.fetchall()
            if not qnotes:
                print("No more notes to process.")
                break

        for note in qnotes:
            notes.append({
                '_index': index,
                '_id': note['id'],
                'createdAt': parse_aid(note['id']),
                'userId': note['userId'],
                'userHost': note['userHost'],
                'channelId': note['channelId'],
                'cw': note['cw'],
                'text': note['text'],
                'tags': note['tags']
            })

        if notes:
            retries = 7
            while retries > 0:
                try:
                    helpers.bulk(es, notes)
                    break
                except Exception as e:
                    print(f"Error while writing to Elasticsearch: {e}")
                    retries -= 1
                    if retries > 0:
                        print(f"Retrying... ({3 - retries}/3)")
                        time.sleep(5)
                    else:
                        raise e

        batch_count += 1
        if batch_count % batch_limit == 0:
            index = generate_index_name(batch_count)
            print(f"Switching to new index: {index}")

        save_offset(ofs)
        print(f'{ofs=} {lmt=} {len(notes)=}')
        ofs += lmt

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Current offset: {ofs}. Saving and exiting...")
        save_offset(ofs)
        break

db.close()
