import json
import random
import shutil
import time
import yaml
import os
import glob
import requests

COMFYUI_INPUT_PATH = "./ComfyUI/input"
COMFYUI_OUTPUT_PATH = "./ComfyUI/output"

# ComfyUI にアクセスする strategy クラスのベースクラス
class BridgeBase():
    def __init__(self, url, prompt_path, text_prompt_path):
        self.url = url
        with open(prompt_path, 'r', encoding='utf-8') as f:
          self.prompt_path = json.load(f)
        self.text_prompt_path = text_prompt_path
        random.seed(time.time())

    # 画像を準備する
    def prepare_image(self, image=None, mask=None):
        counter = 3
        while counter > 0:
            try:
                if os.path.exists(COMFYUI_INPUT_PATH + "/f2i_input.png"):
                    os.remove(COMFYUI_INPUT_PATH + "/f2i_input.png")
                if image is not None:
                    os.rename(image, COMFYUI_INPUT_PATH + "/f2i_input.png")
                else:
                    shutil.copy("./Mailbox/request/empty_mask.png", COMFYUI_INPUT_PATH + "/f2i_input.png")
                if os.path.exists(COMFYUI_INPUT_PATH + "/f2i_mask.png"):
                    os.remove(COMFYUI_INPUT_PATH + "/f2i_mask.png")
                if mask is not None:
                    os.rename(mask, COMFYUI_INPUT_PATH + "/f2i_mask.png")
                else:
                    shutil.copy("./Mailbox/request/empty_mask.png", COMFYUI_INPUT_PATH + "/f2i_mask.png")
                break
            except:
                print("retry prepare_image")
                counter -= 1
                time.sleep(5)
                continue
        return (counter > 0)

    # 画像を取得する
    def get_image(self, result_path):
        files = glob.glob(f"{COMFYUI_OUTPUT_PATH}/fm_f2i_*.png")
        for file in files:
            image = os.path.basename(file)
            # 既に存在する場合は削除
            if os.path.exists(f"{result_path}/{image}"):
                os.remove(f"{result_path}/{image}")
            os.rename(file, f"{result_path}/{image}")

    def request(self):
        # テキストプロンプトはこのタイミングで読み込む
        with open(self.text_prompt_path, 'r') as f:
            text_prompt = yaml.safe_load(f)
        for level in [ 40, 50, 60 ,70]:
            # パラメータ埋め込み(workflowによって異なる処理)
            self.prompt_path["7"]["inputs"]["text"] = ",".join(text_prompt["prompt"])
            self.prompt_path["8"]["inputs"]["text"] = ",".join(text_prompt["negative"])
            self.prompt_path["13"]["inputs"]["denoise"] = level / 100
            self.prompt_path["13"]["inputs"]["seed"] = random.randint(1, 10000000000)
            self.prompt_path["5"]["inputs"]["seed"] = random.randint(1, 10000000000)
            # リクエスト送信
            response = self.send_request(self.prompt_path)

    def send_request(self, prompt):
        headers = {'Content-Type': 'application/json'}
        data = { "prompt": prompt }
        response = requests.post(f"{self.url}prompt", headers=headers, data=json.dumps(data).encode('utf-8'))
        return response

    def await_request(self):
        # 1秒ごとにリクエストの状態を確認
        while True:
            time.sleep(1)
            headers = {'Content-Type': 'application/json'}
            response = requests.get(f"{self.url}queue", headers=headers)
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                time.sleep(3)
                continue
            json_data = response.json()
            # json の queue_running, queue_pending が存在し、 list 長が両方 0 の場合は break
            if len(json_data["queue_running"]) == 0 and len(json_data["queue_pending"]) == 0:
                break


