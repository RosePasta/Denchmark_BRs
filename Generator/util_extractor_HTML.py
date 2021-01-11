import os
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup

class extractor:
    def __init__(self):
        pass

    def get_soup(self,url):
        #, headers = {'User-agent': 'your bot 0.1'}
        html = requests.get(url, headers = {'User-agent': 'your bot 0.1'}).text
        bsObject = BeautifulSoup(html,"html.parser")
        return bsObject

    def check_commit(self,bsObject):
        check = bsObject.select("#js-repo-pjax-container > div.container-xl.clearfix.new-discussion-timeline.px-3.px-md-4.px-lg-5 > div > div.commit.full-commit.mt-0.px-2.pt-2 > span > details > summary > svg")
        if len(check)==0:
            return 'none'
        elif 'octicon-check' in check[0]['class']:
            return 'check'
        elif 'octicon-x' in check[0]['class']:
            return 'error'
        elif 'octicon-dot-fill' in check[0]['class']:
            return 'yet'
        else:
            print('CHECK!!!')
            return check[0]['class'][1]

    def get_author(self,bsObject):
        author = bsObject.select("#js-repo-pjax-container > div.container-xl.clearfix.new-discussion-timeline.px-3.px-md-4.px-lg-5 > div > div.commit.full-commit.mt-0.px-2.pt-2 > div.commit-meta.p-2.d-flex.flex-wrap > div.AvatarStack.flex-self-start > div")[0]['aria-label']

        return author
        # try:
        #     author = bsObject.select("#js-repo-pjax-container > div.container-xl.clearfix.new-discussion-timeline.px-3.px-md-4.px-lg-5 > div > div.commit.full-commit.mt-0.px-2.pt-2 > div.commit-meta.p-2.d-flex.flex-wrap > div.flex-self-start.no-wrap.mr-md-4.mr-0 > a")[0]['href']
        #     author = author.split('author=')[-1]
        # except:
        #     author = bsObject.select("#js-repo-pjax-container > div.container-xl.clearfix.new-discussion-timeline.px-3.px-md-4.px-lg-5 > div > div.commit.full-commit.mt-0.px-2.pt-2 > div.commit-meta.p-2.d-flex.flex-wrap > div.flex-self-start.no-wrap.mr-md-4.mr-0 > span")[0].text
        
        # return author

    # Rose: get only modified files
    def get_fixedfiles(self,bsObject):
        fixedTypes = bsObject.select("#toc > ol > li > svg[title]")
        fTypeList = []
        for fType in fixedTypes:            
            title = fType['title']
            fTypeList.append(title)

        fixedfile = bsObject.select("#toc > ol > li > a")
        fixedfile = [x.text for x in fixedfile]
        newFixedFile = []
        for i, fileName in enumerate(fixedfile):
            if fTypeList[i] == "modified":
                newFixedFile.append(fileName)
        return newFixedFile

    def get_reporter(self,bsObject):
        reporters = bsObject.find_all('a', attrs={'class': 'author link-gray-dark css-truncate-target width-fit'})
        reporters_text = []
        for reporter in reporters:
            reporters_text.append(reporter.text)
        if len(reporters_text) == 0:
            reporters = bsObject.find_all('a', attrs={'class': 'author text-inherit'})    
            for reporter in reporters:
                reporters_text.append(reporter.text)
        print(reporters_text)

    def get_date(self,bsObject):
        # 전처리 없이 raw로 가져옴
        date = bsObject.find('relative-time')
        if date is None:
            return ""
        return date.text

    def get_summary(self,bsObject):
        # 전처리 없이 raw로 가져옴
        summary = bsObject.find('span', attrs={'class': 'js-issue-title'}).text
        return summary

    def get_Comment(self,bsObject):
        comments = bsObject.find_all('td', attrs={'class': 'd-block comment-body markdown-body js-comment-body'})
        comments_text = []
        for comment in comments:
            comments_text.append(comment.text)
        return comments_text

    def get_events(self,bsObject):
        events = bsObject.find_all('a', attrs={'data-hovercard-type': 'pull_request', 'class': 'link-gray-dark f4 text-bold'})
        event_text = []
        for event in events:
            event_text.append(event.text)
        events = [x['href'] for x in events]
        return events, event_text

    # def get_commits_from_pull(self,url):
    #     soup = extractor.get_soup(url)
    #     State = soup.select("#partial-discussion-header > div.d-flex.flex-items-center.flex-wrap.mt-0.gh-header-meta > div.flex-shrink-0.mb-2.flex-self-start.flex-md-self-center > span")[0]["title"].replace('Status: ','')
    #     if State != 'Merged':
    #         return []
    #     commits = soup.find_all('a',attrs={"class":"text-mono f6 btn btn-outline BtnGroup-item"})
    #     commits = [x['href'] for x in commits]
    #     commit_ids = [x.split('/')[-1] for x in commits]
    #     return commit_ids
