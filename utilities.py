import re
from enum import Enum


class SourceType(Enum):
    URL = "URL"
    SEARCH_QUERY = "Search Query"


def is_url_or_search_query(input_string):
    # Regular expression pattern to match a URL
    url_pattern = re.compile(
        r'^(https?:\/\/)?'  # Optional scheme
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # Domain name
        r'(\/[^\s]*)?$'  # Optional path
    )

    if url_pattern.match(input_string):
        return SourceType.URL
    else:
        return SourceType.SEARCH_QUERY
