from github import Github, UnknownObjectException
from typing import Optional
from app.core.config import ConfigManager
import logging

class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, config_manager: ConfigManager):
        self.gh = None
        pat = config_manager.get_setting("GITHUB_PAT")
        if pat:
            self.gh = Github(pat)
        else:
            logging.warning("GitHub PAT not configured - GitHub features will be disabled")

    def get_repo_file_content(self, repo_full_name: str, file_path: str) -> Optional[str]:
        """Get content of a file from a GitHub repository."""
        if not self.gh:
            return None
            
        try:
            repo = self.gh.get_repo(repo_full_name)
            content = repo.get_contents(file_path)
            return content.decoded_content.decode('utf-8')
        except UnknownObjectException:
            logging.warning(f"GitHub resource not found: {repo_full_name}/{file_path}")
            return None
        except Exception as e:
            logging.error(f"GitHub API error: {str(e)}")
            return None

    # Optional additional methods
    def search_repositories(self, query: str) -> Optional[list]:
        """Search GitHub repositories."""
        if not self.gh:
            return None
            
        try:
            return list(self.gh.search_repositories(query))
        except Exception as e:
            logging.error(f"GitHub search error: {str(e)}")
            return None