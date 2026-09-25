import json

class GitLab:
    """
    Instantiate with 1 argument, parsed json string <string>
    """
    def __init__(self, arg1):
        self.json_data = arg1

        # Types of build and issue JSON from GitLab Webhook
        self.issue_types = ["open", "update", "closed"]

        # Below is for common JSON objects
        self.object_kind = arg1.get("object_kind", "")
        self.project_id = arg1.get("project_id", "")
        self.ref = arg1.get("ref", "")
        self.project_name = arg1.get("project_name", "")
        self.user = arg1.get("user", "")
        self.commit = arg1.get("commit", "")
        self.object_attributes = arg1.get("object_attributes", "")
        self.build_status = arg1.get("build_status", "")

        repo_obj = arg1.get("repository", "")
        if repo_obj != "":
            self.repository = repo_obj
            self.repo_name = repo_obj.get("name", "")
            self.repo_homepage = repo_obj.get("homepage", "")

    def check_repository_atttr(self):
        if self.repository == "":
            return False
        else:
            return True

    def get_url(self, url=None):
        """
        Arguments:
            - url : type of url to return <string>
                * input types:
                    - "http" : retrieve git http url
                    - "ssh" : retrieve git ssh url
                    - "homepage" : retrieve homepage url
                    - (no input) : retrieve default git url, which is: "repository": {"url": <url>}
        """
        if not self.check_repository_atttr():
            return False
        if url.lower() == "ssh":
            return self.repository.get("git_ssh_url")
        elif url.lower() == "http":
            return self.repository.get("git_http_url")
        elif url.lower() == "homepage":
            return self.repository.get("homepage")
        else:
            return self.repository.get("url")

    def get_repo_description(self):
        """
        Arguments: None
        Checks to see if the key 'description' is in the webhook
        """
        if check_repository_atttr():
            return self.repository.get("description")
        else:
            return False

    def build(self, *args):
        """
        Checks to see if JSON data from GitLab is build data and also checks to see that you want build data. If so, return True
        Arguments: *args <bool><string><list>
            - can be a list of certain build data  you want
            - build types are 'success', 'failed', 'runnning'
        """
        if self.object_kind == "build" and self.build_status in args:
            return True
        else:
            return False

    def note(self, note_types=False):
        """
        Checks to see if JSON data is a note (comment) and you want note JSON data. If so, return True
        Arguments: note_types <bool>
            - Returns True if you want note type JSON data to return True and JSON data is a note
            - Default - False
        """
        if note_types and self.object_kind == "note":
            return True
        else:
            return False

    def merge_request(self, merge_request_types=False):
        """
        Checks to see if JSON data is a merge request and if you want merge_request data. If so, return True
        Arguments: merge_request_types <bool>
            - True if you want merge request data from GitLab to be returned if JSON data is merge request.
            - Default - False
        """
        if merge_request_types and self.object_kind == "merge_request":
            return True
        else:
            return False

    def issue(self, *args):
        """
        Checks to see if JSON data is an issue from GitLabJSON
        Arguments: *args <bool><string><list>
            - can be list of issue types or boolean
            - issue types are 'open', 'update', 'closed'
            - True if you want all issues pass this conditional function
        """
        if self.object_kind != "issue":
            return False

        if "open" in args or "closed" in args:
            if self.object_attributes.get("state") == "closed" and "closed" in args:
                return True
            elif self.object_attributes.get("action") == "open" and "open" in args:
                return True
        elif "update" in args and self.object_attributes.get("action") == "update":
            return True
        else:
            return False
