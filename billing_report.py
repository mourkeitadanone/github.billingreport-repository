#!/usr/bin/python
# coding: utf8

'''
The class tests Github API
- authentication
- List users
- List repos
- List teams and members
- Show billing report
'''

import json
import requests

from github import Github


ORGANIZATION = 'danone'
ORGANIZATION_ID = 45825739
GITHUB_ADMINS_TEAM_ID = 3464005

def getToken():
    try:
        f = open('github-dev-token.txt')
        token = f.read()
        return token
    except:
        return ''

def getDanoneTeams():
    org = g.get_organization(ORGANIZATION)
    teams = org.get_teams()
    for team in teams:
        print(team.get_members)

g = Github(getToken())


class MyGithub:
    githubUrl = 'https://api.github.com'
    headers = {'accept': 'application/json',
               'content-type': 'application/json',
               'Authorization': 'token {}'.format(getToken())}

    def authentication(self):
        req = requests.post(self.githubUrl+'/user', headers=self.headers)
        return req

    def getRepositories(self):
        data = {'type':'all'}
        req = requests.get(self.githubUrl + '/orgs/danone/repos', headers=self.headers, data=data)
        return req

    def getTeams(self, path):
        req = requests.get(self.githubUrl + path, headers=self.headers)
        return req

    def getTeamsPagination(self, req):
        total_pages = req.links['last']['url'].split('page=')[1]
        return total_pages


    def getTeamMembers(self, team_id):
        members = requests.get(
            self.githubUrl + '/organizations/' + str(ORGANIZATION_ID) + '/team/' + str(team_id) + '/members',
            headers=self.headers).json()
        return members

    def getMembers(self):
        all_teams_req = self.getTeams('/orgs/danone/teams')
        teams_list, cpt = [], 0
        total_teams_pages = int(self.getTeamsPagination(all_teams_req))
        for page in range(total_teams_pages):
            teams = self.getTeams('/orgs/danone/teams?page={}'.format(page + 1))
            for team in teams.json():
                danone_gh_team = DanoneGithubTeam()
                danone_gh_team.setTeamInfos(team['name'], team['id'], team['description'])
                members = self.getTeamMembers(team['id'])
                danone_gh_team.billing = 250 * len(members)
                for cpt in range(len(members)):
                    danone_gh_member = DanoneGithubMember()
                    member_email = self.getUserEmail(members[cpt]['login'])
                    danone_gh_member.setGithubMemberInfos(members[cpt]['id'], members[cpt]['login'], member_email)
                    danone_gh_team.addMemberInList(danone_gh_member)
                teams_list.append(danone_gh_team)
        return teams_list

    def getUser(self):
        req = requests.get(self.githubUrl + '/user', headers=self.headers)
        return req

    def getUserByUsername(self, username):
        req = requests.get(self.githubUrl + '/users/' + username , headers=self.headers)
        return req


    def getUserEmail(self, username):
        try:
            email =  self.getUserByUsername(username).json()['email']
            return email
        except:
            return None

    def createRepo(self, repo_name):
        data = json.dumps({
            'name': repo_name,
            'description': 'Billing report repository towards teams.',
            'homepage': 'https://github.com',
            'private': True,
            'has_issues': True,
            'has_projects': True,
            'has_wiki': True,
            'team_id': GITHUB_ADMINS_TEAM_ID
        })

        req = requests.post(self.githubUrl + '/user/repos', headers=self.headers, data=data)
        print(req.json())
        return req


class DanoneGithubTeam:
    def __init__(self):
        self.name = None
        self.id = None
        self.members = []
        self.billing = 0
        self.description = None
        self.leader = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def setTeamInfos(self, name, id, description):
        self.name = name
        self.id = id
        self.description = description

    def addMemberInList(self, member):
        self.members.append(member)

class DanoneGithubMember:
    def __init__(self):
        self.id = None
        self.login = None
        self.email = None
        self.company = None
        self.type = None

    def __str__(self):
        return self.login

    def __repr__(self):
        return self.login

    def setGithubMemberInfos(self, id, login, email):
        self.id = id
        self.login = login
        self.email = email



if __name__ == '__main__':
    my_g = MyGithub()
    teams_list = my_g.getMembers()
    print(teams_list)
    print(len(teams_list))
    for i in range(len(teams_list)):
        team = teams_list[i]
        print(team.name, team.id, str(team.billing) +
              '€', str(len(team.members)) + ' members', sep=' / ')
    my_g.createRepo('github.billingreport-repository')
