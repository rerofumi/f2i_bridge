import importlib.resources
import json
import os
import random
import time

import fm_comfyui_bridge.bridge
import fm_comfyui_bridge.lora_yaml
import yaml


# ComfyUI にアクセスする strategy クラスのベースクラス
class BridgeBase:
    def __init__(self, url, prompt_path, text_prompt_path, mailbox_path):
        self.url = url
        with importlib.resources.open_text("F2iBridgeWorkflow", prompt_path) as f:
            self.prompt_path = json.load(f)
        self.text_prompt_path = text_prompt_path
        self.mailbox_path = mailbox_path
        self.input_image_name = "f2i_input.png"
        self.mask_image_name = "f2i_mask.png"
        self.lora_yaml = fm_comfyui_bridge.lora_yaml.SdLoraYaml()
        self.lora_yaml.read_from_yaml(os.path.join(mailbox_path, "lora.yaml"))
        random.seed(time.time())

    def get_input_image_name(self):
        current_time = int(time.time())
        self.input_image_name = f"f2i_input_{current_time}.png"
        return self.input_image_name

    def get_mask_image_name(self):
        current_time = int(time.time())
        self.mask_image_name = f"f2i_mask_{current_time}.png"
        return self.mask_image_name

    # 画像を準備する
    def prepare_image(self, image=None, mask=None):
        # i2i 画像
        if image is not None:
            fm_comfyui_bridge.bridge.send_image(
                image, upload_name=self.get_input_image_name()
            )
            os.remove(image)
        else:
            image = os.path.join(self.mailbox_path, "request/empty_mask.png")
            fm_comfyui_bridge.bridge.send_image(
                image, upload_name=self.get_input_image_name()
            )
        # mask 画像
        if mask is not None:
            fm_comfyui_bridge.bridge.send_image(
                mask, upload_name=self.get_mask_image_name()
            )
            os.remove(mask)
        else:
            mask = os.path.join(self.mailbox_path, "request/empty_mask.png")
            fm_comfyui_bridge.bridge.send_image(
                mask, upload_name=self.get_mask_image_name()
            )

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
            self.prompt_path["1"]["inputs"]["image"] = self.input_image_name
            self.prompt_path["7"]["inputs"]["text"] = ",".join(text_prompt["prompt"])
            self.prompt_path["8"]["inputs"]["text"] = ",".join(text_prompt["negative"])
            self.prompt_path["13"]["inputs"]["denoise"] = level / 100
            self.prompt_path["13"]["inputs"]["seed"] = random.randint(1, 10000000000)
            self.prompt_path["5"]["inputs"]["seed"] = random.randint(1, 10000000000)
            # リクエスト送信
            self.generate(self.prompt_path, f"fm_f2i_{index:05d}.png")
