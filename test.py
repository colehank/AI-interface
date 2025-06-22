# %%
from __future__ import annotations

import src
from src import BaseLLM
from src import TemplateLLM
# %%
llm = BaseLLM()
llm.call(
    messages=[{'role': 'user', 'content': 'Who is the president of the United States?'}],
    response_format='text',
)

res = llm.call(
    messages=llm.call_history + [{'role': 'user', 'content': 'Where is the president from?'}],
    response_format='text',
)
llm.print_history()
# %%
prompt_file = src.prompts.llm_prompts['text2triples']
template_llm = TemplateLLM(prompt_file)
res = template_llm.call(
    passage='XiaoMing is a Chinese student from Beijing Normal University',
    named_entities='["Chinese", "Beijing Normal University", "XiaoMing"]',
    model='gpt-4o',
    response_format='json',
)
template_llm.print_history()
# %%
