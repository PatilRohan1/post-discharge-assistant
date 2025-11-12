from typing import List, Dict
from duckduckgo_search import DDGS
from src.utils.logger import Logger
from src.constants.environment_constants import EnvironmentConstants


class WebSearchTool:
    def __init__(self):
        self.max_results = EnvironmentConstants.WEB_SEARCH_RESULTS.value
        Logger.log_info_message("Web Search Tool initialized (DuckDuckGo)")
    
    def search(self, query: str) -> List[Dict]:
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    max_results=self.max_results
                ))
            
            formatted_results = [
                {
                    "title": result.get("title", ""),
                    "snippet": result.get("body", ""),
                    "url": result.get("href", ""),
                    "source": "Web Search"
                }
                for result in results
            ]
            
            Logger.log_info_message(f"Web search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            Logger.log_error_message(e, "Error in web search")
            return []