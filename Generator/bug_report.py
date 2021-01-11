class BugReport:
    bugid = ""
    author = ""
    opened = ""
    closed = ""
    summary = ""
    description = ""
    comments = {}   
    commits = {}   


    def __init__(self, bugid, author, opened, closed, summary, description, comments,commits):
        self.bugid = bugid
        self.author = author
        self.opened = opened
        self.closed = closed
        self.summary = summary
        self.description = description
        self.comments = comments
        self.commits = commits
        pass

    def getValues(self):
        return self.bugid, self.author, self.opened, self.closed, self.summary, self.description, self.comments, self.commits