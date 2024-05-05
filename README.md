# プロジェクト名

"File to Image generator Bridge"

## 概要

ディレクトリを監視しファイルが置かれたらそのファイルを ComfyUI に投げる、シンプルなサポートプログラム。

- 規定の Mailbox ディレクトリに特定名の起動ファイルを置かれたらそれを元画に画像生成開始
- 生成結果は同じくメールボックスディレクトリの下に既定のファイル名で置かれる
- 生成依頼画像のファイル名によって生成機能の呼び分け
- 生成結果は毎回同じファイル名なのでペイントツールのレイヤー読み込みを、マクロ・アクションなどで省力化することが可能
- i2i や controlnet 等の強度を変えつつ 4枚生成するので、絵の方向性模索ができる

## 必要なもの

- 実行環境
  - Python
    - Windows 版の Python 3.10 で作成
  - python pip モジュール
    - 以下を使用、pip で予め入れておくか venv を作ってそこの pip で install
    - requests
    - yaml
  - ComfyUI 実行環境
    - ComfyUI を API 経由で呼び出すので、ComfiUI が動く環境を構築できること
- 各種学習済みモデル
  - ComfyUI のワークフローモデル内で以下を使用
    - 必要に応じて同じ真名を揃えたり、自分の好みの奴に差し替える
  - SDXLモデル
    - AnythingXL_xl.safetensors
  - Controlnetモデル
    - sai_xl_canny_256lora.safetensors
  - embbeding
    - negativeXL_D.safetensors
    - Text prompt 内で指定する形なので用意しなくても良い
- その他
  - PNGファイルを読み書きできるペイントツール

## インストール方法

1. f2i_bridge のリポジトリを clone する
2. f2i_bridge の『直下』に ComfyUI を clone して起動する様に整備する
    1. `./ComfyUI/input`, `./ComfyUI/output` のパスで画像をやりとりするのでパスを合わせること
    2. workflow で使っているモデルを ComfyUI の model 下に配置する
3. f2i_bridge が使うモジュールを必要に応じてインストールする
    ```
    pip install requests yaml
    ```


## 使い方

ペイントツールで元画を用意して Mailbox ディレクトリの下に特定のファイル名で保存する。
しばらく待つと Mailbox ディレクトリの下に画像が生成されるので、それをペイントツールのレイヤーに読み込んで利用する。

### 起動

1. ComfyUI を起動する、`127.0.0.1:8188` で待ち受けている状態にすること
2. ComfyUI GUI は使わないのでブラウザが起動しても、閉じてしまって良い
3. `python f2i_bridge.py` でブリッジを起動、待ち受け状態にする

### 準備

- これから描きたい絵のテキストプロンプトを `./Mailbox/text_prompt.yaml` に記述する
    - テキストプロンプトだけでおおよそ求める風貌が出力されているのが望ましい
- 学習済みモデルを任意の物にしたい時は ComfyUI に設定しておく
    - Workflow ディレクトリ内の `*_api.json` をエディタで編集し `AnythingXL_xl.safetensors`, `sai_xl_canny_256lora.safetensors` の部分を使いたいモデルで置き換える
- `embedding` が使いたいときは ComfyUI で設定して、テキストプロンプトの中で指定する

### 基本的な使い方

- `./Mailbox/request/` の下に入力画像を規定のファイルネームで作成することで生成が開始される
- トリガーとなるファイル名は以下の 3つ
  - `f2i_input.png`
  - `f2i_lineart.png`
  - `f2i_canny.png`
- 生成が完了すると `./Mailbox/result/` 以下に生成画像が置かれる
- 生成画像のファイル名は基本以下で固定
  - `fm_f2i_00001_.png`
  - `fm_f2i_00002_.png`
  - `fm_f2i_00003_.png`
  - `fm_f2i_00004_.png`
- 入力＆生成画像のサイズは基本 1024x1024 pixel
  - 入力画像サイズで出力の大きさが決まるので 1024x1024 以上の非正方形でも大丈夫
- テキストプロンプトは生成依頼をするタイミングで読みこんでいるので、f2i_bridge を起動したまま編集しても反映される

### 機能別説明

#### 線画生成

線画で描かれたラフ絵をベースに近い構図でモノクロの線画を生成する。
内部的には Controlnet canny を使用しており、白地に濃い色の線での描画が最も良い結果を出力する。

入力画像として `f2i_lineart.png` というファイルネームの画像を置くことで実行される。

![lineart sample](/picture/fig_lineart.png "lineart generate")

#### Controlnet I2I (Canny)

入力画像の境界線を抽出(canny)して、その構図をヒントに生成する。
線画生成とやっていることは同じだがモノクロ線画を prompt に加えてないため、おおよそカラー彩色済みの結果が出力される。

入力画像として `f2i_canny.png` というファイルネームの画像を置くことで実行される。

![canny sample](/picture/fig_controlnet_canny.png "conirolnet(canny) generate")

#### Mask Inpaint

入力画像とマスク画像の 2つを入力し、マスク画像の非透明部分領域のみに生成を行う。
マスク画像は透過PNGで作成すること。

マスク画像 `f2i_mask.png` と入力画像 `f2i_input.png` の両方を置くことで実行される。
`f2i_input.png` の存在を見て実行が走るので、マスクを先に置いて input の方を後で置くこと。

![inpaint sample](/picture/fig_inpaint.png "inpaint generate")

#### Image2Image

mask画像を置かずに `f2i_input.png` のみの設置で通常の i2i 相当を出力する。
canny より出力のブレが大きく、テキストプロンプトに強く依存する。

![i2i sample](/picture/fig_i2i.png "i2i generate")


### 便利な使い方

- 生成画像の読み込みをオートアクションに登録する
    - clip studio paint では "ファイル>読み込み>画像" でレイヤーに画像を読み込みできるし、このとき複数画像を一遍に選択できる
    - それでも大した労力ではないが、上記作業をオートアクションに登録しておくとワンクリックで実行できるため使い勝手が向上する
    - オートアクションをさらにクイックアクセスに登録するとさらにクリック回数が減る
    - セーブはどうしてもファイル名入力が間に挟まるためオートアクション化できなかった、残念

### テキストプロンプト書式

`./Mailbox/text_prompt.yaml` は yaml 形式のファイルで以下の様な内容になっている

```
prompt:
  - "1girl, female lion ear and tail, open mouth, fang, yellow bob hair, sailor school wear"
  - "front view, hands up to face side, wild finger pose, smile"
negative:
  - "furry, chemo, chibi"
  - "embedding:negativeXL_D"
```

`prompt:` と `negative:` の 2つのオブジェクトで、その階層は "-" で連なる配列になっている。
`  - "～"` の部分(頭に2つの空白)はいくつ書き連ねても大丈夫で内部ではひとかたまりのプロンプトとして扱われる。


## ライセンス

MIT licence.

## 作者情報

rerofumi

## 変更履歴

- May.05.2024
    - first release
