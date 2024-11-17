import time

from config.settings import Settings
from models.credentials import GitHubCredentials
from services.github_fetcher import GitHubDataFetcher

def main():
    # Load configuration
    token = Settings.load_github_token()
    credentials = GitHubCredentials(token=token)
    fetcher = GitHubDataFetcher(credentials)
    
    # Example repository
    repo_url = "https://github.com/aris-space/sage-moc"
    
    try:
        start_time = time.time()
        # Fetch complete repository data
        repo_data = fetcher.fetch_complete_repository_data(repo_url)

        # repo_issues = fetcher.fetch_issues(repo_url)
        # repo_pull_requests = fetcher.fetch_pull_requests(repo_url)

        # print(f"Fetched {len(repo_issues)} issues")
        # print(f"Fetched {len(repo_pull_requests)} pull requests")
        
        print(f"Fetched {len(repo_data['issues'])} issues")
        print(f"Fetched {len(repo_data['pull_requests'])} pull requests")
        
        # Print some statistics about the data
        total_comments = sum(len(issue.get('comments_data', [])) for issue in repo_data['issues'])
        total_events = sum(len(issue.get('events_data', [])) for issue in repo_data['issues'])
        total_pr_reviews = sum(len(pr.get('reviews', [])) for pr in repo_data['pull_requests'])
        
        print(f"Total issue comments: {total_comments}")
        print(f"Total issue events: {total_events}")
        print(f"Total PR reviews: {total_pr_reviews}")


        print(f"Time elapsed: {time.time() - start_time:.2f} seconds")


    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 