import time
import sys
import json
import requests

def print_header(title, eng_title, author, version,website):
    # 使用简单的艺术字风格构造标题信息
    # Construct a fancy header using ASCII art
    header_art = f"""
===============================================
 █████         █████████    █████████  ██████████   ███████████
░░███         ███░░░░░███  ███░░░░░███░░███░░░░███ ░█░░░███░░░█
 ░███        ░███    ░███ ░███    ░░░  ░███   ░░███░   ░███  ░
 ░███        ░███████████ ░░█████████  ░███    ░███    ░███
 ░███        ░███░░░░░███  ░░░░░░░░███ ░███    ░███    ░███
 ░███      █ ░███    ░███  ███    ░███ ░███    ███     ░███
 ███████████ █████   █████░░█████████  ██████████      █████
░░░░░░░░░░░ ░░░░░   ░░░░░  ░░░░░░░░░  ░░░░░░░░░░      ░░░░░
===============================================
{title}
{eng_title}
作者: {author} | Author
版本: {version} | Version
项目地址: {website} | Website
===============================================
"""
    print(header_art)

def print_statistics_box(url, model_name, total_bytes, question_bytes,
                         first_byte_time, twenty_byte_time, fifty_byte_time,
                         full_time_ms, avg_rate, start_time):
    # 构造各项统计信息内容 / Construct various statistics information lines
    stats_lines = []
    stats_lines.append(f"接口地址           : {url} | API URL")
    stats_lines.append(f"模型名称           : {model_name} | Model Name")
    stats_lines.append("-" * 50)
    stats_lines.append(f"发送问题字节长度   : {question_bytes} Byte | Question Byte Length")
    stats_lines.append(f"返回答案字节长度   : {total_bytes} Byte | Answer Byte Length")

    if first_byte_time is not None:
        first_ms = (first_byte_time - start_time) * 1000
        stats_lines.append(f"首个字节响应速度   : {first_ms:.2f} ms | Time to First Byte")
    else:
        stats_lines.append("首个字节响应速度   : N/A | Time to First Byte N/A")

    if twenty_byte_time is not None:
        twenty_ms = (twenty_byte_time - start_time) * 1000
        stats_lines.append(f"前20个字节响应速度  : {twenty_ms:.2f} ms | Time for First 20 Bytes")
    else:
        stats_lines.append("前20个字节响应速度  : N/A | Time for First 20 Bytes N/A")

    if fifty_byte_time is not None:
        fifty_ms = (fifty_byte_time - start_time) * 1000
        stats_lines.append(f"前50个字节响应速度  : {fifty_ms:.2f} ms | Time for First 50 Bytes")
    else:
        stats_lines.append("前50个字节响应速度  : N/A | Time for First 50 Bytes N/A")

    stats_lines.append(f"全部回答响应速度    : {full_time_ms:.2f} ms | Total Response Time")
    stats_lines.append(f"平均生成字节速率    : {avg_rate:.2f} Byte/S | Average Byte Generation Rate")

    # 设置统计信息标题，确保标题不超出边框 / Set the statistics header ensuring it fits within its border
    header_title = "统计信息 (Statistics)"
    max_line_length = max(max(len(line) for line in stats_lines), len(header_title))
    border = "+" + "-" * (max_line_length + 10) + "+"
    title_line = header_title.center(max_line_length)

    # 输出统计信息标题和统计框 / Output the statistics header and box
    print("\n" + title_line)
    print(border)
    for line in stats_lines:
        print("| " + line.ljust(max_line_length) + " |")
    print(border)

def score_time(measured, ideal, poor):
    """
    对响应时间打分（单位 ms）:
    Score the response time in milliseconds:
      - 如果 measured 小于等于 ideal，则得满分 10 分；
        If measured is less than or equal to ideal, score 10 points;
      - 如果 measured 大于等于 poor，则得 0 分；
        If measured is greater than or equal to poor, score 0;
      - 否则线性下降得分。
        Otherwise, score decreases linearly.
    """
    if measured is None:
        return 0
    if measured <= ideal:
        return 10
    elif measured >= poor:
        return 0
    else:
        return 10 * (poor - measured) / (poor - ideal)

def score_bytes(total_bytes, ideal_bytes=400, min_bytes=40):
    """
    对返回答案的字节长度打分:
    Score the byte length of the returned answer:
      - 如果 total_bytes 小于等于 min_bytes，则得 0 分；
        If total_bytes is less than or equal to min_bytes, score 0;
      - 如果 total_bytes 大于等于 ideal_bytes，则得 10 分；
        If total_bytes is greater than or equal to ideal_bytes, score 10;
      - 否则线性上升得分。
        Otherwise, score increases linearly.
    """
    if total_bytes <= min_bytes:
        return 0
    elif total_bytes >= ideal_bytes:
        return 10
    else:
        return 10 * (total_bytes - min_bytes) / (ideal_bytes - min_bytes)

def score_rate(rate, ideal, poor):
    """
    对平均生成字节速率打分（单位：Byte/秒）:
    Score the average byte generation rate (in Byte/second):
      - 如果 rate 大于等于 ideal，则得满分 10 分；
        If rate is greater than or equal to ideal, score 10;
      - 如果 rate 小于等于 poor，则得 0 分；
        If rate is less than or equal to poor, score 0;
      - 否则线性上升得分。
        Otherwise, score increases linearly.
    """
    if rate >= ideal:
        return 10
    elif rate <= poor:
        return 0
    else:
        return 10 * (rate - poor) / (ideal - poor)

def print_score(overall_score):
    # 输出调用 API 后的速度得分 / Print the API call speed score
    score_box = f"本次调用 API 速度得分 : {overall_score:.2f} / 10.00 | API Speed Score"
    border = "+" + "-" * (len(score_box) + 10) + "+"
    print("\n" + border)
    print("| " + score_box + " |")
    print(border)

def test_api_speed(base_url, headers, model_name, question):
    # 构造完整的 API URL，假设接口路径为 /chat/completions
    # Construct the full API URL, assuming the endpoint is /chat/completions
    endpoint = "/chat/completions"
    url = base_url + endpoint

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": question}
        ],
        "stream": True
    }

    # 输出问题信息 / Print the question information
    print("\n发送给 API 的问题 [Question sent to API]:", question)

    # 计算问题字节长度 (单位 Byte) / Compute the byte length of the question (unit: Byte)
    question_bytes = len(question.encode('utf-8'))

    print("\nAPI 返回答案 [API response]:")

    # 记录开始时间和统计变量 / Record the start time and initialize statistics variables
    start_time = time.time()
    first_byte_time = None
    twenty_byte_time = None
    fifty_byte_time = None  # 记录前50字节响应时间 / Record the time when first 50 bytes are received
    total_bytes = 0

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        # 检查状态码 / Check the response status code
        if response.status_code != 200:
            print("请求错误，状态码 (Request error, status code):", response.status_code)
            return
        response.encoding = 'utf-8'
    except requests.exceptions.RequestException as e:
        print("网络请求发生异常 (Network request exception):", e)
        return

    # 逐行处理返回的流数据 / Process the streamed data line by line
    for line in response.iter_lines(decode_unicode=True):
        if line:
            current_time = time.time()
            # 去掉 "data:" 前缀 / Remove the "data:" prefix
            if line.startswith("data:"):
                line = line[5:].strip()
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue  # 跳过无法解析的行 / Skip lines that cannot be parsed

            # 提取有效文本信息：chunk["choices"][0]["delta"]["content"]
            # Extract the relevant text: chunk["choices"][0]["delta"]["content"]
            choices = chunk.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    # 累计返回内容字节数（UTF-8）
                    # Accumulate the byte length of the returned content (UTF-8)
                    content_bytes = len(content.encode('utf-8'))
                    total_bytes += content_bytes
                    # 实时打印有效文本 / Print the received text in real time
                    sys.stdout.write(content)
                    sys.stdout.flush()

                    # 记录响应的各个阶段的时间 / Record the time of each stage of the response
                    if first_byte_time is None:
                        first_byte_time = current_time
                    if total_bytes >= 20 and twenty_byte_time is None:
                        twenty_byte_time = current_time
                    if total_bytes >= 50 and fifty_byte_time is None:
                        fifty_byte_time = current_time

    print("\n")  # 输出换行 / Print a newline

    # 计算整体响应时间 (ms) / Calculate total response time in milliseconds
    end_time = time.time()
    full_time_ms = (end_time - start_time) * 1000

    # 计算平均生成字节速率 (Byte/秒) / Calculate the average byte generation rate (Byte/second)
    full_time_sec = end_time - start_time
    avg_rate = total_bytes / full_time_sec if full_time_sec > 0 else 0

    # 输出统计信息框, 包括“发送问题字节长度”
    # Print the statistics box, including the question's byte length
    print_statistics_box(url, model_name, total_bytes, question_bytes,
                         first_byte_time, twenty_byte_time, fifty_byte_time,
                         full_time_ms, avg_rate, start_time)

    # === 打分系统 === / === Scoring System ===
    # 根据规则进行打分 / Score based on defined rules
    s1 = score_time((first_byte_time - start_time) * 1000 if first_byte_time else None, ideal=150, poor=2000)
    s2 = score_time((twenty_byte_time - start_time) * 1000 if twenty_byte_time else None, ideal=200, poor=2400)
    s3 = score_time((fifty_byte_time - start_time) * 1000 if fifty_byte_time else None, ideal=350, poor=3000)
    s4 = score_time(full_time_ms, ideal=1000, poor=20000)
    s5 = score_bytes(total_bytes, ideal_bytes=400, min_bytes=40)
    s6 = score_rate(avg_rate, ideal=300, poor=60)

    overall_score = 0.2 * s1 + 0.3 * s2 + 0.15 * s3 + 0.1 * s4 + 0.05 * s5 + 0.2 * s6

    print_score(overall_score)

def main():
    # ☆☆☆在此配置 API URL / Configure your API URL here
    # etc. https://api.siliconflow.cn/v1 https://api.openai-hk.com/v1 https://spark-api-open.xf-yun.com/v1 https://ark.cn-beijing.volces.com/api/v3
    base_url = "https://ark.cn-beijing.volces.com/api/v3"
    headers = {
        "Content-Type": "application/json",
        # ☆☆☆在此配置 API Key，此处注意不要删除 "Bearer " 前缀
        # Configure your API Key here; note: do not remove the "Bearer " prefix.
        "Authorization": "Bearer API Key"
    }
    # ☆☆☆在此配置 model_name
    model_name = "请在程序内输入您的model name"

    print_header("大语言模型接口速度检测工具", "LLM API Speed Detection Tool", "Electronic Sheep", "V1.01","https://github.com/RockstarBin/lasdt")

    print("接口地址 [API URL]: " + base_url + "/chat/completions")
    print("模型名称 [Model Name]: " + model_name)

    while True:
        # 控制台输入问题，若输入 quit 则退出 / Enter a question; type 'quit' to exit
        question = input("\n请输入测试问题[Please enter a test question]或输入 quit 退出[or type 'quit' to exit]: ")
        if question.strip().lower() == "quit":
            print("如遇问题欢迎 issue，再见！[If you encounter issues, feel free to open an issue. Goodbye!]")
            break

        test_api_speed(base_url, headers, model_name, question)

if __name__ == "__main__":
    main()