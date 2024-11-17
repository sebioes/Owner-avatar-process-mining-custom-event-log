from dataclasses import dataclass

@dataclass
class GitHubCredentials:
    """Class to store GitHub authentication credentials"""
    token: str
    api_version: str = "2022-11-28" 