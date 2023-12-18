from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
import dashscope
import pandas as pd
import os
import xlsxwriter
from os.path import join, realpath, dirname
import parsel
import json

dashscope.api_key=""
root_path = dirname(realpath(__file__))
prompt_path = join(root_path, 'input.xlsx')
res_path = join(root_path, '通义万相')

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
    wb = xlsxwriter.Workbook('通义万相.xlsx')
    ws = wb.add_worksheet('Sheet1')
    ws.set_column('D:D', 28.5)
    title_format = wb.add_format({'bold': False, 'font_size': 11, 'align': 'center'})
    ws.write('D1','生成图片',title_format)
    for k in range(len(prompt)):
        ws.set_row(k+1, 160)
        ws.insert_image('D' + str(k+2), res_path+f'/{k+1}.png', {'x_scale': 0.2, 'y_scale': 0.2})
    wb.close()

# 通义万相
def tongyiwanxiang(prompts):
    i = 1 # 图片索引命名
    if not os.path.exists(res_path):
        os.mkdir(res_path)
    for prompt in prompts:
        #prompt = 'Mouse rides elephant'
        rsp = dashscope.ImageSynthesis.call(model=dashscope.ImageSynthesis.Models.wanx_v1,
                                prompt=prompt,
                                n=1,
                                size='1024*1024')
        if rsp.status_code == HTTPStatus.OK:
            for result in rsp.output.results:
                file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
                with open(res_path+f'/{i}.png', 'wb+') as f:
                    f.write(requests.get(result.url).content)
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                (rsp.status_code, rsp.code, rsp.message))
        i = i+1


if __name__ == '__main__':

    print("通义万相：获取提示词中...")
    prompts = get_prompts()  # 获取所有prompt

    print("通义万相：生成图片中...")
    tongyiwanxiang(prompts)
    print("通义万相：生图完毕！！！")

    #to_excel(prompts)
    
