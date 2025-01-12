import os
import time

import click

import F2iBridge.bridge_canny as bridge_canny
import F2iBridge.bridge_i2i as bridge_i2i
import F2iBridge.bridge_i2i_refine as bridge_i2i_refine
import F2iBridge.bridge_inpaint as bridge_inpaint
import F2iBridge.bridge_rewrite_line as bridge_rewrite_line


def main(mailbox_path, url):
    # 監視するディレクトリ
    watch_dir = os.path.join(mailbox_path, "request")
    #
    strategy_i2i = bridge_i2i.BridgeImage2Image(
        url,
        "image2image_api.json",
        os.path.join(mailbox_path, "text_prompt.yaml"),
        mailbox_path,
    )
    strategy_inpaint = bridge_inpaint.BridgeInpaint(
        url,
        "mask_inpaint_api.json",
        os.path.join(mailbox_path, "text_prompt.yaml"),
        mailbox_path,
    )
    strategy_canny = bridge_canny.BridgeCanny(
        url,
        "canny_api.json",
        os.path.join(mailbox_path, "text_prompt.yaml"),
        mailbox_path,
    )
    strategy_lineart = bridge_rewrite_line.BridgeRewriteLine(
        url,
        "canny_api.json",
        os.path.join(mailbox_path, "text_prompt.yaml"),
        mailbox_path,
    )
    strategy_i2i_refine = bridge_i2i_refine.BridgeImage2ImageRefine(
        url,
        "image2image_api.json",
        os.path.join(mailbox_path, "text_prompt.yaml"),
        mailbox_path,
    )
    print(f"watch start: {watch_dir}")
    while True:
        time.sleep(1)
        processer = None
        # 1. i2i パターン
        # ファイルの確認
        if os.path.exists(f"{watch_dir}/f2i_input.png"):
            time.sleep(3)
            if os.path.exists(f"{watch_dir}/f2i_mask.png"):
                print("----------")
                print("inpaint start")
                processer = strategy_inpaint
                processer.prepare_image(
                    image=f"{watch_dir}/f2i_input.png", mask=f"{watch_dir}/f2i_mask.png"
                )
            else:
                print("----------")
                print("i2i start")
                processer = strategy_i2i
                processer.prepare_image(image=f"{watch_dir}/f2i_input.png")
        # 2. lineart パターン
        if os.path.exists(f"{watch_dir}/f2i_lineart.png"):
            print("----------")
            print("lineart start")
            time.sleep(3)
            processer = strategy_lineart
            processer.prepare_image(image=f"{watch_dir}/f2i_lineart.png")
        # 3. canny パターン
        if os.path.exists(f"{watch_dir}/f2i_canny.png"):
            print("----------")
            print("canny start")
            time.sleep(3)
            processer = strategy_canny
            processer.prepare_image(image=f"{watch_dir}/f2i_canny.png")
        # 4. i2i refine パターン
        if os.path.exists(f"{watch_dir}/f2i_refine.png"):
            print("----------")
            print("i2i refine start")
            time.sleep(3)
            processer = strategy_i2i_refine
            processer.prepare_image(image=f"{watch_dir}/f2i_refine.png")
        #
        if processer is None:
            continue
        # 実行
        processer.request()
        print("end")


# CLI main function
@click.command("F2iBridge", help="Image2Image supporter")
@click.option(
    "-m", "--mailbox", default="./MailBox", help="mailBox directory path", type=str
)
@click.option(
    "-h",
    "--host",
    default="http://localhost:8188/",
    help="ComfyUI API address",
    type=str,
)
def run(mailbox: str, host: str):
    main(mailbox, host)
