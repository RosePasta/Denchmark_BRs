# Author: Misoo Kim, Youngkyoun Kim

from github import Github
import datetime
import calendar
from urllib.request import urlopen
from bs4 import BeautifulSoup

frameworks = ['tensorflow','keras','cntk','caffe','caffe2','torch','pytorch','mxnet','chainer','theano','deeplearning4j','dl4j','paddlepaddle','paddle']

# https://machinelearningmastery.com/a-tour-of-machine-learning-algorithms/
frameworks += ['deep-learning','deep-neural-network','deep-reinforcement-learning','deep-q-learing','convolution-neural-network','recurrent-neural-network','deep-belief-network','long-short-term-memory-networks','deep-boltzmann-machine']
# frameworks += ['dnn','drl','dql','cnn','rnn','dbn','lstm','dbm']


# Based on https://madnight.github.io/githut/#/pull_requests/2020/3 
# Selecting the programming languages in Top-10
target_languages  = ["javascript","python","java","go","c++","ruby","typescript","php","c#","c"]

date_criteria = datetime.datetime(2020, 1, 1)

access_tokens = [ "eb70e3bb56fb272e26cb94810a5c18a87a7beaab", "69c6b06d66e7af6943f3058266587935278ad901"]
token_id = 0
g = Github(access_tokens[token_id])

project_names = set()
project_file_path = "./data/stage1_projects/"
f = open(project_file_path+"1st_candidate_projects.csv", 'w', encoding='utf8')
for framework in frameworks:    
    print(g.get_rate_limit(), framework, " loading..")
    repositories = g.search_repositories(query='topic:'+framework, sort='stars',order ='desc')    
    i = 0    
    for repo in repositories:        
        if str(repo.full_name).lower() in project_names:
            continue
        num_stars = repo.stargazers_count
        num_forks = repo.forks_count
        if num_stars < 100:
            break

        # 2. Filtering no-issue projects
        if repo.has_issues == False:
            continue
        
        # 3. Get languages and Skip no-target-programing-language-based repo
        languages = [language for language in repo.get_languages().keys() if language in target_languages]
        if len(languages) == 0:
            continue

        # 5. Get lasted commit and skip no commit during 1 year.
        lasted_commit_date = repo.get_commits()[0].commit.author.date
        if lasted_commit_date < date_criteria:
            continue

        # 6. Count bug reports and Skip repo when num_bug reports is lower than 100.
        labels = repo.get_labels()
        bug_labels = [label for label in labels if str(label).lower().find('bug') > -1]
        num_closed_brs = 0
        for bug_label in bug_labels:
            issues = repo.get_issues(state='closed', labels=[bug_label])
            num_closed_brs += issues.totalCount        
        if num_closed_brs < 10:
            continue
        
        print(framework, i, repo.full_name, languages, num_stars, num_forks, num_closed_brs)
        f = open(project_file_path+"1st_candidates.csv", 'a')
        f.write(repo.full_name+","+str(num_stars)+","+str(num_closed_brs)+"\n")
        f.close()

        project_names.add(str(repo.full_name).lower())
        i +=1
    print(framework, i)

