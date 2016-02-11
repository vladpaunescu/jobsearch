from os import listdir

IGNORE_DIR = "gitignores"
MERGED_FILE =".gitignore"
COMMENT = "### generated from {} ###\n"


def main():
    files = listdir(IGNORE_DIR)
    merged = ""
    for f in files:
    	with open ("{}/{}".format(IGNORE_DIR, f)) as fin:
    		data = fin.read()
    		merged += COMMENT.format(f)
    		merged += data
    		merged += "\n"
    
    with open(MERGED_FILE, "w") as fout:
    	fout.write(merged)


if __name__ == '__main__':
    main()