import os
import requests
from bs4 import BeautifulSoup
import time
import datetime

def get_bugid_from_url(url):
    time.sleep(5)
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    pinned = soup.findAll('div',{"class":"mt-1 text-small text-gray pinned-item-desc"})
    pinned_id = []
    for r in pinned:
        if 'was closed' not in str(r):
            continue
        issue_id = int(str(r).split('\n')[2].strip().replace('#',''))
        pinned_id.append(issue_id)

    result = soup.findAll('span',{"class":"opened-by"})
    bugids = []
    for r in result:
        # 1. Filtering non-closed reports
        if 'was closed' not in str(r):
            continue
        bid = int(str(r).split('\n')[1].strip().replace('#',''))
        # 2. Filtering the pinned bug reports
        if bid in pinned_id:
            continue
        bugids.append(bid)
    if len(bugids) == 0 and "no results matched" not in str(html):
        bugids.append("NONE")
    return bugids

def get_buglink(project):
    time.sleep(5)
    url = f"https://github.com/{project}/issues/show_menu_content?partial=issues%2Ffilters%2Flabels_content&q=is%3Aissue+is%3Aclosed"
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    result = soup.findAll('a',{"class":"SelectMenu-item flex-items-start label-select-menu-item js-issues-label-select-menu-item"})
    label_links = [x['href'] for x in result]
    buglinks = [x for x in label_links if 'bug' in x.lower()]
    buglinks = [f"https://github.com{x}" for x in buglinks]
    return buglinks

def get_closedBR_meta(urls):
    # return Closed BR#, page# 
    closed_num = 0
    page_num = '_'
    for url in urls:
        html = requests.get(url).text
        soup = BeautifulSoup(html,'html.parser')
        closed_num += int(soup.select('#js-issues-toolbar > div > div.flex-auto.d-none.d-lg-block.no-wrap > div > a.btn-link.selected')[0].text.split()[0].replace(",",""))
        page_nums = soup.select('#js-repo-pjax-container > div.container-xl.clearfix.new-discussion-timeline.px-3.px-md-4.px-lg-5 > div > div > div.paginate-container.d-none.d-sm-flex.flex-sm-justify-center > div > em')
        if len(page_nums)!=0:
            page_num = page_num+'_'+str(page_nums[0]['data-total-pages'])
        if len(page_nums)==0:
            page_num = page_num+'_0'
        time.sleep(5)
    return closed_num, page_num, urls



target_projects = set()
project_path = "./data/stage1_projects/2nd_project_descriptions.tsv"
f = open(project_path, "r", encoding="utf8")
for line in f.readlines():
    project_name = line.split("\t")[0].lower()
    project_type = line.split("\t")[1]
    if project_type == "NODLSW":
        continue
    target_projects.add(project_name)

# f = open(project_path,"a", encoding = "utf8")
# f.close()
for project in target_projects:    
    # 1. Load meta data for crawling the bug reports because of limit-rate of GitHub API
    urls = get_buglink(project)
    closed_num, br_pages, urls = get_closedBR_meta(urls)
    if br_pages == '_':
        br_pages = [1]
    else:
        br_pages = br_pages.split('_')
        br_pages = [int(x) for x in br_pages if x!='']

    print(project, urls)
    # 2. Load bug ids with bug label
    f = open("./data/stage2_groundtruths/1st_candidate_bugs.csv","a", encoding = "utf8")
    for i, url in enumerate(urls):
        prefix = url.split("?")[0]
        suffix = url.split("?", 2)[1]
        bug_label = suffix.split("%3A")[len(suffix.split("%3A"))-1]
        bug_ids = set()
        max_br_pages = br_pages[i]
        if max_br_pages == 0:
            max_br_pages = 1
        for j in range(1, max_br_pages+1):
            page_url = prefix +"?page="+str(j)+ "&"+suffix
            page_bug_ids = get_bugid_from_url(page_url)
            while len(page_bug_ids) == 0:
                time.sleep(5)
                page_bug_ids = get_bugid_from_url(page_url)
            if page_bug_ids[0] != "NONE":
                bug_ids = bug_ids.union(page_bug_ids)
        time.sleep(5)                
        print(project, bug_label, len(bug_ids))
        for bug_id in bug_ids:
            if bug_label.lower().find('not') > -1:
                continue
            f.write(project+","+bug_label+","+str(bug_id)+"\n")
    f.close()