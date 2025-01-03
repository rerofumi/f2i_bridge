import os
import shutil

import fm_comfyui_bridge.bridge
import yaml

from F2iBridge import bridge_base


class BridgeImage2ImageRefine(bridge_base.BridgeBase):
    def __init__(self, url, json_path, yaml_path, mailbox_path):
        super().__init__(url, json_path, yaml_path, mailbox_path)

    def prepare_image(self, image=None, mask=None):
        # i2i 画像
        target = os.path.join(self.mailbox_path, "result/fm_f2i_00000.png")
        if image is not None:
            shutil.move(image, target)
        else:
            image = os.path.join(self.mailbox_path, "request/empty_mask.png")
            shutil.move(image, target)

    def request(self):
        # テキストプロンプトはこのタイミングで読み込む
        with open(self.text_prompt_path, "r") as f:
            text_prompt = yaml.safe_load(f)
        # 生成
        target = os.path.join(self.mailbox_path, "result/fm_f2i_00000.png")
        positive = self.lora_yaml.trigger + "," + ",".join(text_prompt["prompt"])
        image = fm_comfyui_bridge.bridge.generate_i2i_highreso(
            positive,
            ",".join(text_prompt["negative"]),
            self.lora_yaml,
            self.lora_yaml.image_size,
            target,
        )
        filename = "fm_f2i_00001.png"
        fm_comfyui_bridge.bridge.save_image(
            image,
            filename=filename,
            workspace=self.mailbox_path,
            output_dir="result",
        )
        print(f"Saved image to {filename}")
