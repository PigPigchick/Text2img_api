import requests
import json
import pandas as pd
import xlsxwriter
from os.path import join, realpath, dirname
import time
import os

API_KEY = ""
SECRET_KEY = ""
root_path = dirname(realpath(__file__))
prompt_path = join(root_path, 'input.xlsx')
res_path = join(root_path, '文心一格')

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

# 存储结果到excel中
def to_excel(prompt):
    wb = xlsxwriter.Workbook('文心一格.xlsx')
    ws = wb.add_worksheet('Sheet1')
    ws.set_column('D:D', 28.5)
    title_format = wb.add_format({'bold': False, 'font_size': 11, 'align': 'center'})
    ws.write('D1','生成图片',title_format)
    for k in range(len(prompt)):
        ws.set_row(k+1, 160)
        ws.insert_image('D' + str(k+2), res_path+f'/{k+1}.png', {'x_scale': 0.2, 'y_scale': 0.2})
    wb.close()

def wenxinyige(prompts):

    #prompts = ["两名选手一起跑步冲过终点线"]
    url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2imgv2?access_token=" + get_access_token()
    for prompt in prompts:
        # 提交请求
        payload = json.dumps({
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "image_num": 1
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        s = response.json()
        res_id.append(s['data']['task_id'])
        time.sleep(8)
    print(res_id)

def output_img():
    #res_id = ['1727937239739167539']
    url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImgv2?access_token=" + get_access_token()
    i = 1
    if not os.path.exists(res_path):
        os.mkdir(res_path)
    for out in res_id:
        payload = json.dumps({
            "task_id": str(out)
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        s = response.json()
        print(s)
        pic = s['data']['sub_task_result_list'][0]['final_image_list'][0]['img_url']
        with open(res_path+f'/{i}.png', 'wb+') as f:
            f.write(requests.get(pic).content)
        i = i+1

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

if __name__ == '__main__':

    print("文心一格：获取提示词中...")
    prompts = get_prompts()

    print("文心一格：请求生成图片中...")
    wenxinyige(prompts)

    time.sleep(len(prompts)*5)

    print("文心一格：获取图片中...")
    output_img()

    print("文心一格：生图完毕！！！")