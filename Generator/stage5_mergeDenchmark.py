import xml.etree.ElementTree as ET
import os

project_num = 0
bug_num = 0
base_entity_path = "./data/stage4_buggyEntities/"
base_bug_path = "./data/stage2_bugreports/"
absolute_path = "./data/final_dataset/full/"
projects = os.listdir("./data/stage4_buggyentities/")
for project in projects:
    project_num += 1  
    project_name = project.replace("/","+")

    folder_path = absolute_path + project_name +"/"
    try:
        if not(os.path.isdir(folder_path)):
            os.makedirs(os.path.join(folder_path))
    except OSError as e:
        print("Failed to create directory!")
        raise

    path = base_entity_path + project_name +"/"
    bug_path = base_bug_path + project_name +"/"
    bugs = os.listdir("./data/stage4_buggyentities/"+project+"/")
    for bug in bugs:                
        f = open(folder_path+bug, "w", encoding="utf8")
        
        f.write("<bug_data>\n")

        print(bug_path+bug)
        bug_f = open(bug_path+bug,"r",encoding="utf8")
        f.write(' '.join(bug_f.readlines()))
        f.write("\n")
        print(path+bug)
        bug_entity_f = open(path+bug,"r",encoding="utf8")
        f.write(' '.join(bug_entity_f.readlines()))

        f.write("</bug_data>\n")

        f.close()
        print(folder_path+bug)

        tree = ET.parse(folder_path+bug)
        bug_num += 1

print(project_num, bug_num)