import random
import yaml
from . import bridge_base


class BridgeCanny(bridge_base.BridgeBase):
    def __init__(self, url, json_path, yaml_path):
        super().__init__(url, json_path, yaml_path)

    def request(self):
        # テキストプロンプトはこのタイミングで読み込む
        with open(self.text_prompt_path, 'r') as f:
            text_prompt = yaml.safe_load(f)
        for level in [ 40, 50, 60 ,70]:
            # パラメータ埋め込み(workflowによって異なる処理)
            self.prompt_path["8"]["inputs"]["text"] = ",".join(text_prompt["prompt"])
            self.prompt_path["10"]["inputs"]["text"] = ",".join(text_prompt["negative"])
            self.prompt_path["6"]["inputs"]["strength"] = level / 100
            self.prompt_path["15"]["inputs"]["seed"] = random.randint(1, 10000000000)
            # リクエスト送信
            response = self.send_request(self.prompt_path)

