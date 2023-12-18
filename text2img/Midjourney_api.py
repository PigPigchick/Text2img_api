import http.client
import json
import pandas as pd
import xlsxwriter
import requests
import time
from os.path import join, realpath, dirname
import os

root_path = dirname(realpath(__file__))
prompt_path = join(root_path, 'input.xlsx')
res_path = join(root_path, 'Midjourney')

res_id = []

# 读取prompt：从excel中读取一列prompt
def get_prompts():
    df = pd.read_excel(prompt_path,header=0)  # 读取项目名称列,不要列名
    df_li = df.values.tolist()
    result = []
    for s_li in df_li:
        result.append(s_li[0])
    print(result)
    return result

def Mid_request(prompts):

    for prompt in prompts:
        conn = http.client.HTTPSConnection("ai.huashi6.com")
        payload = json.dumps({
            "prompt": prompt,
            "type": "fast"
        })
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json',
            'Auth-Token': 'wlKVCDTd43yArNXNtTxFvAmeKbe6uQY8'
        }
        conn.request("POST", "/aiapi/v1/mj/draw", payload, headers)
        res = conn.getresponse()
        data = res.read()
        data = data.decode("utf-8")
        jsonData = json.loads(data)
        print(jsonData)
        res_id.append(jsonData['data']['paintingSign'])


def Mid_response():

    i = 1
    if not os.path.exists(res_path):
        os.mkdir(res_path)
    for id in res_id:
        conn = http.client.HTTPSConnection("ai.huashi6.com")
        payload = json.dumps({
            "taskId": str(id)
        })
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json',
            'Auth-Token': ''
        }
        conn.request("POST", "/aiapi/v1/mj/task/progress", payload, headers)
        res = conn.getresponse()
        data = res.read()
        data = data.decode("utf-8")
        jsonData = json.loads(data)
        print(jsonData)
        pic = jsonData['data']['images'][0]['imageUrl']
        with open(res_path + f'/{i}.png', 'wb+') as f:
            f.write(requests.get(pic).content)
        i = i + 1

if __name__ == '__main__':

    print("Midjourney：获取提示词中...")
    prompts = get_prompts()

    #prompts = ["一个女孩"]
    print("Midjourney：请求生成图片中...")
    Mid_request(prompts)

    time.sleep(len(prompts)*50)

    print("Midjourney：获取图片中...")
    Mid_response()

    print("Midjourney：生图完毕！！！")
    