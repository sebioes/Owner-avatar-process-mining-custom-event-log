from typing import Dict, List
import requests
from models.credentials import GitHubCredentials
from .url_parser import GitHubUrlParser

class GitHubDataFetcher:
    """Class to fetch data from GitHub repositories"""
    
    def __init__(self, credentials: GitHubCredentials):
        self.base_url = "https://api.github.com"
        self.credentials = credentials
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {credentials.token}",
            "X-GitHub-Api-Version": credentials.api_version
        }
        self.url_parser = GitHubUrlParser()

    def fetch_issues(self, repo_url: str, state: str = "all") -> List[Dict]:
        """Fetch all issues from a repository"""
        owner, repo = self.url_parser.parse_repo_url(repo_url)
        return self._paginated_get(f"/repos/{owner}/{repo}/issues", {"state": state})

    def fetch_pull_requests(self, repo_url: str, state: str = "all") -> List[Dict]:
        """Fetch all pull requests from a repository"""
        owner, repo = self.url_parser.parse_repo_url(repo_url)
        return self._paginated_get(f"/repos/{owner}/{repo}/pulls", {"state": state})

    def fetch_issue_comments(self, repo_url: str, issue_number: int) -> List[Dict]:
        """Fetch all comments for a specific issue"""
        owner, repo = self.url_parser.parse_repo_url(repo_url)
        return self._paginated_get(f"/repos/{owner}/{repo}/issues/{issue_number}/comments")

    def fetch_issue_events(self, repo_url: str, issue_number: int) -> List[Dict]:
        """Fetch all events for a specific issue"""
        owner, repo = self.url_parser.parse_repo_url(repo_url)
        return self._paginated_get(f"/repos/{owner}/{repo}/issues/{issue_number}/events")

    def fetch_pr_reviews(self, repo_url: str, pr_number: int) -> List[Dict]:
        """Fetch all reviews for a specific pull request"""
        owner, repo = self.url_parser.parse_repo_url(repo_url)
        return self._paginated_get(f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews")

    def _paginated_get(self, endpoint: str, extra_params: Dict = None) -> List[Dict]:
        """Generic method to handle paginated GitHub API requests"""
        results = []
        page = 1
        
        while True:
            params = {"per_page": 100, "page": page}
            if extra_params:
                params.update(extra_params)
                
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")
            
            page_data = response.json()
            if not page_data:
                break
                
            results.extend(page_data)
            page += 1
            
        return results

    def fetch_complete_repository_data(self, repo_url: str) -> Dict:
        """Fetch all relevant data from a repository"""
        # Fetch basic issues and PRs
        issues = self.fetch_issues(repo_url)
        pull_requests = self.fetch_pull_requests(repo_url)
        
        # Enhance issues with comments and events
        for issue in issues:
            issue_number = issue['number']
            issue['comments_data'] = self.fetch_issue_comments(repo_url, issue_number)
            issue['events_data'] = self.fetch_issue_events(repo_url, issue_number)
        
        # Enhance PRs with reviews
        for pr in pull_requests:
            pr_number = pr['number']
            pr['reviews'] = self.fetch_pr_reviews(repo_url, pr_number)
            pr['comments_data'] = self.fetch_issue_comments(repo_url, pr_number)
            pr['events_data'] = self.fetch_issue_events(repo_url, pr_number)
        
        return {
            'issues': issues,
            'pull_requests': pull_requests
        } 