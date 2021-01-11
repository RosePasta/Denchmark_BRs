import os
import requests
from bs4 import BeautifulSoup
import time
import util_extractor 
extractor = util_extractor.extractor()


def load_projects():
    lines = open("./data/stage2_bugreports/1st_candidate_bugs.csv", "r", encoding="utf8").readlines()
    project_bugs = {}
    all_bug_num = 0
    for line in lines[1:]:
        line = line.replace("\n","")
        project = line.split(",")[0].lower()
        bugid = line.split(",")[2]
        if project in project_bugs.keys():
            if bugid not in project_bugs[project]:
                project_bugs[project].add(bugid)
                all_bug_num +=1
        else:
            project_bugs[project] = set()
            project_bugs[project].add(bugid)
            all_bug_num +=1
    return project_bugs, all_bug_num

project_bugs, bug_num = load_projects()
print(len(project_bugs), bug_num)

f = open("./data/stage3_groundtruths/1st_candidate_bugs_with_pr.csv", "r", encoding="utf8")
lines = f.readlines()
already_set = set()
for line in lines:
    project = line.split(",")[0].lower()
    bug_id = line.split(",")[1]
    already_set.add(project+"-"+bug_id)

num_bugs = 0
all_bugs = 0
noevent_bugs = 0
already_bugNum = 0
flag = False
for project in project_bugs.keys():
    bugs = project_bugs[project]
    print(project, len(bugs))
    for bug in bugs:
        if str(project+"-"+bug) in already_set:
            print(project+"-"+bug, "ALREADY")
            continue
        all_bugs = all_bugs + 1
        url = "https://github.com/"+project+"/issues/"+bug
        bsObject = extractor.get_soup(url)

        f = open("./data/stage3_groundtruths/1st_candidate_bugs_with_pr.csv", "a", encoding="utf8")
        assert bsObject != None
        events, events_text = extractor.get_events(bsObject)
        if len(events)==0:
            noevent_bugs =noevent_bugs + 1
            return_string = project+","+bug+",NOPR(EVENT),"
            f.write(return_string+"\n")

            print('[NO event]',bug,'\n')
            continue
        events = [x.lower() for x in events]
        events = [x for x in events if project.lower() in x.lower()]
        events_links = [f"https://www.github.com{x}" for x in events]
        print(bug, events_links)
        for event in events_links:
            pr_id = event.split("/")[len(event.split("/"))-1]
            data_key = project.replace("+","/")+"-"+bug+"-"+pr_id

            # Filtering the pull requests which have the past ID than bug id
            if int(bug) > int(pr_id):         
                # return_string = project+","+bug+",NOPR(PREVID"+pr_id+"),"
                # f.write(return_string+"\n")       
                continue
            
            soup = extractor.get_soup(event)
            State = soup.select("#partial-discussion-header > div.d-flex.flex-items-center.flex-wrap.mt-0.gh-header-meta > div.flex-shrink-0.mb-2.flex-self-start.flex-md-self-center > span")[0]["title"].replace('Status: ','')
            if State != 'Merged':  
                # return_string = project+","+bug+",NOPR(NOMERGE"+pr_id+"),"
                # f.write(return_string+"\n")      
                continue

            print(project, bug, pr_id, data_key)            
            commit_url = "https://www.github.com/"+project+"/pull/"+pr_id+"/commits"
            print(commit_url)
            soup = extractor.get_soup(commit_url)
            # 여기서 merged commit 아니면 [] return
            commits = extractor.get_commits_from_pull(soup)
            print(commits)
            return_string = project+","+bug+","+pr_id+","+'|'.join(commits)
            # print(return_string)
            f.write(return_string+"\n")
        print()
        num_bugs = num_bugs+1
        f.close()
f.close()

print(already_bugNum)
print(num_bugs)
print(all_bugs)