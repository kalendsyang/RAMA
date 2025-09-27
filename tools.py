import requests
import json
import http.client
import time
import re
from typing import Optional,List,Dict
import json
import traceback
import re
import mimetypes
import datetime

EXTRACT_NEW_INFO_PROMPT = """You are a helpful AI research assistant. I will provide you:
* The user's main question. This is a complex question that requires a deep research to answer.
* The context so far. This includes all the information that has been gathered from previous turns, including the sub-questions and the information gathered from other resources for them.
* One page of a webpage content as well as the page index. We do paging because the content of a webpage is usually long and we want to provide you with a manageable amount of information at a time. So please mind the page index to know which page you are reading as this could help you infer what could appear in other pages.

Your task is to read the webpage content carefully and extract all *new* information (compared to the context so far) that could help answer either the main question or the sub-question. So you should only gather incremental information from this webpage, but if you find additional details that can complete the previous context, please include them. If you find contradictory information, also include them for further analysis. Provide detailed information including numbers, dates, facts, examples, and explanations when available. Keep the original information as possible, but you can summarize if needed.

In addition to the extracted information, you should also think about whether we need to read more content from this webpage to get more detailed information by paging down to read more content. Also, add a very short summary of the extracted information to help the user understand the new information.


Note that there could be no useful information on the webpage.

Your answer should follow the following format: 
* Put the extracted new information in <extracted_info> tag. If there is no new information, leave the <extracted_info> tag empty. Do your best to get as much information as possible.
* Put "yes" or "no" in <page_down> tag. This will be used for whether to do page down to read more content from the web. For example, if you find the extracted information is from the introduction section in a paper, then you can infer that the extracted information could miss detailed information, next round can further read more content for details in this web page by paging down. If this already the last page, always put "no" in <page_down> tag.
* Put the short summary of the extracted information in <short_summary> tag. Try your best to make it short but also informative as this will present to the user to notify your progress. If there is no useful new information, please also say something like "Didn't find useful information, will read more" in the short summary (be free to use your own words). 

Important note: Use the same language as the user's main question for the short summary. For example, if the main question is using Chinese, then the short summary should also be in Chinese.


<main_question>
{main_question}
</main_question>

<webpage_content>
    <page_index>{page_index}</page_index>
    <total_page_number>{total_pages}</total_page_number>
    <current_page_content>{page_content}</current_page_content>
</webpage_content>

Now think and extract the incremental information that could help answer the main question."""



def truncate_content(content: str, max_length: int) -> str:
    if len(content) <= max_length:
        return content
    return (
        content[: max_length // 2]
        + f"\n..._This content has been truncated to stay below {max_length} characters_...\n"
        + content[-max_length // 2 :]
    )
        
def get_content_from_tag(content, tag, default_value=None):
    # 1) (.*?) lazy match，minimum match characters
    # 2) (?=(</tag>|<\w+|$)) lookahead assertion, meaning stop matching when followed by </tag> or <any word character> or end of text
    # 3) re.DOTALL makes . match newline characters
    pattern = rf"<{tag}>(.*?)(?=(</{tag}>|<\w+|$))"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return default_value

def web_browser(url, query, client, max_output_length) -> str:
    try:

        import requests
        from markdownify import markdownify
        from requests.exceptions import RequestException
    except ImportError as e:
        raise ImportError(
            "You must install packages `markdownify` and `requests` to run this tool: for instance run `pip install markdownify requests`."
        ) from e
    try:
        # Send a GET request to the URL with a 20-second timeout
        # proxies = {
        #     "http": "socks5h://127.0.0.1:11080",
        #     "https": "socks5h://127.0.0.1:11080",
        # }
        
        # response = requests.get(url, timeout=20, proxies=proxies)
        response = requests.get(url, timeout=20) # socks5://127.0.0.1:11080
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify(response.text).strip()
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
        markdown_content = truncate_content(markdown_content, max_output_length)

        prompt = EXTRACT_NEW_INFO_PROMPT.format(
                main_question=query,
                page_index=1,
                total_pages=1,
                page_content=markdown_content
            )
        messages = [{"role": "user", "content": prompt}]
        # print('llm processing:',messages)
        result = client(messages)
        response = json.loads(result.model_dump_json())['content']
        # print('llm processing result:',response)
        extracted_info = get_content_from_tag(response, "extracted_info", "").strip()

        return extracted_info

    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later or check the URL."
    except RequestException as e:
        return f"Error fetching the webpage: {(str(traceback.format_exc()))}"
    except Exception as e:
        return f"An unexpected error occurred: {(str(traceback.format_exc()))}"



def serper_data_serp_api(query,
                      region='',
                      lang=''):
    headers = { 'X-API-KEY': 'your google api key', 'Content-Type': 'application/json' } 
    payload = json.dumps({
      "q": query,
      # "location": "",
      "gl": region,
      "hl": lang,
      "num": 10,
      # "tbs": "qdr:d"
    })
    attempts = 3
    for attempt in range(attempts):
        try:
            conn = http.client.HTTPSConnection("google.serper.dev") 
            conn.request("POST", "/search", payload, headers) 
            res = conn.getresponse() 
            data = json.loads(res.read().decode("utf-8"))
            if 'organic' not in data.keys():
                raise Exception(f"No results found for query: '{query}' '{str(data)}'. Use a less specific query.")
            else:
                results = data["organic"]
                return results
        except Exception as e:
            print(f"serper search API error: {e}")
            if attempt < attempts - 1:
                continue
            else:
                return []
