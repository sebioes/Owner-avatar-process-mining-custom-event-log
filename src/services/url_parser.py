class GitHubUrlParser:
    """Service for parsing GitHub URLs"""
    
    @staticmethod
    def parse_repo_url(repo_url: str) -> tuple[str, str]:
        """Extract owner and repo name from repository URL"""
        # Remove trailing .git if present
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        # Split the URL and get the last two parts
        parts = repo_url.split('/')
        owner = parts[-2]
        repo = parts[-1]

        return owner, repo 