import bs4
import urllib2
import urllib
import traceback
import os
import sys
from pymongo import MongoClient
import json
from time import sleep
from samba.provision.sambadns import TXTRecord

CRAWL_DIR = "crawl"
USER_AGENT = ('User-Agent', 'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')
ROOT_URL = "http://www.bestjobs.ro/cautare/locuri-de-munca/ignore/bucuresti-municipiul-bucuresti-romania/cmt"
COOKIE = ('Cookie', 
                                  """uniquevisitor=de561f1bdaa28cf5bcd0df21f6a7b19e; bjGeoLoc=0-0; jobfeed_preferences=ELQVGQ-yeLPZUJV6jbOhpOPdU23GSOXJT2EfmXiiYqHsMfjcwT-6O4VJt5vN1VWlvym1aupxVT77diRtbUw-r4pmsH4Z4eHI6yNI-M24qE_E_skbhGqODQ..; rvj3=751321%7E1%7C740662%7E1%7C740659%7E1%7C751744%7E1%7C752115%7E1%7C749448%7E1; _dc_gtm_UA-1528351-2=1; _ga=GA1.2.10765448.1449602482; tmprealsrch=1; bjrefdom=1""")

mappings = [("nivel cariera", "career_level"), ("locatii", "locations"), ("limbi vorbite", "languages")]
jobs = []
companies = []

GET_MORE_JOBS_URL = "http://www.bestjobs.ro/search/_getmorejobs"


def build_request(url, params=""):
    #print 'getting' ,url
        req = urllib2.Request(url)
        req.add_header(USER_AGENT[0], USER_AGENT[1])
        req.add_data(params)
        opener = urllib2.build_opener()
        opener.addheaders.append(COOKIE)
        return req, opener

def get_url_content(url, data=""):
    try:  
        req, opener = build_request(url, data)
        res = opener.open(req)
        return res.read().decode('utf-8')
    except Exception:
        traceback.print_exc()

    return ''

def safe_assign(d, key, elem):
    d[key] = get_utf8_text(elem.text) if elem is not None else ""
    
def get_utf8_text(text):
    return text
    
def save_job(job_desc):
    print "Saving job " + job_desc['url']
    parts = str.split(job_desc['url'], "/")
    if len(parts) < 4:
        print "Skipping job " + job_desc['url']
    with open("{}/{}.json".format(CRAWL_DIR, parts[3]), 'wb') as outfile:
        dump = json.dumps(job_desc, ensure_ascii=False)
        outfile.write(dump.encode("utf-8"))

def process_job (job_link):
    print "Processing " + str(job_link)
    job_url = job_link['href']
    html = get_url_content(job_url)
    soup = bs4.BeautifulSoup(html)
    job_title_div = soup.find('div', class_='jd-title')
    job_desc = {}
    
    job_title = job_title_div.find("h1")
    safe_assign(job_desc, 'title', job_title)
    
    company_name = job_title_div.find('a')
    safe_assign(job_desc, 'company', company_name)
    job_desc['company_url'] = company_name['href'] if company_name is not None else ""
    
    job_desc_div = soup.find('div', class_='jd-header')
    jd_contents = job_desc_div.find_all('td', class_='jd-content')
   
    for i in xrange(0, len(jd_contents), 2):
        if jd_contents[i] is None or jd_contents[i + 1] is None:
            continue
        key = get_utf8_text(jd_contents[i].text)
        val = get_utf8_text(jd_contents[i+1].text)
        for mapping in mappings:
            if mapping[0] in key.lower():
                job_desc[mapping[1]] = val
                break
        
    jd_body_div = soup.find('div', class_='jd-body')
    job_desc['body'] = jd_body_div.text
    print job_desc['body']
    job_desc['url'] = job_url
    save_job(job_desc)
    

def process_jobs(job_links):
    print "{} job links to process".format(len(job_links))
    for job_link in job_links:
        process_job(job_link)
        sleep(0.5)

def process_page(data):
    job_links = []
    company_links = []
    soup = bs4.BeautifulSoup(data)
    joblist = (x for x in soup.find_all('div') if 'class' in x.attrs and 'job-card-inner' in x.attrs['class'])
    for job_e in joblist:
        a_job_company = job_e.find('a', class_="job-company")
        a_job_link = job_e.find('a', class_="job-link")
        company_links.append(a_job_company)
        job_links.append(a_job_link)
    
    process_jobs(job_links)
  
def start_crawl(url):
    data = get_url_content(url)
    process_page(data)
   
    
def get_page(pageno):
    url = GET_MORE_JOBS_URL
    form_data = {'page': pageno}
    params = urllib.urlencode(form_data)
    data = get_url_content(url, params)
    process_page(data)
    
def main():
    if not os.path.exists(CRAWL_DIR):
        os.makedirs(CRAWL_DIR)
    start_crawl(ROOT_URL)
    for i in xrange(2, 20):
        print "Processing page {}".format(i)
        get_page(i)
        

if __name__ == '__main__':
    main()
