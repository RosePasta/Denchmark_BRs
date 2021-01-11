import datetime
from datetime import timedelta
import xml.etree.ElementTree as ET
from pydriller import RepositoryMining
from git import GitCommandError
import os
git_absolute_path = "E:\\Misoo\\Denchmark_GitRepositories\\"

# f = open("./data/stage3_groundtruths/1st_candidate_bugs_with_logs.csv", "r", encoding="utf8")
# project_bug_commit_map = {}
# lines = f.readlines()
# min_commit_id = 999
# max_commit_id = 0
# for line in lines:
#     tokens = line.replace("\n","").split(",")
#     project = tokens[0].lower()
#     bug_id = tokens[1]
#     commit_id = tokens[2]

#     if project in project_bug_commit_map.keys():
#         if bug_id in project_bug_commit_map[project].keys():            
#             project_bug_commit_map[project][bug_id].add(commit_id)
#         else:
#             project_bug_commit_map[project][bug_id] = set()
#             project_bug_commit_map[project][bug_id].add(commit_id)            
#     else:
#         project_bug_commit_map[project] = {}
#         project_bug_commit_map[project][bug_id] = set()
#         project_bug_commit_map[project][bug_id].add(commit_id)

# bug_num = 0
# for project in project_bug_commit_map.keys():
#     for bug in project_bug_commit_map[project].keys():
#         bug_num += 1

# print(bug_num, len(project_bug_commit_map))

# f = open("./data/stage3_groundtruths/1st_candidate_bugs_with_pr_logs.csv", "r", encoding="utf8")
# lines = f.readlines()
# for line in lines:
#     tokens = line.replace("\n","").split(",")
#     project = tokens[0].lower()
#     bug_id = tokens[1]
#     commit_ids = tokens[3].split("|")

#     if project in project_bug_commit_map.keys():
#         if bug_id in project_bug_commit_map[project].keys():     
#             for commit_id in commit_ids:
#                 # for commit in RepositoryMining(git_path, single=commit_id).traverse_commits():
#                 #     commit_id = commit.hash
#                 project_bug_commit_map[project][bug_id].add(commit_id)
#         else:
#             project_bug_commit_map[project][bug_id] = set()
#             for commit_id in commit_ids:                
#                 # for commit in RepositoryMining(git_path, single=commit_id).traverse_commits():
#                 #     commit_id = commit.hash
#                 project_bug_commit_map[project][bug_id].add(commit_id)            
#     else:
#         project_bug_commit_map[project] = {}
#         project_bug_commit_map[project][bug_id] = set()
#         for commit_id in commit_ids:
#             project_bug_commit_map[project][bug_id].add(commit_id)

# bug_num = 0
# commit_num = 0
# for project in project_bug_commit_map.keys():
#     for bug in project_bug_commit_map[project].keys():
#         bug_num += 1
#         commit_num += len(project_bug_commit_map[project][bug])

# print(bug_num, len(project_bug_commit_map), commit_num)

# # A. Linking Bug-Commit
# f = open("./data/stage3_groundtruths/2nd_candidate_bugs_linked_commits.csv", "w", encoding="utf8")
# avg_commit_num = 0
# bug_num = 0

# for project in project_bug_commit_map.keys():
#     git_path = git_absolute_path + project.replace("/","+")
#     git_path = git_path +"\\"+project.replace("/","+").split("+")[1]
#     for bug in project_bug_commit_map[project].keys():
#         bug_num += 1
#         for commit in project_bug_commit_map[project][bug]:
#             for commit_id in RepositoryMining(git_path, single=commit).traverse_commits():
#                 commit = commit_id.hash
#             f.write(project+","+bug+","+commit+"\n")
#         avg_commit_num += len(project_bug_commit_map[project][bug])
#         print(project, bug, len(project_bug_commit_map[project][bug]))

# f.close()
# print(avg_commit_num / bug_num)


# B.1. Filtering commit based on commit date, num of commits, and commit type (changes)
f = open("./data/stage3_groundtruths/2nd_candidate_bugs_linked_commits.csv", "r", encoding="utf8")
project_bug_commit_map = {}
lines = f.readlines()
min_commit_id = 999
max_commit_id = 0
for line in lines:
    tokens = line.replace("\n","").split(",")
    project = tokens[0].lower()
    bug_id = tokens[1]
    commit_id = tokens[2]

    if project in project_bug_commit_map.keys():
        if bug_id in project_bug_commit_map[project].keys():            
            project_bug_commit_map[project][bug_id].add(commit_id)
        else:
            project_bug_commit_map[project][bug_id] = set()
            project_bug_commit_map[project][bug_id].add(commit_id)            
    else:
        project_bug_commit_map[project] = {}
        project_bug_commit_map[project][bug_id] = set()
        project_bug_commit_map[project][bug_id].add(commit_id)

# f = open("./data/stage3_groundtruths/3rd_candidate_bugs_linked_commits_filtered1.csv", "w", encoding="utf8")
all_bugs = 0
commit_num = 0
bug_num = 0
two_commit_bugs = 0
no_modif_commit_bugs = 0
no_during_date_bugs = 0
for project in project_bug_commit_map.keys():
    git_path = git_absolute_path + project.replace("/","+")
    git_path = git_path +"\\"+project.replace("/","+").split("+")[1]
    for bug in project_bug_commit_map[project].keys():
        bug_id = bug
        all_bugs += 1
        if len(project_bug_commit_map[project][bug_id]) > 1:
            two_commit_bugs += 1
            print(project, bug_id, len(project_bug_commit_map[project][bug_id]) , "ONE MORE COMMITS")
            continue

        bug_path ="./data/stage2_bugreports/"+project.replace("/","+")+"/"+bug_id+".xml"
        if os.path.isfile(bug_path) is False:
            print(bug_path, "NO BUG FILE!")
            continue
        tree = ET.parse(bug_path)
        root = tree.getroot()

        open_date_text = root.attrib['open_date'].split("T")[0].split("-")
        bug_open_date = datetime.datetime.strptime((open_date_text[0])+"-"+(open_date_text[1])+"-"+(open_date_text[2]), '%Y-%m-%d')

        closed_date_text = root.attrib['closed_time'].split("T")[0].split("-")
        bug_closed_date = datetime.datetime.strptime((closed_date_text[0])+"-"+(closed_date_text[1])+"-"+(closed_date_text[2]), '%Y-%m-%d')
        
        target_commits = set()
        for commit_id in project_bug_commit_map[project][bug_id]:
            print(project+","+bug+","+commit_id+"\n")
            try:
                flag = False
                commit_date = None
                for commit in RepositoryMining(git_path, single=commit_id).traverse_commits():
                    commit_date = commit.committer_date
                    commit_date = datetime.datetime.strptime(str(commit_date.year)+"-"+str(commit_date.month)+"-"+str(commit_date.day), '%Y-%m-%d')
                    for modification in commit.modifications:
                        if modification.change_type.name =="MODIFY":
                            flag = True
                            break
                    if flag is True:
                        break                
                
                # 2. Filtering the out of bug resolution date
                if flag is True:                                        
                    if bug_open_date <= commit_date and commit_date <= bug_closed_date:
                        target_commits.add(commit_id)
                    else:
                        print(project, bug_id, commit_id, bug_open_date, commit_date, bug_closed_date , "INVALUD DATE")
                        no_during_date_bugs += 1
                else:
                    print(project, bug_id, commit_id, "NO MODIF COMMIT")
                    no_modif_commit_bugs += 1

            except (ValueError, OSError, GitCommandError) as e:
                print("NO ", project,  bug, commit_id)
                continue
        
        if len(target_commits) > 0:
            for commit in target_commits:
                # f.write(project+","+bug+","+commit+"\n")
                print(project+","+bug+","+commit+"\n")
                commit_num +=1 
            bug_num += 1

# f.close()
print(all_bugs, bug_num, commit_num, two_commit_bugs, no_modif_commit_bugs, no_during_date_bugs)



# # B.2. Filtering Bug-Commit mentioned with other bugs
# f = open("./data/stage3_groundtruths/3rd_candidate_bugs_linked_commits_filtered1.csv", "r", encoding="utf8")
# project_bug_commit_map = {}
# lines = f.readlines()
# min_commit_id = 999
# max_commit_id = 0
# for line in lines:
#     tokens = line.replace("\n","").split(",")
#     project = tokens[0].lower()
#     bug_id = tokens[1]
#     commit_id = tokens[2]

#     if project in project_bug_commit_map.keys():
#         if bug_id in project_bug_commit_map[project].keys():            
#             project_bug_commit_map[project][bug_id].add(commit_id)
#         else:
#             project_bug_commit_map[project][bug_id] = set()
#             project_bug_commit_map[project][bug_id].add(commit_id)            
#     else:
#         project_bug_commit_map[project] = {}
#         project_bug_commit_map[project][bug_id] = set()
#         project_bug_commit_map[project][bug_id].add(commit_id)

# bug_num = 0
# for project in project_bug_commit_map.keys():
#     for bug in project_bug_commit_map[project].keys():
#         bug_num += 1
# print(bug_num, len(project_bug_commit_map))

# f = open("./data/stage3_groundtruths/3rd_candidate_bugs_linked_commits_filtered2.csv", "w", encoding="utf8")
# new_all_bugs = 0
# multi_commit_bug_num = 0
# for project in project_bug_commit_map.keys():    
#     # Filtering the multi-bug-mentioned commits
#     # BUGSJS: A Benchmark of JavaScript Bug, ICST'19
#     # - Refer the Bug Isolation
#     commit_bug_map = {}
#     for bug_id in project_bug_commit_map[project].keys():
#         for commit_id in project_bug_commit_map[project][bug_id]:
#             if commit_id in commit_bug_map.keys():
#                 commit_bug_map[commit_id].add(bug_id)
#             else:
#                 commit_bug_map[commit_id] = set()
#                 commit_bug_map[commit_id].add(bug_id)
#     filtered_bugs = set()
#     for commit_id in commit_bug_map.keys():
#         if len(commit_bug_map[commit_id]) > 1:
#             for bug_id in commit_bug_map[commit_id]:
#                 filtered_bugs.add(bug_id)
#     multi_commit_bug_num += len(filtered_bugs)


#     git_path = git_absolute_path + project.replace("/","+")
#     git_path = git_path +"\\"+project.replace("/","+").split("+")[1]
#     for bug_id in project_bug_commit_map[project].keys():
#         # Filtering the multi-bug-mentioned commits
#         if bug_id in filtered_bugs:
#             continue
        
#         target_commits = set()
#         for commit_id in project_bug_commit_map[project][bug_id]:
#             f.write(project+","+bug_id+","+commit_id+"\n")
#             new_all_bugs += 1

# f.close()
    


# print(all_bugs, bug_num, commit_num, two_commit_bugs, no_modif_commit_bugs, no_during_date_bugs)
# print(new_all_bugs, multi_commit_bug_num)