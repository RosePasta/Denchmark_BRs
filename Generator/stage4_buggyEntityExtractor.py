import datetime
from datetime import timedelta
import xml.etree.ElementTree as ET
from pydriller import RepositoryMining
from git import GitCommandError
import os
import sys
sys.setrecursionlimit(10000)

def escape_cdata(text):
    # # escape character data
    try:
        if not text.startswith("<![CDATA[") and not text.endswith("]]>"):
            if "&" in text:
                text = text.replace("&", "&amp;")
            if "<" in text:
                text = text.replace("<", "&lt;")
            if ">" in text:
                text = text.replace(">", "&gt;")                
        return text
    except (TypeError, AttributeError):
        ET._raise_serialization_error(text)

git_absolute_path = "E:\\Misoo\\Denchmark_GitRepositories\\"
f = open("./data/stage3_groundtruths/3rd_candidate_bugs_linked_commits_filtered2.csv", "r", encoding="utf8")
project_bug_commit_map = {}
lines = f.readlines()
min_commit_id = 999
max_commit_id = 0
project_commits = {}
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

    if project in project_commits.keys():
        project_commits[project].add(commit_id)
    else:
        project_commits[project] = set()
        project_commits[project].add(commit_id)

bug_num = 0
for project in project_bug_commit_map.keys():
    for bug in project_bug_commit_map[project].keys():
        bug_num += 1

print(bug_num, len(project_bug_commit_map))

absolute_path = "./data/stage4_buggyEntities/"
for project in project_bug_commit_map.keys():    
    project_name = project.replace("/","+")
    path = absolute_path + project_name +"/"
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        print("Failed to create directory!")
        raise
    git_path = git_absolute_path + project.replace("/","+")
    git_path = git_path +"\\"+project.replace("/","+").split("+")[1]
    commits = project_commits[project]

    for bug in project_bug_commit_map[project].keys():
        if os.path.isfile(path+bug+".xml") is True:
            print(path+bug+".xml ALREADY")
            continue
        f = open(path+bug+".xml", "w", encoding="utf8")
        for commit_id in project_bug_commit_map[project][bug]:
            for commit in RepositoryMining(git_path, single=commit_id).traverse_commits():
                print(project,bug, commit_id)
                f.write("<commit id='"+commit_id+"' author='"+escape_cdata(commit.author.name).replace("'","")+"' date='"+str(commit.committer_date)+"'>\n")
                try:
                    f.write("\t<dmm_unit complexity='"+str(commit.dmm_unit_complexity)+"' interfacing='"+str(commit.dmm_unit_interfacing)+"' size='"+str(commit.dmm_unit_size)+"'></dmm_unit>\n")
                    print(project, bug, commit.hash, commit.dmm_unit_complexity, len(commit.modifications), commit.dmm_unit_interfacing, commit.dmm_unit_size)
                except MemoryError:
                    f.write("\t<dmm_unit complexity='None' interfacing='None' size='None'></dmm_unit>\n")
                for modification in commit.modifications:
                    f.write("\t<modification change_type='"+modification.change_type.name+"' old_name='"+str(modification.old_path)+"' new_name='"+str(modification.new_path)+"'>\n")
                    f.write("\t\t<file_info nloc='"+str(modification.nloc)+"' complexity='"+str(modification.complexity)+"' token_count='"+str(modification.token_count)+"'></file_info>\n")
                    print("\tM-OLD\t", project, commit.hash, modification.change_type.name, modification.nloc, modification.complexity, modification.token_count, modification.old_path)
                    print("\tM-NEW\t", project, commit.hash, modification.change_type.name, modification.nloc, modification.complexity, modification.token_count, modification.new_path)
                    diff_parses = modification.diff_parsed
                    change_type = modification.change_type.name
                    if change_type =="MODIFY":
                        added_lines = []
                        for diff_lines in diff_parses['added']:
                            added_lines.append(str(diff_lines[0]))
                        deleted_lines = []
                        for diff_lines in diff_parses['deleted']:
                            deleted_lines.append(str(diff_lines[0]))
                        filtered_lines  = []
                        for method in modification.changed_methods:
                            print("\t\tMETHOD\t",method.name,method.parameters)
                            f.write("\t\t<method name='"+escape_cdata(method.name)+"' parameters='"+escape_cdata(','.join(method.parameters))+"'>\n")
                            f.write("\t\t\t\t<method_info nloc='"+str(method.nloc)+"' complexity='"+str(method.complexity)+"' token_count='"+str(method.token_count)+"' nesting_level='"+str(method.top_nesting_level)+"' start_line='"+str(method.start_line)+"' end_line='"+str(method.end_line)+"'></method_info>\n")
                            start_line = method.start_line
                            end_line = method.end_line                            
                            f.write("\t\t\t<added_lines>")
                            method_line_list =[]
                            for added_line in added_lines:
                                if int(added_line) >= start_line and end_line >= int(added_line):
                                    method_line_list.append(added_line)
                                    filtered_lines.append(added_line)
                            f.write(",".join(method_line_list)+"</added_lines>\n")                          

                            f.write("\t\t\t<deleted_lines>")
                            method_line_list =[]
                            for deleted_line in deleted_lines:
                                if int(deleted_line) >= start_line and end_line >= int(deleted_line):
                                    method_line_list.append(deleted_line)
                                    filtered_lines.append(deleted_line)
                            f.write(",".join(method_line_list)+"</deleted_lines>\n")
                            f.write("\t\t</method>\n")
    
                        f.write("\t\t<modified_lines>\n")                                            
                        f.write("\t\t\t<added_lines>")
                        method_line_list =[]
                        for added_line in added_lines:
                            if added_line not in filtered_lines:
                                method_line_list.append(added_line)
                        f.write(",".join(method_line_list)+"</added_lines>\n")       
                                          
                        f.write("\t\t\t<deleted_lines>")
                        method_line_list =[]
                        for deleted_line in deleted_lines:
                            if deleted_line not in filtered_lines:
                                method_line_list.append(deleted_line)
                        f.write(",".join(method_line_list)+"</deleted_lines>\n")       

                        f.write("\t\t</modified_lines>\n")     
                        print("\t\t\tADD_LINE\t",','.join(added_lines))
                        print("\t\t\tDEL_LINE\t",','.join(deleted_lines))
                    
                    f.write("\t</modification>\n")
                f.write("</commit>\n")
        f.close()



project_num = 0
bug_num = 0
base_bug_path = "./data/stage2_bugreports/"
projects = os.listdir("./data/stage4_buggyentities/")
for project in projects:
    project_num += 1  
    project_name = project.replace("/","+")
    path = absolute_path + project_name +"/"
    bug_path = base_bug_path + project_name +"/"
    bugs = os.listdir("./data/stage4_buggyentities/"+project+"/")
    for bug in bugs:        
        print(path+bug)
        tree = ET.parse(path+bug)  
        print(bug_path+bug)
        tree = ET.parse(bug_path+bug)
        bug_num += 1

print(project_num, bug_num)