import json
import requests


class GitHub(object):

    _base_url = "https://api.github.com/"
    _gh_user = None
    _gh_repo = None

    def __init__(self, url=None, github_user=None, github_repo=None):
        if url:
            self._base_url = url
        if github_user:
            self._gh_user = github_user
        if github_repo:
            self._gh_repo = github_repo

    def _request(self, url):
        try:
            self.response = requests.get(url)
            self.response.raise_for_status()
            return json.loads(self.response.content.decode('utf-8'))
        except Exception as e:
            raise e

    def get_latest_branch(self, branch, github_user=None, github_repo=None):
        self._gh_user = github_user if github_user else self._gh_user
        self._gh_repo = github_repo if github_repo else self._gh_repo

        url_data = f"repos/{self._gh_user}/{self._gh_repo}/branches/{branch}"
        return self._request(f"{self._base_url}{url_data}")

    def get_releases(self, github_user=None, github_repo=None):
        self._gh_user = github_user if github_user else self._gh_user
        self._gh_repo = github_repo if github_repo else self._gh_repo

        url_data = f"repos/{self._gh_user}/{self._gh_repo}/releases"
        return self._request(f"{self._base_url}{url_data}")

    def get_latest_release(self, github_user=None, github_repo=None):
        self._gh_user = github_user if github_user else self._gh_user
        self._gh_repo = github_repo if github_repo else self._gh_repo

        url_data = f"repos/{self._gh_user}/{self._gh_repo}/releases/latest"
        return self._request(f"{self._base_url}{url_data}")

    def get_tags(self, github_user=None, github_repo=None):
        self._gh_user = github_user if github_user else self._gh_user
        self._gh_repo = github_repo if github_repo else self._gh_repo

        url_data = f"repos/{self._gh_user}/{self._gh_repo}/tags"
        return self._request(f"{self._base_url}{url_data}")
