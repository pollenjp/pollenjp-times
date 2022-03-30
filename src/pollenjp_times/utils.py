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


def convert_slack_urls_to_discord(text: str) -> str:
    """
    extract urls from slack message text

    example:
        Input:
            "<@U123456>はー\n<#hoge-ch|C123456>ひー\nふー\n<https://example.com>へー\n<https://example.com|https://example.com>"
        Output:
            "`@ U123456`\n`#hoge-ch`\nへー\n https://example.com \n https://example.com "
    """

    text = re.sub(r"<@(\S+?)>", r"`@ \1`", text)
    text = re.sub(r"<#(\S+?)\|(\S+?)>", r"`#\1`", text)
    text = re.sub(r"<(\S+?)\|(\S+?)>", r" \1 ", text)
    text = re.sub(r"<(\S+?)>", r" \1 ", text)

    return text
