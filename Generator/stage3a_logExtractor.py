
import os
import requests
from bs4 import BeautifulSoup
import time
import util_extractor 
extractor = util_extractor.extractor()
import subprocess
import sys
import re

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


def cmd(command):
    command = 'cmd /u /c '+command
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    result = p.communicate()
    text = result[0]
    text = text.decode('utf-8',errors='ignore')    
    if len(text)>1:
        return text.split('\n')
    else:
        return []


project_bugs, bug_num = load_projects()
print(len(project_bugs), bug_num)

f = open("./data/stage3_groundtruths/1st_candidate_bugs_with_logs.csv", "r", encoding="utf8")
lines = f.readlines()
already_set = set()
for line in lines:
    project = line.split(",")[0].lower()
    bug_id = line.split(",")[1]
    already_set.add(project+"-"+bug_id)

os.environ['PYTHONIOENCODING'] = 'utf-8'
pattern = re.compile(r'^[ 0-9]+$')
buggy_keywords = ['fix','bug','error','crash','#']
absolute_path = "E:\\Misoo\\Denchmark_GitRepositories\\"
f = open("./data/stage3_groundtruths/1st_candidate_bugs_with_logs.csv", "a", encoding="utf8")
allbug = 0
for project in project_bugs.keys():
    os.chdir("E:\\Misoo\\Python_workspace\\Denchmark\\")
    path = absolute_path + project.replace("/","+")
    if os.path.isdir(path) is False:        
        os.makedirs(path)
        os.chdir(path)
        result = cmd("git clone http://github.com/"+project)
        print("FINISH to clone the repository", project)
    
    bug_list = project_bugs[project]
    path = path +"\\"+project.split("/")[1]

    os.chdir(path)
    
    p = subprocess.Popen("cmd /u /c git checkout master", stdout=subprocess.PIPE)
    result = p.communicate()   
    # print(result)     
    for bug_id in bug_list:
        identifier = project+'-'+bug_id
        if identifier in already_set:
            print(identifier, "ALREADY")
            continue
        # time.sleep(5)
        # Get Commit having the bugID as text
        commit_list = cmd("git log --all --name-status --pretty=format:%h%x09%an%x09%ad%x09%s --grep \""+bug_id+"\"")
        commit_ids = []
        commit_id_files = {}
        commit_id_date = {}
        commit_id_text = {}
        commit_text_id = {}
        commit_messages = {}
        prev_commit = ""
        prev_commit_date = ""
        prev_commit_summary = ""
        fixed_files = []
        for commit_text in commit_list:
            if len(commit_text.replace(" ","")) < 2:
                # Get Commit Message
                commit_message= ' '.join(cmd("git show -s --format=%B "+prev_commit))
                commit_messages[prev_commit] = commit_message
                commit_id_files[prev_commit] = fixed_files
                commit_id_date[prev_commit] = prev_commit_date
                commit_id_text[prev_commit] = prev_commit_summary
                commit_text_id[prev_commit_summary] = prev_commit
                commit_ids.append(prev_commit)
                prev_commit = ""
                prev_commit_date = ""
                prev_commit_summary = ""
                fixed_files = []
                continue
            if len(prev_commit) == 0:
                prev_commit = commit_text.split("\t")[0]
                prev_commit_date = commit_text.split("\t")[2]
                prev_commit_summary = commit_text.split("\t")[3]
            else:
                file_type = commit_text.split("\t")[0]
                if file_type =="M":
                    fixed_files.append(commit_text.replace("\n","").split("\t")[1])      
        
        # Only selecting the commit having buggy-keywords and exact number of bug id
        # print(bug_id, len(commit_list))
        for commit in commit_ids:
            flag = False
            body = commit_messages[commit]
            for key in buggy_keywords:                
                if body.lower().find(key) > -1:
                    numbers = re.findall(r"\d+", body)
                    for result in numbers:
                        if str(result) == bug_id:
                            # print(bug_id, key, numbers, result, body)
                            flag = True
                            break
            if flag is False:
                continue
            print(project+","+bug_id+","+commit)
            f.write(project+","+bug_id+","+commit+"\n")
f.close()