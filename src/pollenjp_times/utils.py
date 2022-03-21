# Standard Library
import re
from typing import List


def extract_slack_urls(text: str) -> List[str]:
    """
    extract urls from slack message text

    example:
        Input: "へー\n<https://example.com>\n<https://example.com|https://example.com>"
        Output: ["https://example.com", "https://example.com"]
    """
    slack_urls: List[str] = re.findall(pattern=r"<.*>", string=text)
    urls: List[str] = []
    for slack_url in slack_urls:
        match = re.match(r"<(?P<url>.*)\|.*>", slack_url)
        if match is None:
            url = slack_url[1:-1]
        else:
            url = match.groupdict()["url"]
        urls.append(url)
    return urls
