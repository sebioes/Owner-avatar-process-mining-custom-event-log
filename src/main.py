import time
from pathlib import Path

from config.settings import Settings
from models.credentials import GitHubCredentials
from services.github_fetcher import GitHubDataFetcher
from services.event_log_generator import GitHubEventLogGenerator

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
        print("Fetching repository data...")
        repo_data = fetcher.fetch_complete_repository_data(repo_url)
        
        print(f"Fetched {len(repo_data['issues'])} issues")
        print(f"Fetched {len(repo_data['pull_requests'])} pull requests")

        print(f"\nTime elapsed fetching repository data: {time.time() - start_time:.2f} seconds")

        start_generate_event_log = time.time()
        
        # Generate event log
        print("\nGenerating event log...")
        generator = GitHubEventLogGenerator()
        
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate output filename from repository name
        repo_name = repo_url.split('/')[-1]
        output_path = output_dir / f"{repo_name}_event_log.xes"
        
        generator.generate_event_log(repo_data, str(output_path))
        print(f"Event log saved to: {output_path}")
        
        print(f"\nTime elapsed generating event log: {time.time() - start_generate_event_log:.2f} seconds")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 