from tools import tools_map, query_user_for_details
from prompt import gen_prompt, user_prompt
from model_provider import ModelProvider
from dotenv import load_dotenv
import dashscope

load_dotenv()
mp = ModelProvider()

dashscope.api_key = 'sk-f529539e3a50472fac783cf1e99fddef'

# 解析模型返回的响应，提取关键信息并格式化为字符串
def parse_thoughts(response):
    try:
        thoughts = response.get("thoughts")
        observation = response.get("observation")
        planning = thoughts.get("planning")
        reasoning = thoughts.get("reasoning")
        reflection = thoughts.get("reflection")
        summary = thoughts.get("summary")
        query_user = thoughts.get("query_user")
        prompt = f"planning: {planning}reasoning: {reasoning}reflection: {reflection}observation: {observation}summary: {summary}query_user: {query_user}"
        return prompt
    except Exception as e:
        print(f"parse_thoughts error: {e}")
        return ""
    return {}

# 执行代理任务，与模型交互并处理结果
def agent_execute(query, max_request_time):
    cur_request_time = 0
    chat_history = []
    agent_scratch = ""
    while cur_request_time < max_request_time:
        cur_request_time += 1
        prompt = gen_prompt(query, agent_scratch)
        print('开始调用通义千问.....')
        response = mp.chat(prompt, chat_history)
        print(response)
        if not response or not isinstance(response, dict):
            print(f"call llm exception, response is: {response}")
            continue
        action_info = response.get("action")
        action_name = action_info.get("name")
        action_args = action_info.get("args")
        print(f"action_name: {action_name}, action_args: {action_args}")
        thoughts = response.get("thoughts")
        planning = thoughts.get("planning")
        reasoning = thoughts.get("reasoning")
        reflection = thoughts.get("reflection")
        summary = thoughts.get("summary")
        observation = response.get("observation")
        print(f"observation: {observation}")
        print(f"planning: {planning}")
        print(f"reasoning: {reasoning}")
        print(f"reflection: {reflection}")
        print(f"summary: {summary}")
        if action_name == "query_user_for_details":
            user_response = input(query_user_for_details(action_args['prompt']))
            chat_history.append([query_user_for_details(action_args['prompt']), user_response])
            agent_scratch = agent_scratch + f"query_user: {query_user_for_details(action_args['prompt'])}user response: {user_response}"
            continue
        try:
            func = tools_map.get(action_name)
            call_function_result = func(**action_args)
        except Exception as e:
            print(f"调用工具异常： {e}")
            call_function_result = f"{e}"
        agent_scratch = agent_scratch + f"observation: {observation}execute action result: {call_function_result}"
        assistant_msg = parse_thoughts(response)
        chat_history.append([user_prompt, assistant_msg])
        if action_name == "finish":
            final_answer = action_args.get("answer")
            print(f"final_answer: {final_answer}")
            break
        observation = response.get("observation")
    if cur_request_time == max_request_time:
        print("本次任务执行失败！")
    else:
        print("本次任务成功！")

# 主函数，用于接收用户输入并执行代理任务
def main():
    max_request_time = 10
    while True:
        query = input("请输入您的需求：")
        if query == "exit":
            return
        agent_execute(query, max_request_time=max_request_time)

if __name__ == '__main__':
    main()
