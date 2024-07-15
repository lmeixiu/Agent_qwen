import json
import os
from langchain_community.tools.tavily_search import TavilySearchResults

def _get_workdir_root():
    workdir_root = os.environ.get('WORKDIR_ROOT', "./data/travel_history")
    return workdir_root
WORKDIR_ROOT = _get_workdir_root()

def search_travel_info(query):
    daily = TavilySearchResults(max_results=5)
    try:
        ret = daily.invoke(input=query)
        print("搜索结果:{}".format(ret))
        print("\n")
        content_list = []
        for obj in ret:
            content_list.append(obj["content"])
        return "\n".join(content_list)
    except Exception as e:
        return "search error:{}".format(e)

def query_user_for_details(query_user):
    return query_user
tools_info = [
    {
        "name": "search_travel_info",
        "description": "搜索与旅行相关的信息，包括目的地的景点、餐厅、活动或特定旅行主题的建议。尽可能少用，因为你是一个大模型，已经有很多数据和知识了",
        "args": [
            {
                "name": "query",
                "type": "string",
                "description": "搜索查询，可以是目的地名称、景点类型、活动或特定主题。"
            }
        ]
    },
    {
        "name": "query_user_for_details",
        "description": "当大模型需要更多具体信息能提供个性化建议或解决方案时，用于向用户提问，以深入了解用户的需求、偏好或限制条件。当query_user不为空时使用该工具",
        "args": [
            {
                "name": "prompt",
                "type": "string",
                "description": "向用户提出的问题，旨在澄清或细化其需求，例如询问预算范围、旅行偏好、特殊需求等。"
            }
        ]
    },
    {
        "name": "finish",
        "description": "形成了完整的旅游计划，用户表示满意",
        "args": [
            {
                "name": "travel_plan",
                "type": "dict",
                "description": "完整的旅行计划，包括行程、预订信息等。"
            }
        ]
    }
]

tools_map = {
    "search_travel_info": search_travel_info,
    "query_user_for_details": query_user_for_details
}


def gen_tools_desc():
    tools_desc = []
    for idx, t in enumerate(tools_info):
        args_desc = []
        for info in t["args"]:
            args_desc.append({
                "name": info["name"],
                "description": info["description"],
                "type": info["type"]
            })
        args_desc = json.dumps(args_desc, ensure_ascii=False)
        tool_desc = f"{idx+1}.{t['name']}:{t['description']}, args: {args_desc}"
        tools_desc.append(tool_desc)
    tools_prompt = "\n".join(tools_desc)
    return tools_prompt



