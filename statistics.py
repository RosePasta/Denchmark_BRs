import os
import json
import numpy as np
import datetime
from github import Github
import requests
import time

target_languages  = ["javascript","python","java","go","c++","ruby","typescript","php","c#","c"]

frameworks = ['tensorflow','cntk','caffe','torch','mxnet','chainer','theano','org.deeplearning4j','paddle']

access_token = "aa115aac6951012f5a1ed2209ef86882801d41dd"
g = Github(access_token)

project_num = 0
all_bugs = 0
base_bug_path = "./JSonSet/simplejson/"
projects = os.listdir(base_bug_path)
language_num = []
topics_num = []
write_f = open("./report.csv", "a", encoding="utf8")
write_f.write('project,code-bug-num,bug-num,avgcomments,avgresolution,avgfiles,avgmethod,avglines,')
for framework in frameworks:
    write_f.write(framework+",")
for language in target_languages:
    write_f.write(language+",")
write_f.write('topics\n')
# write_f.close()
for project in projects:
    g = Github(access_token)
    print(g.get_rate_limit(), g.get_rate_limit().search, project, " loading..")
    repo = g.get_repo(project.replace("+","/"))
    languages = [language.lower() for language in repo.get_languages().keys() if language.lower() in target_languages]
    language_num.append(len(languages))
    topics = [topic for topic in repo.get_topics() if topic.lower() in frameworks]
    topics_num.append(len(topics))

    project_name = project.replace("/","+")
    bugs = os.listdir(base_bug_path+project+"/")

    used_frameworks = dict()
    for framework in frameworks:
        try:
            results = g.search_code("import "+framework+" repo:"+project.replace("+","/"))
            if results.totalCount > 0:
                used_frameworks[framework] = results.totalCount
            results = g.search_code("from "+framework+" repo:"+project.replace("+","/"))
            if results.totalCount > 0:
                used_frameworks[framework] = results.totalCount
        except:
            print(project, "PERMISSION? in github search code")
    time.sleep(60)

    # search_list = repo.search_code('import tensorflow')
    # print(search_list)
    code_bug_num = 0 
    bug_num = 0
    comment_num_list = []
    resolve_day_list = []
    m_file_num_list = []
    m_mth_num_list = []
    m_line_num_list = []
    for bug in bugs:        
        f = open(base_bug_path+project+"/"+bug)
        content = ' '.join(f.readlines())
        JSobject = json.loads(content)
        br_description = JSobject['BR']['BR_text']['BRdescription']
        if br_description.find("<denchmark-code>") > -1:
            code_bug_num += 1
        bug_num += 1
        comment_num_list.append(len(JSobject['BR']['comments']))

        open_date = datetime.datetime.strptime(JSobject['BR']['BRopenT'], "%Y-%m-%dT%H:%M:%SZ")
        closed_date = datetime.datetime.strptime(JSobject['BR']['BRcloseT'], "%Y-%m-%dT%H:%M:%SZ")
        diff_date = closed_date - open_date
        resolve_day_list.append(diff_date.days)

        commit_files = JSobject['commit']['changed_files']
        modif_file_num = 0
        modif_mth_num = 0
        modif_lines = set()
        for commit_file in commit_files:
            if commit_files[commit_file]['file_change_type'] == "MODIFY":
                modif_file_num += 1
                modif_mth_num += commit_files[commit_file]['file_Nmethod']
                hunks = commit_files[commit_file]['hunks']
                for hunk in hunks:
                    if hunks[hunk]['added_lines'] is not None:
                        modif_lines = modif_lines | set(hunks[hunk]['added_lines'].split(","))
                    if hunks[hunk]['deleted_lines'] is not None:
                        modif_lines = modif_lines | set(hunks[hunk]['deleted_lines'].split(","))
        
        m_file_num_list.append(modif_file_num)
        m_mth_num_list.append(modif_mth_num)
        m_line_num_list.append(len(modif_lines))
    avg_comments =  np.array(comment_num_list).mean()
    avg_resolution = np.array(resolve_day_list).mean()
    avg_m_file = np.array(m_file_num_list).mean()
    avg_m_mth = np.array(m_mth_num_list).mean()
    avg_m_line = np.array(m_line_num_list).mean()
    # print(project, len(used_frameworks), len(languages), len(topics), code_bug_num, bug_num, avg_comments, avg_resolution, avg_m_file, avg_m_mth, avg_m_line)
    print(project+","+str(code_bug_num)+","+str(bug_num)+","+str(avg_comments)+","+str(avg_resolution)+","+str(avg_m_file)+","+str(avg_m_mth)+","+str(avg_m_line)+",")
    write_f.write(project+","+str(code_bug_num)+","+str(bug_num)+","+str(avg_comments)+","+str(avg_resolution)+","+str(avg_m_file)+","+str(avg_m_mth)+","+str(avg_m_line)+",")
    
    for framework in frameworks:
        if framework in used_frameworks.keys():
            write_f.write("O,")
        else:
            write_f.write("X,")

    for language in target_languages:
        if language in languages:
            write_f.write("O,")
        else:
            write_f.write("X,")
    write_f.write('|'.join(topics)+"\n")
    all_bugs += bug_num
    project_num += 1  
print(project_num, all_bugs)
print(np.array(language_num).mean(), np.array(topics_num).mean())
write_f.close()