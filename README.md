# 大语言模型接口速度检测工具 / LLM API Speed Detection Tool

## 项目介绍 (Project Overview)
本工具用于测试和评估大语言模型 API 的响应速度。程序通过向 API 发送测试问题，并实时显示流式返回的响应，同时收集详细的性能指标（如首字节响应时间、前20/50字节响应时间、总响应时间和平均生成字节速率）。最终，根据预定义的规则计算一个综合性能打分。  
This tool is designed to test and evaluate the response speed of large language model APIs. It sends a test query to an API, displays the streaming response in real time, and collects detailed performance metrics (such as time-to-first-byte, response times for the first 20/50 bytes, total response time, and average byte generation rate) to ultimately calculate an overall performance score.

---

## 特性 (Features)
- **实时流数据展示 / Real-Time Streaming:** 程序在接收到数据时立即打印，便于观察响应过程。  
  The tool prints data as it streams in, allowing you to monitor the response in real time.
  
- **详细性能指标 / Detailed Performance Metrics:** 包括接口地址、模型名称、发送问题字节长度、返回答案字节长度、各阶段响应速度及总体响应时间。  
  It records metrics like API URL, model name, the byte length of the query and answer, time to first byte, time for the first 20/50 bytes, and total response time.
  
- **性能打分系统 / Performance Scoring System:** 根据响应时间和字节速率等指标，通过线性比例计算得分，为 API 响应提供量化评估。  
  The scoring system evaluates performance based on response times and byte rates using linear scaling to provide a quantitative assessment of API performance.
  
- **中英双语支持 / Bilingual Support:** 所有注释、消息和文档均提供中文及英文说明，方便国内外用户理解。  
  All comments, messages, and documentation are provided in both Chinese and English for ease of use by users worldwide.

- **多轮对话支持 / Multi round dialogue support:** 支持多轮对话，用户可以灵活使用大语言模型提问并获取答案。  
  Supporting multiple rounds of dialogue, users can flexibly use the big language model to ask questions and obtain answers.
  
---

## 使用说明 (Usage Instructions)

### 1. 部署 Python3 环境 / Setting Up a Python3 Environment
- **检查是否安装 Python 3:**  
  Open your terminal or command prompt and run:
  ```bash
  python3 --version
如果显示版本号（例如 Python 3.12.X），则说明已安装；否则需要从 Python官网下载 并安装。
(If a version number like Python 3.12.X is displayed, Python 3 is already installed; otherwise, download and install it from the official Python website.)

创建虚拟环境（推荐）:
在项目根目录下执行以下命令以创建并激活虚拟环境：

- ### 创建虚拟环境 (Create a virtual environment)
  ```bash
  python3 -m venv venv
- ### 在 macOS/Linux 上激活虚拟环境 (Activate on macOS/Linux)
  ```bash
  source venv/bin/activate
- ### 在 Windows 上激活虚拟环境 (Activate on Windows)
  ```bash
  venv\Scripts\activate
### 虚拟环境可以隔离项目依赖，确保不与系统的其他 Python 包冲突。
(A virtual environment isolates project dependencies, ensuring they do not conflict with other system-wide Python packages.)

安装项目依赖:
- 在虚拟环境中，通过 pip 安装依赖：
  ```bash
  pip install requests
(Within the virtual environment, install the required dependencies using pip.)

2. 配置接口地址和 API Key / Configuring API URL and API Key
打开脚本文件（例如 LASDT.py）。
以下三行代码进行替换：

- Python
  ```bash

  base_url = "https://api.siliconflow.cn/v1"  # line 245

  "Authorization": "Bearer YourAPIKeyHere"  # line 250

  model_name = "Qwen/Qwen2.5-7B-Instruct"  # line 253

以下三个步骤是必须的：

①将 base_url 修改为您所使用的 API 服务器地址。
①Change base_url to the API server URL you are using.

②替换 headers["Authorization"] 中的 YourAPIKeyHere 为实际的 API Key，并保持 "Bearer " 前缀不变。
②Replace sk-YourAPIKeyHere with your actual API Key (keep the "Bearer " prefix unchanged).

③修改 model_name 为您所使用的模型名称。
③Optionally, update model_name to match the model you wish to call.

3. 运行程序 / Running the Program
确保您的 Python 环境已正确配置，并安装了 requests 库。
Make sure your Python environment is set up and the requests library is installed (see step 1).
- 在命令行中运行程序：

  ```bash
  python LASDT.py

根据提示输入测试问题，随后程序将显示 API 的实时流数据及相关统计信息。
Follow the prompts to enter a test query, and the program will display the streaming API response along with performance metrics.

---

## 打分系统说明 (Scoring System Explanation)
程序根据以下指标为 API 响应打分，每项满分为 10 分，总分根据各项权重加权计算。

首字节响应时间 (Time to First Byte):

如果响应时间 ≤ 150ms，则得 10 分；
If the response time is ≤ 150ms, it scores 10 points.
如果响应时间 ≥ 2000ms，则得 0 分；
If the response time is ≥ 2000ms, it scores 0 points.
否则按线性方式计算得分。
Otherwise, the score is calculated linearly between these bounds.
前20个字节响应时间 (Response Time for First 20 Bytes):

如果响应时间 ≤ 200ms，则得 10 分；
If the response time is ≤ 200ms, it scores 10 points.
如果响应时间 ≥ 2400ms，则得 0 分；
If the response time is ≥ 2400ms, it scores 0 points.
否则按线性衰减计算得分。
Otherwise, the score is decreased linearly between these bounds.
前50个字节响应时间 (Response Time for First 50 Bytes):

如果响应时间 ≤ 350ms，则得 10 分；
If the response time is ≤ 350ms, it scores 10 points.
如果响应时间 ≥ 3000ms，则得 0 分；
If the response time is ≥ 3000ms, it scores 0 points.
否则按线性方式计算得分。
Otherwise, the score is calculated linearly between these bounds.
全部回答响应时间 (Total Response Time):

如果响应时间 ≤ 1000ms，则得 10 分；
If the total response time is ≤ 2000ms, it scores 10 points.
如果响应时间 ≥ 20000ms，则得 0 分；
If the response time is ≥ 12000ms, it scores 0 points.
否则按比例计算得分。
Otherwise, the score is calculated proportionally.
返回答案字节数 (Answer Byte Length):

如果字节数 ≤ 40，则得 0 分；
If the byte length is ≤ 40, it scores 0 points.
如果字节数 ≥ 400，则得 10 分；
If the byte length is ≥ 400, it scores 10 points.
否则按线性方式计算得分。
Otherwise, the score increases linearly.
平均生成字节速率 (Average Byte Generation Rate):

如果速率 ≥ 300 Byte/sec，则得 10 分；
If the generation rate is ≥ 300 Byte/sec, it scores 10 points.
如果速率 ≤ 60 Byte/sec，则得 0 分；
If the generation rate is ≤ 60 Byte/sec, it scores 0 points.
否则按线性方式计算得分。
Otherwise, the score is calculated linearly.
各项得分依据以下权重汇总计算为最终综合得分：
The final overall score is computed as the weighted sum of the individual scores:

首字节响应时间: 20%
Time to First Byte: 20%
前20个字节响应时间: 30%
Time for First 20 Bytes: 30%
前50个字节响应时间: 15%
Time for First 50 Bytes: 15%
全部回答响应时间: 10%
Total Response Time: 10%
返回答案字节数: 5%
Answer Byte Length: 5%
平均生成字节速率: 20%
Average Byte Generation Rate: 20%

---

## 贡献 (Contributing)
欢迎任何形式的贡献，包括错误反馈、功能建议及代码优化。请通过提交 Pull Request 或在 Issue 中讨论来共享您的想法。
Contributions are welcome in the form of bug reports, feature suggestions, or code optimizations. Feel free to share your thoughts by submitting a pull request or opening an issue.

---

## 许可协议 (License)
本项目采用 MIT 许可证。
This project is licensed under the MIT License.

---

## 联系方式 (Contact)
如有任何疑问或建议，请联系项目维护者。
If you have any questions or suggestions, please contact the project maintainer.
```
