import random

import yaml

from F2iBridge import bridge_base


class BridgeCanny(bridge_base.BridgeBase):
    def __init__(self, url, json_path, yaml_path, mailbox_path):
        super().__init__(url, json_path, yaml_path, mailbox_path)

    def request(self):
        # テキストプロンプトはこのタイミングで読み込む
        with open(self.text_prompt_path, "r") as f:
            text_prompt = yaml.safe_load(f)
        for index, level in enumerate([40, 50, 60, 70]):
            # パラメータ埋め込み(workflowによって異なる処理)
            self.prompt_path["3"]["inputs"]["image"] = self.input_image_name
            self.prompt_path["8"]["inputs"]["text"] = ",".join(text_prompt["prompt"])
            self.prompt_path["10"]["inputs"]["text"] = ",".join(text_prompt["negative"])
            self.prompt_path["26"]["inputs"]["strength"] = level / 100
            self.prompt_path["15"]["inputs"]["seed"] = random.randint(1, 10000000000)
            self.prompt_path["14"]["inputs"]["ckpt_name"] = self.lora_yaml.checkpoint
            # リクエスト送信
            self.generate(self.prompt_path, f"fm_f2i_{index:05d}.png")
