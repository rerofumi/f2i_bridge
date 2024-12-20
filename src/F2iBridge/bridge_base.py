import importlib.resources
import json
import os
import random
import time

import fm_comfyui_bridge.bridge
import yaml


# ComfyUI にアクセスする strategy クラスのベースクラス
class BridgeBase:
    def __init__(self, url, prompt_path, text_prompt_path, mailbox_path):
        self.url = url
        with importlib.resources.open_text("Workflow", prompt_path) as f:
            self.prompt_path = json.load(f)
        self.text_prompt_path = text_prompt_path
        self.mailbox_path = mailbox_path
        random.seed(time.time())

    # 画像を準備する
    def prepare_image(self, image=None, mask=None):
        # i2i 画像
        if image is not None:
            fm_comfyui_bridge.bridge.send_image(image, upload_name="f2i_input.png")
            os.remove(image)
        else:
            image = os.path.join(self.mailbox_path, "request/empty_mask.png")
            fm_comfyui_bridge.bridge.send_image(image, upload_name="f2i_input.png")
        # mask 画像
        if mask is not None:
            fm_comfyui_bridge.bridge.send_image(mask, upload_name="f2i_mask.png")
            os.remove(mask)
        else:
            mask = os.path.join(self.mailbox_path, "request/empty_mask.png")
            fm_comfyui_bridge.bridge.send_image(mask, upload_name="f2i_mask.png")

    def generate(self, prompt, filename, output_node="19"):
        id = fm_comfyui_bridge.bridge.send_request(prompt)
        if id:
            fm_comfyui_bridge.bridge.await_request(1, 3)
            image = fm_comfyui_bridge.bridge.get_image(id, output_node=output_node)
            fm_comfyui_bridge.bridge.save_image(
                image,
                filename=filename,
                workspace=self.mailbox_path,
                output_dir="result",
            )
            print(f"Saved image to {filename}")
        else:
            return None

    def request(self):
        # テキストプロンプトはこのタイミングで読み込む
        with open(self.text_prompt_path, "r") as f:
            text_prompt = yaml.safe_load(f)
        for index, level in enumerate([40, 50, 60, 70]):
            # パラメータ埋め込み(workflowによって異なる処理)
            self.prompt_path["7"]["inputs"]["text"] = ",".join(text_prompt["prompt"])
            self.prompt_path["8"]["inputs"]["text"] = ",".join(text_prompt["negative"])
            self.prompt_path["13"]["inputs"]["denoise"] = level / 100
            self.prompt_path["13"]["inputs"]["seed"] = random.randint(1, 10000000000)
            self.prompt_path["5"]["inputs"]["seed"] = random.randint(1, 10000000000)
            # リクエスト送信
            self.generate(self.prompt_path, f"fm_f2i_{index:05d}.png")
