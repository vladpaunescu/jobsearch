import json
from os import listdir
from os.path import isfile



CRAWL_DIR = "crawl"
MERGED_FILE = "bestjobs20150211.json"

def trim_newline(input_d):
    for k in input_d:
        old = input_d[k]
        trimmed = old.replace("\n", "")
        print old
        print trimmed
        

def process_json(out, f):
    with open("{}/{}".format(CRAWL_DIR, f), "r") as js:
        data = json.load(js, encoding="utf-8")
        out.append(data)
   
def main():
    files = listdir(CRAWL_DIR)
    out = []
    for f in files:
        process_json(out, f)
    with open(MERGED_FILE, "wb") as fout:
        dump = json.dumps(out, ensure_ascii=False)
        fout.write(dump.encode("utf-8"))
        

if __name__ == '__main__':
    main()
