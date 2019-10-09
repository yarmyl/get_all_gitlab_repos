#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gitlab
import requests
import argparse
import os
import re


class Gitapi:

    def __init__(self, auth):
        if auth['method'] == "OATH":
            self.oath_auth(
                auth['url'],
                self.pass_auth(auth['url'], auth['user'], auth['pass'])
            )
        elif auth['method'] == "TOKEN":
            self.token_auth(auth['url'], auth['token'])

    def token_auth(self, url, token):
        self.gl = gitlab.Gitlab(url, private_token=token)
        self.url = url
        self.token = token
        self.gl.auth()

    def pass_auth(self, url, user, passwd):
        url += 'oauth/token' if url[-1] == '/' else '/oauth/token'
        data = 'grant_type=password&username=' + user + '&password=' + passwd
        r = requests.post(url, data=data)
        self.user = user
        self.passwd = passwd
        return r.json()['access_token']

    def oath_auth(self, url, token):
        self.gl = gitlab.Gitlab(url, oauth_token=token)
        self.url = url
        self.token = token
        self.gl.auth()

    def proj_list(self):
        projects = self.gl.projects.list(all=True)
        return projects

    def proj_list_name(self):
        projects = self.proj_list()
        projects_name = []
        for a in projects:
            projects_name.append(self.get_proj(a.id).name)
        return projects_name

    def group_list(self):
        groups = self.gl.groups.list(all=True)
        return groups

    def group_list_name(self):
        groups = self.group_list()
        groups_name = []
        for a in groups:
            groups_name.append(self.get_group(a.id).name)
        return groups_name

    def get_group(self, id):
        return self.gl.groups.get(id)

    def get_proj(self, id):
        return self.gl.projects.get(id)
    
    def proj_list_path(self):
        projects = self.proj_list()
        projects_name = []
        for a in projects:
            projects_name.append(self.get_proj(a.id).path_with_namespace)
        return projects_name


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', nargs='?')
    parser.add_argument('--user', nargs='?')
    parser.add_argument('--passwd', nargs='?')
    return parser


def main():
    parser = createParser()
    namespace = parser.parse_args()
    git = {
        'method': "OATH",
        'url': namespace.url,
        'user': namespace.user,
        'pass': namespace.passwd
    }
    gitapi = Gitapi(git)
#    for dir in gitapi.proj_list_name():
#      os.mkdir(dir)
    for dir in gitapi.group_list_name():
        if not os.path.exists(dir):
           os.mkdir(dir)
#    print(gitapi.get_proj(gitapi.proj_list()[1].id))
    paths = gitapi.proj_list_path()
    for dir in paths:
        os.chdir(re.split('/', dir)[0])
        os.system("git clone git@" + re.split('http://', namespace.url)[1] + ':' + dir + '.git')
        os.chdir('..')


if __name__ == "__main__":
    main()
