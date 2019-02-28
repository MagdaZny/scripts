import requests
import xml.etree.ElementTree as ET
import sys
import urllib3
import re

# TO ECEXUTE: python3 -W ignore mvnDependencies.py payments-transport
# last argument indicates a searched dependency

personal_access_token="***" #create your own here https://gitlab.tech.lastmile.com/profile/personal_access_tokens
dependency = str(sys.argv[1])
repos_with_dependencies = []
namespace = '{http://maven.apache.org/POM/4.0.0}'
getRepositoriesUrl="https://gitlab.tech.lastmile.com/api/v4/projects/"

def get_repositories():
    ids = []
    querystring = {"private_token":personal_access_token,"membership":"true","simple":"true","page":"1","per_page":"100"}
    response = requests.request("GET", getRepositoriesUrl, params=querystring, verify=False)

    for i in response.json():
        ids.append(i["id"])
    return ids

def find_dependencies(root, repoName):
    if(root.find(namespace + 'dependencies')):
        for d in root.find(namespace + 'dependencies'):
            artifactId = d.find(namespace + 'artifactId').text
            if(artifactId == dependency):
                repos_with_dependencies.append(repoName)

def check_pom(id):
    url = getRepositoriesUrl + str(id) + "/repository/files/pom.xml/raw?ref=master"
    querystring = {"private_token":personal_access_token}
    response = requests.request("GET", url, params=querystring, verify=False)

    if(response.status_code != 200):
        print("Error with status code " + str(response.status_code) + " for response of a repo with id " + str(id))
    else:
        root = ET.fromstring(response.content)
        repoName = root.find(namespace + 'artifactId').text
        if(root.find(namespace + 'dependencyManagement')):
            find_dependencies(root.find(namespace + 'dependencyManagement'), repoName)
        find_dependencies(root, repoName)

all_repos = get_repositories()
print("Number of repositories to scan: " + str(len(all_repos)))
for repo in all_repos:
    print(repo)
    check_pom(repo)

print("")
print("Projects dependent on " + dependency + ":")
for repo in repos_with_dependencies:
    print(repo)
