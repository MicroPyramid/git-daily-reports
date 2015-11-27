import smtplib
from datetime import datetime, timedelta

from github import Github
from gitlab import Gitlab


def GitHub_Work_Log(username, password):
    g = Github(username, password)
    since = datetime.now() - timedelta(days=1)
    email = g.get_user().email
    work_log = ""

    for repo in g.get_user().get_repos():
        # To get merged commits log for User
        commits = repo.get_commits(since=since, author=username)
        count = sum([1 for c in commits])
        if count > 0:
            work_log += "Project Name: " + repo.name + '\n'

        # list all commits log for individual project.
        for commit in commits:
            work_log += commit.commit.message + '\n'

        # Get all Un-merged commits from pull requests
        pulls = repo.get_pulls()
        for p in pulls:
            if str(email) == str(p.user.email):
                if p.get_commits():
                    work_log += "Project Name: " + repo.name + '\n'
                    for commit in p.get_commits():
                        work_log += commit.commit.message + '\n'
    return work_log


def GitLab_Work_Log(url, token):
    gl = Gitlab(url, token)
    gl.auth()
    work_log = ''
    for project in gl.Project():
        work_log += "Project Name: " + project.name + '\n'
        for commit in project.Commit():
            if commit.author_email == gl.user.email:
                commited_at = datetime.strptime(commit.created_at[:19], '%Y-%m-%dT%H:%M:%S')
                if datetime.today().date()-timedelta(1) == commited_at.date():
                    work_log += commit.message + '\n'

        for merge in project.MergeRequest():
            if merge.author.id == gl.user.id:
                merged_at = datetime.strptime(merge.created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                if datetime.today().date()-timedelta(1) == merged_at.date():
                    work_log += merge.title + '\n'

    return work_log


def send_email(email, receivers, work_log):
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(email, receivers, work_log)
        print "Successfully sent email"
    except:
        print "Error: unable to send email"


if __name__ == '__main__':
    username = "GitHubUserName"
    password = "GitHubPassword"
    # ToDo Possible chenge Possword to Token
    gitHubLog = GitHub_Work_Log(username, password)

    url = 'yourGitLabURL'
    token = 'yourPrivateToken'
    GitLabLog = GitLab_Work_Log(url, token)

    email = "youremail@example.com"
    receivers = ['email@example.com']
    work_log = gitHubLog + GitLabLog
    send_email(email, receivers, work_log)
