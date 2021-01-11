
import os
import requests
from bs4 import BeautifulSoup
import time
import util_extractor 
import xml.etree.ElementTree as ET
import shutil


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

extractor = util_extractor.extractor()

lines = open("./data/stage2_bugreports/1st_candidate_bugs.csv", "r", encoding="utf8").readlines()
print("Target Bug Num: ",len(lines))
project_bugs = {}
for line in lines:
    line = line.replace("\n","")
    project = line.split(",")[0]
    bugid = line.split(",")[2]
    if project in project_bugs.keys():
        if bugid not in project_bugs[project]:            
            project_bugs[project].add(bugid)
    else:
        project_bugs[project] = set()
        project_bugs[project].add(bugid)

num_bugs = 0
all_bugs = 0
already_bugs = 0
absolute_path = "./data/stage2_bugreports/"
for project in project_bugs.keys():
    print(project)
    project_name = project.replace("/","+")
    path = absolute_path + project_name +"/"
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        print("Failed to create directory!")
        raise
    br2info = {} # 최 output
    bugs = project_bugs[project]
    for bugid in bugs:       
        bug = bugid
        all_bugs = all_bugs+1
        temp_path = "E:\\Misoo\\Denchmark_Dataset\\"+project_name+"\\bugs\\"+bugid+".xml"
        if os.path.isfile(temp_path):
            # print(path+bug+".xml ALREADY!")
            shutil.copyfile(temp_path,path+bugid+".xml")
            already_bugs+=1 
            continue
        if os.path.isfile(path+bugid+".xml"):
            # print(path+bug+".xml ALREADY!")
            already_bugs+=1 
            continue

        url = "https://github.com/"+project+"/issues/"+bugid
        # issue page 가져오기. 
        bsObject = None
        while True:
            print(url)
            html = requests.get(url, headers = {'User-agent': 'your bot 0.1'})
            bsObject = BeautifulSoup(html.text,"html.parser")
            # Rate limit handling
            if html.status_code!=429:
                break
            print("seelp for 5 sec...", project, bugid)
            time.sleep(5)
        assert bsObject != None

        # 가져올 정보
        author = None
        opentime = None
        closetime = None
        summary = None
        description = None  # [('text',~), ('code',~)] 이렇게 저장
        commentsnum = 0
        comments = {}
        # print(project, bug, url)
        
        summary = extractor.get_summary(bsObject) # 제목
        opentime = bsObject.select("#partial-discussion-header > div.d-flex.flex-items-center.flex-wrap.mt-0.gh-header-meta > div.flex-auto.min-width-0.mb-2 > relative-time")[0]['datetime']
        # 닫혔다 다시 열린 경우 마지막 닫힌 시간을 close time으로
        
        candidate = bsObject.find_all('div',attrs={"class":"TimelineItem-body"})
        candidate = [x for x in candidate if 'closed this' in x.text]
        # print(len(candidate))
        try:
            closetime = [x.find('relative-time')['datetime'] for x in candidate][-1]
        except:
            continue
        commentblocks = extractor.get_commentblocks(bsObject)
        for i,comment in enumerate(commentblocks):
            try:
                isaddition,writer,ctime = extractor.get_blockinfo(comment)
            except:
                continue
            content = extractor.get_blockcontent(comment)
            if isaddition:
                commentsnum+=1
                comments[i-1] = {'writer':writer,
                                 'time':ctime,
                                 'content':content
                                }
            else:
                author = writer
                description = content

        # BR ghost author 처리
        if author=='(ghost)':
            author = bsObject.find('a',attrs={"class":"author text-bold link-gray"}).text+author
        # print(summary)
        # print(description)
        # print(opentime,'~',closetime)
        # print(commentsnum)
        # print(author, len(commentblocks),'comments')
        assert author != None
        assert opentime is not None
        assert closetime is not None
        assert summary is not None
        assert content is not None

        br2info[bugid] = {'author':author,
                          'opentime':opentime,
                          'closetime':closetime,
                          'commentsnum':commentsnum,
                          'summary':summary,
                          'description':description,
                          'comments':comments
                         }
        # print()
        f = open(path+bugid+".xml", "w", encoding="utf8")
        f.write("<bug id='"+bug+"' author='"+author+"' open_date='"+opentime+"' closed_time='"+closetime+"'>\n")
        summary = summary.replace("<","&lt;").replace(">","&gt;")
        f.write("\t<summary>"+escape_cdata(summary)+"</summary>\n")
        f.write("\t<description>\n")
        description = escape_cdata(description)
        f.write(description+"\n")
        f.write("\t</description>\n")

        f.write("\t<comments>\n")
        
        for i,comment in enumerate(commentblocks):
            if i == 0: # is Description
                continue
            try:
                isaddition,writer,ctime = extractor.get_blockinfo(comment)
            except:
                continue
            content = extractor.get_blockcontent(comment)
            if isaddition:
                commentsnum+=1
                comments[i-1] = {'writer':writer,
                                 'time':ctime,
                                 'content':content
                                }
            else:
                author = writer
                description = content

            f.write("\t\t<comment id='"+str(i)+"' author='"+author+"' date='"+ctime+"'>\n")
            content = escape_cdata(content)
            f.write("\t\t"+content+"\n")
            f.write("\t\t</comment>\n")
        
        f.write("\t</comments>\n")
        f.write("</bug>")
        f.close()
        num_bugs = num_bugs +1
        # time.sleep(2)
    print(project+"\t"+str(num_bugs), already_bugs)
    num_bugs = 0
    already_bugs = 0


print(num_bugs, all_bugs)