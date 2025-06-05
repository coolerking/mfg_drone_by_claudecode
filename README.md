# MFG ドローン - 自動追従撮影システム

Tello EDU ドローンを使って移動する対象物を自動的に追跡・撮影するシステムです。

## 概要

このシステムは以下の3つの主要コンポーネントで構成されています:

1. **バックエンドAPI** (Raspberry Pi 5)
   - ドローン制御
   - ビデオ処理
   - 物体認識と追跡

2. **管理者用フロントエンド** (Windows PC)
   - 物体認識モデルのトレーニング
   - ドローン制御
   - 追跡開始/停止

3. **一般ユーザー用フロントエンド** (Windows PC)
   - ドローンからのリアルタイム映像表示

## 機能要件

1. 対象物の学習および認識機能
   - 画像を取得して学習する
   - 学習した画像を元に対象物を認識する

2. 対象物を画面の中心に捉えるようにTello EDUを動かす機能
   - Tello EDUを動かすためのコマンドを生成して送信する

3. Tello EDUのカメラから取得した画像を参照する機能
   - Tello EDUのカメラから取得した画像をほぼリアルタイムで参照できるようにWebアプリケーションとして提供する

## 非機能要件

- ネットワーク
  - 家庭用ルータに接続するものとする
  - インターネット接続可能
  - 一般ユーザのデバイスは同一ネットワーク上に存在するものとする

- 対象とするドローン
  - [Tello EDU](https://www.ryzerobotics.com/jp/tello-edu)

- ドローンからの画像を受信し、AIモデルをもとに次の行動を決定、指示をドローンに送信するバックエンドシステム（APIサーバ）
  - [Raspberry Pi 5 8MB](https://www.raspberrypi.com/products/raspberry-pi-5/)
    - [Raspberry Pi OS Lite 64bit May 6th 2025](https://www.raspberrypi.com/software/operating-systems/)
      - [Python 3.11](https://www.python.org/downloads/release/python-3110/)
        - [FastAPI](https://fastapi.tiangolo.com/ja/)
        - [djitellopy](https://github.com/damiafuentes/DJITelloPy)

- ドローンの撮影動画を受信しユーザに見せるための一般ユーザ用フロントエンドシステム
  - Windows11 Pro 64bit
    - [Python 3.11](https://www.python.org/downloads/release/python-3110/)
      - [Flask](https://flask.palletsprojects.com/en/2.3.x/)

- ドローンに撮影対象を学習させたり、追従開始・停止を指示するための管理者用フロントエンドシステム
  - Windows11 Pro 64bit
    - [Python 3.11](https://www.python.org/downloads/release/python-3110/)
      - [Flask](https://flask.palletsprojects.com/en/2.3.x/)

- 一般ユーザクライアント
  - iPad Air 13インチ第5世代
    - iOS 17.0.3
      - Safari

> 2つのフロントエンドシステムは同一のPCで動作する


