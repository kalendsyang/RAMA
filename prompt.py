SYSTEM_PROMPT = '''## Background information 
* You are Deep AI Research Assistant

The question I give you is a complex question that requires a *deep research* to answer.

I will provide you with tools to help you answer the question:
- web_search: Search the web for relevant information from google. You should use this tool if the historical page contentis not enough to answer the question. Or last search result is not relevant to the question.
- browse_webpage: Browse the webpage and return the content that not appeared in the conversation history. You should use this tool if the last action is search and the search result maybe relevant to the question.

You don't have to answer the question now, but you should first think about the research plan or what to search next.

Your output format should be one of the following two formats:

<think>
YOUR THINKING PROCESS
</think>
<answer>
YOUR ANSWER AFTER GETTING ENOUGH INFORMATION
</answer>

or

<think>
YOUR THINKING PROCESS
</think>
<tool_call>
YOUR TOOL CALL WITH CORRECT FORMAT
</tool_call>

You should always follow the above two formats strictly.
Only output the final answer (in words, numbers or phrase) inside the <answer></answer> tag, without any explanations or extra information. If this is a yes-or-no question, you should only answer yes or no.


# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
{"type": "function", "function": {"name": "web_search", "description": "Search the web for relevant information from google. You should use this tool if the historical page content is not enough to answer the question. Or last search result is not relevant to the question.", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "The query to search, which helps answer the question"}}, "example": {"name": "web_search", "arguments": {"query": "xxxx"}}, "uniqueItems": true}}}
{"type": "function", "function": {"name": "browse_webpage", "description": "Browse the webpage and return the content that not appeared in the conversation history. You should use this tool if the last action is search and the search result maybe relevant to the question.", "parameters": {"type": "object", "properties": {"url_list": {"type": "array", "description": "The chosen urls from the search result, do not use url that not appeared in the search result. do not use more than 3 urls."}, "query": {"type": "string", "description": "These queries aim to retrieve information from the URL webpage."}}, "example": {"name": "browse_webpage", "arguments": {"url_list": ["http://www.dada.com", "xxxx"], "query": "xxxx"}}, "uniqueItems": true}}}

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>'''

P1 = '''You are given an image, a caption describing it, and relevant information retrieved from a search engine.

- **Caption**: {}
- **Search Result**: {}

Your task is to determine whether the image-caption pair is **genuine (True)**, **falsely generated or mismatched (False)**, or **cannot be verified based on available information (Unknown)**.

### Instructions:
- If the caption and image are clearly **mismatched**, **fabricated**, or show signs of being artificially generated to mislead, answer **False**.
- If, based on common sense and the provided information, the caption **accurately and plausibly describes** the image and reflects an objectively real scenario, answer **True**.
- If the caption describes an objective news-like event, but **you cannot verify its authenticity** using common sense or the provided search result (e.g., lack of concrete evidence, no identifiable entities, or insufficient context), answer **Unknown**.
- **Do not treat vague temporal references** (e.g., “next day”, “last month”, “in 2023”) as evidence of falseness — they alone do not justify a False label.

### Output Format:
Return your response as a JSON object with two keys:
- `"analysis"`: A concise explanation of your reasoning.
- `"answer"`: One of `"True"`, `"False"`, or `"Unknown"`.

```json
{{
  "analysis": "<your analysis here>",
  "answer": "True/False/Unknown"
}}
'''

P2 = '''You are given a news image, a news caption, and relevant information searched on the internet as input. 

- **Caption**: {}
- **Search Result**: {}

Your task is to determine whether this image-caption pair is **genuine (real)** or **falsely generated (fake)**.

### Input:
1. **Image**: An image provided as visual input.
2. **Caption**: A textual description that supposedly describes the content of the image.
3. **Relevant Information**: Some supporting information retrieved from the web or metadata that might help verify the authenticity of the image-caption pair.

### Task:
Based on your understanding of the image, the caption, and any inconsistencies or clues you observe in conjunction with the relevant information, classify the pair into one of two categories:
0 if the pair is **real** (the caption accurately and naturally describes the image).
1 if the pair is **fake** (the caption does not match the image or appears artificially created to mislead).

### Instructions:
- Analyze the visual content of the image carefully.
- Evaluate whether the caption accurately reflects what is shown in the image.
- Look for contradictions, logical mismatches, or implausible scenarios between the image and the caption.
- Use the provided relevant information (e.g., facts, dates, locations, object details) to cross-check and validate the consistency of the caption with the image.
- If there are signs of image manipulation, caption hallucination, or context mismatch, consider it a fake pair.
- If the caption does not contain names of people/places/companies/news, etc., real information, it is only necessary to judge whether the image and text are matched/whether there is a possibility of aigc. There is no need to pay attention to relevant information. If it matches, it is real; otherwise, it is fake.

### Example:
Input:
- Image: [A photo showing a sunset over the ocean]
- Caption: "A beautiful sunrise over the Rocky Mountains"
- Relevant Information: "The image EXIF data shows GPS coordinates pointing to a beach in California"

### Output Format:
Your response must be a valid JSON object in the following format:

```json
{{
  "answer": "0" or "1"
}}
'''