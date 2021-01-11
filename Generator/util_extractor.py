# Author: Agness. Youngkoung Kim
import os
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import bs4
import time

class extractor:
    def __init__(self):
        pass

    def get_soup(self,url):
        #, headers = {'User-agent': 'your bot 0.1'}
        while True:
            html = requests.get(url, headers = {'User-agent': 'your bot 0.1'})
            if html.status_code==200:
                break
            time.sleep(3)
        bsObject = BeautifulSoup(html.text,"html.parser")
        return bsObject

    def get_blockinfo(self,comment):
        #writer
        try:
            writer= comment.find('a',attrs={'class':'author link-gray-dark css-truncate-target width-fit'}).text
        except:
            writer = '(ghost)'
        # comment ir issue
        isaddition = False
        if 'issuecomment-' in comment['id']:
            isaddition = True
        #writtentime
        time = comment.find('relative-time')['datetime']
        return isaddition,writer,time

    def ish(self,tag):
        if len(tag)>2:
            return False
        if tag=='h':
            return True
        if tag[0]=='h':
            if tag[1].isdigit:
                return True
        return False

    def gettext(self,children):
        content = []
        for child in children:
            # cf) https://github.com/explosion/spaCy/issues/1733 python version 
            if type(child)==bs4.element.NavigableString:
                content.append(child)
                continue
            grandchildren = list(child.children)
            dochild = False
            # head 일 경우
            if self.ish(child.name):
                combine = f"<denchmark-h:{child.name}>{child.text}</denchmark-h>\n"
                content.append(combine)
                continue

            # code인 경우
            if child.name=='pre':
                try:
                    text = child.find('code').text
                    text = f"<denchmark-code>{text}</denchmark-code>\n"
                    content.append(text)
                    continue
                except:
                    pass


            # link가 있는지 체크
            islink = False
            for item in grandchildren:
                if type(item)==bs4.element.Tag:
                    text = item.text
                    try:
                        link = item['href']
                        islink = True
                    except:
                        pass
            #link없는경우
            if not islink:
                content.append(child.text)
                continue
            # link있는경우
            else:
                tempcontent = ''
                for item in grandchildren:
                    if type(item)==bs4.element.NavigableString:
                        tempcontent+=item
                        continue
                    else:
                        try:
                            text = item.text
                            link = item['href']
                            combine = f"<denchmark-link:{link}>{text}</denchmark-link>\n"
                            tempcontent+=combine
                        except:
                            pass # tag만 있는 것들
                content.append(tempcontent)
        
        content = '\n'.join(content)
        return content

    def get_blockcontent(self,comment):
        # 내용
        content = comment.find('td')
        children = list(content.children)
        children = [x for x in children if x !='\n']
        content = self.gettext(children)
        #<denchmark-link:http:....>   </denchmark-link>
        return content

    def getonlytext(self,children):
        content = []
        for child in children:
            # cf) https://github.com/explosion/spaCy/issues/1733 python version 
            if type(child)==bs4.element.NavigableString:
                content.append(child)
                continue
            grandchildren = list(child.children)
            dochild = False
            # head 일 경우
            if self.ish(child.name):
                content.append(child.text)
                continue

            # code인 경우
            if child.name=='pre':
                try:
                    text = child.find('code').text
                    content.append(text)
                    continue
                except:
                    pass


            # link가 있는지 체크
            islink = False
            for item in grandchildren:
                if type(item)==bs4.element.Tag:
                    text = item.text
                    try:
                        link = item['href']
                        islink = True
                    except:
                        pass
            #link없는경우
            if not islink:
                content.append(child.text)
                continue
            # link있는경우
            else:
                tempcontent = ''
                for item in grandchildren:
                    if type(item)==bs4.element.NavigableString:
                        tempcontent+=item
                        continue
                    else:
                        try:
                            text = item.text
                            link = item['href']
                            
                            combine = content.append(text)
                            tempcontent+=combine
                        except:
                            pass # tag만 있는 것들
                content.append(tempcontent)
        
        content = '\n'.join(content)
        return content

    def get_blockcontent_onlytext(self,comment):
        # 내용
        content = comment.find('td')
        children = list(content.children)
        children = [x for x in children if x !='\n']
        content = self.getonlytext(children)
        #<denchmark-link:http:....>   </denchmark-link>
        return content

    def get_commentblocks(self,bsObject):
        commentblocks = bsObject.find_all('div',attrs={'class':'timeline-comment-group js-minimizable-comment-group js-targetable-element TimelineItem-body my-0'})
        return commentblocks

    def get_reporter(self,bsObject):
        reporters = bsObject.find_all('a', attrs={'class': 'author link-gray-dark css-truncate-target width-fit'})
        reporters_text = []
        for reporter in reporters:
            reporters_text.append(reporter.text)
        if len(reporters_text) == 0:
            reporters = bsObject.find_all('a', attrs={'class': 'author text-inherit'})    
            for reporter in reporters:
                reporters_text.append(reporter.text)
        #print(reporters_text)
        return reporters_text

    def get_summary(self,bsObject):
        summary = bsObject.find('span', attrs={'class': 'js-issue-title'}).text
        summary = summary.strip()
        return summary

    def get_Comment(self,bsObject):
        comments = bsObject.find_all('td', attrs={'class': 'd-block comment-body markdown-body js-comment-body'})
        comments_text = []
        comments_day = []
        for comment in comments:
            comments_text.append(comment.text)
            #comments_day.append(comment.text)
        #print(comments_day)
        #print(keyword, bug_id,  len(comments_day[0]), len(comments_day), len(comments_text))
        return comments_text

    def get_events(self,bsObject):
        events = bsObject.find_all('a', attrs={'data-hovercard-type': 'pull_request', 'class': 'link-gray-dark f4 text-bold'})
        event_text = []
        for event in events:
            event_text.append(event.text)
        events = [x['href'] for x in events]
        return events, event_text


    def get_commits_from_pull(self,soup):
        #soup = self.get_soup(url)
        State = soup.select("#partial-discussion-header > div.d-flex.flex-items-center.flex-wrap.mt-0.gh-header-meta > div.flex-shrink-0.mb-2.flex-self-start.flex-md-self-center > span")[0]["title"].replace('Status: ','')
        if State != 'Merged':
            return []
        commits = soup.find_all('a',attrs={"class":"text-mono f6 btn btn-outline BtnGroup-item"})
        commits = [x['href'] for x in commits]
        commit_ids = [x.split('/')[-1] for x in commits]
        return commit_ids
