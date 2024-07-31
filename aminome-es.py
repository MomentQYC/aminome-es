import psycopg2
import psycopg2.extras
import orjson
from elasticsearch import Elasticsearch, helpers
from datetime import datetime

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
index = ""
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
ofs = 0

index = index + "---notes" + "-" + datetime.now().strftime("%Y%m")

while True:
    notes = []
    with db.cursor() as cur:
        cur.execute('SELECT "id", "userId", "userHost", "channelId", "cw", "text", "tags" FROM "note" \
                    WHERE ("note"."text" IS NOT NULL) \
                    LIMIT %s OFFSET %s', (lmt, ofs))
        qnotes = cur.fetchall()
        if not qnotes:
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
        helpers.bulk(es, notes)
    print(f'{ofs=} {lmt=} {len(notes)=}')
    ofs += lmt

db.close()
