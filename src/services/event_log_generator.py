from typing import Dict, List
import pandas as pd
import pm4py
from datetime import datetime

class GitHubEventLogGenerator:
    """Class to generate XES event logs from GitHub repository data"""
    
    def __init__(self):
        self.case_id_prefix = "GH"  # Prefix for case IDs
        
    def generate_event_log(self, repo_data: Dict, output_path: str) -> None:
        """
        Generate and save XES event log from GitHub repository data
        
        Args:
            repo_data: Dictionary containing issues and pull requests data
            output_path: Path where the XES file should be saved
        """
        # Convert GitHub data to dataframe format
        events = self._create_events_dataframe(repo_data)
        
        # Format dataframe for PM4Py
        event_log = pm4py.format_dataframe(
            events,
            case_id='case_id',
            activity_key='activity',
            timestamp_key='timestamp'
        )
        
        # Write to XES file
        pm4py.write_xes(event_log, output_path)
        
    def _create_events_dataframe(self, repo_data: Dict) -> pd.DataFrame:
        """Create a pandas DataFrame with all events"""
        events = []
        
        # Process issues
        for issue in repo_data['issues']:
            case_id = f"{self.case_id_prefix}_ISSUE_{issue['number']}"
            
            # Add issue creation event
            events.append({
                'case_id': case_id,
                'activity': 'create_issue',
                'timestamp': issue['created_at'],
                'resource': issue['user']['login'],
                'issue_type': 'issue',
                'state': issue['state']
            })
            
            # Add close event if issue is closed
            if issue['state'] == 'closed' and issue['closed_at']:
                events.append({
                    'case_id': case_id,
                    'activity': 'close_issue',
                    'timestamp': issue['closed_at'],
                    'resource': issue['user']['login'],  # Using creator as closer since we don't have detailed events
                    'issue_type': 'issue',
                    'state': 'closed'
                })
            
            # Add comment events
            for comment in issue.get('comments_data', []):
                events.append({
                    'case_id': case_id,
                    'activity': 'comment',
                    'timestamp': comment['created_at'],
                    'resource': comment['user']['login'],
                    'issue_type': 'issue',
                    'state': issue['state']
                })
        
        # Process pull requests
        for pr in repo_data['pull_requests']:
            case_id = f"{self.case_id_prefix}_PR_{pr['number']}"
            
            # Add PR creation event
            events.append({
                'case_id': case_id,
                'activity': 'create_pull_request',
                'timestamp': pr['created_at'],
                'resource': pr['user']['login'],
                'issue_type': 'pull_request',
                'state': pr['state']
            })
            
            # Add PR review events
            for review in pr.get('reviews', []):
                events.append({
                    'case_id': case_id,
                    'activity': f'review_{review["state"].lower()}',  # e.g., review_approved, review_commented
                    'timestamp': review['submitted_at'],
                    'resource': review['user']['login'],
                    'issue_type': 'pull_request',
                    'state': pr['state']
                })

            # Add PR comment events
            for comment in pr.get('comments_data', []):
                events.append({
                    'case_id': case_id,
                    'activity': 'comment',
                    'timestamp': comment['created_at'],
                    'resource': comment['user']['login'],
                    'issue_type': 'pull_request',
                    'state': pr['state']
                })
            
            # Add merge/close events
            if pr.get('merged_at'):  # Check if PR was merged using merged_at field
                events.append({
                    'case_id': case_id,
                    'activity': 'merge_pull_request',
                    'timestamp': pr['merged_at'],
                    'resource': pr['merged_by']['login'] if pr.get('merged_by') else pr['user']['login'],
                    'issue_type': 'pull_request',
                    'state': 'merged'
                })
            elif pr['state'] == 'closed':
                events.append({
                    'case_id': case_id,
                    'activity': 'close_pull_request',
                    'timestamp': pr['closed_at'],
                    'resource': pr['user']['login'],  # Using creator as closer
                    'issue_type': 'pull_request',
                    'state': 'closed'
                })
        
        # Convert to DataFrame and sort by timestamp
        df = pd.DataFrame(events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.sort_values('timestamp') 