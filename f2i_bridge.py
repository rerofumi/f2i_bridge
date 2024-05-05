import os
import time
from bridge_src import bridge_inpaint
from bridge_src import bridge_i2i
from bridge_src import bridge_rewrite_line
from bridge_src import bridge_canny

# ComfyUI の API エンドポイント
url = 'http://localhost:8188/'

# 監視するディレクトリ
watch_dir = './Mailbox/request'

def main():
    strategy_i2i = bridge_i2i.BridgeImage2Image(url, "./Workflow/image2image_api.json", "./Mailbox/text_prompt.yaml")
    strategy_inpaint = bridge_inpaint.BridgeInpaint(url, "./Workflow/mask_inpaint_api.json", "./Mailbox/text_prompt.yaml")
    strategy_canny = bridge_canny.BridgeCanny(url, "./Workflow/canny_api.json", "./Mailbox/text_prompt.yaml")
    strategy_lineart = bridge_rewrite_line.BridgeRewriteLine(url, "./Workflow/canny_api.json", "./Mailbox/text_prompt.yaml")
    print("watch start")
    while True:
        time.sleep(1)
        prepare = False
        processer = None
        # 1. i2i パターン
        # ファイルの確認
        if os.path.exists(f"{watch_dir}/f2i_input.png"):
            time.sleep(3)
            if os.path.exists(f"{watch_dir}/f2i_mask.png"):
                print("inpaint start")
                processer = strategy_inpaint
                prepare = processer.prepare_image(image=f"{watch_dir}/f2i_input.png", mask=f"{watch_dir}/f2i_mask.png")
            else:
                print("i2i start")
                processer = strategy_i2i
                prepare = processer.prepare_image(image=f"{watch_dir}/f2i_input.png")
        # 2. lineart パターン
        if os.path.exists(f"{watch_dir}/f2i_lineart.png"):
            print("lineart start")
            time.sleep(3)
            processer = strategy_lineart
            prepare = processer.prepare_image(image=f"{watch_dir}/f2i_lineart.png")
        # 3. canny パターン
        if os.path.exists(f"{watch_dir}/f2i_canny.png"):
            print("canny start")
            time.sleep(3)
            processer = strategy_canny
            prepare = processer.prepare_image(image=f"{watch_dir}/f2i_canny.png")
        #
        if processer is None:
            continue
        #
        # 実行
        if prepare:
            try:
                processer.request()
                processer.await_request()
                processer.get_image("./Mailbox/result")
                print("end")
            except:
                print("request failed")
        else:
            print("prepare_image failed")


if __name__ == '__main__':
    main()

