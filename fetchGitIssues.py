##########################################################################################
#  Author: Abhay Khanna                                                                  #
#                                                                                        #
#  Script to get the issue details and the first comment from a GIT issue URL            #
#                                                                                        #
#  Usage:                                                                                #
#  -----                                                                                 #
#  python fetchGitIssue.py <GIT_ISSUE_URL> [PAT_TOKEN]                                   #
#                                                                                        #
# NOTE: Here PAT is the "Personal Access Token" generated from GIT API                   #
##########################################################################################
 
########################## IMPORT PACKAGES#######################################    
import os
import re
import sys
import time
import subprocess
import json
from common import ContentLogger
try:
    import requests 
except:
    subprocess.run("pip install -q requests", check=True)
    time.sleep(5.0)
    import requests

import logging
import warnings
warnings.filterwarnings("ignore")
##################################################################################
 
def getIssueDetailsFromGitRepo(git_issue_url, pat_token):
    try:
        # Extract repo owner, repo name, and issue number from the URL
        repo_owner, repo_name, issue_number = re.search(r"https://github.com/(.*?)/(.*?)/issues/(\d+)", git_issue_url).groups()
    except:
        print({'ERROR': {'message': "Invalid Git issue URL."}})
        logging.info("Invalid GIT issue URL.\n\nDONE!")
        content_logger.log("error", "Invalid GIT issue URL.\n\nDONE!")
        sys.exit(1)
 
    # API endpoint for the specific issue
    issue_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
    comments_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments"
 
    headers = {
        "Authorization": f"token {pat_token}",
        "Accept": "application/vnd.github.v3+json"
    } if pat_token else {}
 
    # Get the issue details
    issue_response = requests.get(issue_url, headers=headers, verify=False)
    if issue_response.status_code != 200:
        logging.info(f"Unable to get the issue details from GIT REPOSITORY\n")
        logging.info(f'Error: {issue_response.status_code} - {issue_response.text} \n\nDONE!')
        
        content_logger.log("error", f"Unable to get the issue details from GIT REPOSITORY\n")
        content_logger.log("error", f'Error: {issue_response.status_code} - {issue_response.text} \n\nDONE!')
        
        error_data = json.loads(issue_response.text)
        message = error_data.get("message", "Unable to get the issue details from GIT REPOSITORY")
        print({'ERROR' : {"message": message}})
        sys.exit(1)
 
    issue = issue_response.json()
 
    # Get the first comment
    comments_response = requests.get(comments_url, headers=headers, verify=False)
    if comments_response.status_code == 200:
        comments = comments_response.json()
        first_comment = comments[0]['body'] if comments else "No comments available."
    else:
        first_comment = "Unable to fetch comments."
 
    # Log and return the issue details and first comment
    logging.info(f"Issue Title :{issue['title']}\n")
    logging.info(f"Issue Description :{issue['body']}\n")
    
    content_logger.log("info", f"Issue Title :{issue['title']}\n")
    content_logger.log("info", f"Issue Description :{issue['body']}\n")    
 
    result = {
        "Title": issue['title'],
        "Description": issue['body'],
    }
    
    return result
 
if __name__ == "__main__":
    params = sys.argv
    
    log_file = "./../../../Data/DefectFixIssueDetails/gitIssueDetails.txt"
    content_log = "./../../../Logs/system/fetchGitIssues.log"
    os.makedirs("./../../../Logs/system/", exist_ok=True)

    for file_ in [log_file, content_log]:
        if os.path.exists(file_):
            os.remove(file_)

    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(message)s')
    content_logger = ContentLogger(content_log)

    if len(params) == 3:
        _, git_issue_url, pat_token = params
    elif len(params) == 2:
        _, git_issue_url = params
        pat_token = ''
    else:
        print({'ERROR': {'message': "Script needs exactly two or three arguments. i.e., <GIT_ISSUE_URL> <PAT_TOKEN>"}})
        content_logger.log("error", "Script needs exactly two or three arguments. i.e., <GIT_ISSUE_URL> <PAT_TOKEN>")
        sys.exit(1)
    
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    issue_details = getIssueDetailsFromGitRepo(git_issue_url, pat_token)
    print({'SUCCESS': "Git Issue fetched successfully."})
    content_logger.log("info", "Git Issue fetched successfully.")
