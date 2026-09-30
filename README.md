# Android GApps Patcher - TAB-A04-BR3 チャレンジタッチ3のAndroidシステムイメージへGAppsを自動展開・適用するLinux用GUIツール

## 【重要なお知らせと免責事項】
本ツールを使用した場合、以下の条件にすべて同意したものとみなされます。

1. 本ツールはAndroidシステムのパーティション書き換えを行う高度なツールです。
2. 誤った操作や不具合により、デバイスが起動しなくなる（文鎮化する）等の重大なリスクがあります。
3. 本ツールの使用によるいかなるデータの損失、機器の破損・損害についても、作者は一切の責任を負いません。すべて自己責任でご利用ください。
4. 本ツールを使用するにあたっては、以下の条件を必ず満たしていることをご確認ください：
   - **adb、fastboot、MTKClient** のすべてのツールが正常に使用できること。
     - 特に MTKClient は依存関係が複雑かつAndroidの深いシステム階層を扱うため、万が一 fastboot が失敗した際に復旧手段がないと文鎮化します。
   - 重要なパーティション（できればすべてのパーティション）のバックアップを事前に取得しておくこと。
   - パソコンおよびAndroidのシステム構造に関する十分な知識があること。
5. 作者の検証環境は **Python 3.12 / Zorin OS 18.1** です。
   - Ubuntuベース向けに構築されているため、他のLinuxディストリビューションでは正常に動作しない場合があります（※Linux Mint等ではマウントが読み込み専用になる挙動が確認されているため、Zorin OSの利用を強く推奨します）。

---

## 概要
Linux環境下で、Androidの `system.img` に対して OpenGApps などの ZIP パッケージ（内部の `.tar.lz`）を自動展開し、適切なシステムディレクトリ（`app` / `priv-app` / `etc` / `framework` / `lib` / `lib64`）へ自動統合・パッチ当てを行える Python GUI ツールです (`customtkinter` 使用)。

## 主な機能
- **GApps ZIPの自動解析:** ZIPファイル内の `Core` または `GApps` フォルダから `.tar.lz` ファイルを自動検出・展開
- **lzip依存関係の自動チェック:** 展開に必要な `lzip` コマンドの有無を確認し、不足している場合は自動でインストールを試行
- **システムイメージの安全なマウント・統合:** `system.img` をループデバイスとして読み書き可能（`rw`）でマウントし、ファイルを再帰的に統合
- **権限・SELinuxコンテキストの自動修復:** 統合したファイル群に対して適切なパーミッション（`755` / `644`、オーナー `0:0`）および SELinux コンテキスト（`u:object_r:system_file:s0`）を自動設定
- **安全なディスク同期:** 処理完了後の `sync` 実行と確実なアンマウント処理

## 動作環境・必要要件
- **OS:** Zorin OS 18.1 推奨（Ubuntuベース。Linux Mint等ではマウントが読み込み専用になる不具合が確認されているためZorin OSを強く推奨します）
- **Python:** Python 3.12 推奨
- **Python ライブラリ:** `customtkinter` `tkinter`
- **システムコマンド:** `lzip`, `tar`, `mount`, `umount`, `findmnt`, `sudo`
- **GApps** `https://opengapps.org/ `こちらのサイトからPlatformは `ARM64` Androidは `7.0` Variantは `pico` を選択して赤い丸ボタンを押すとダウンロード先に進みます。そして数秒後にGAppsのzipファイルのダウンロードが開始されます。 

## インストール手順

端末（ターミナル）を開き、必要なパッケージをインストールしてください：

```bash
# tkinterのインストール（未導入の場合）
sudo apt install python3-tk
```

## 仮想環境について（推奨）
最近のLinuxディストリビューションでは、システム全体の Python 環境への直接 `pip install` が制限されている場合があります（externally-managed-environment エラー）。
そのため、`venv` を使用して仮想環境を構築して実行することを強くおすすめします。

```bash
# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate

# 必要なライブラリのインストール
pip install customtkinter
```

どうしてもシステム全体にインストールしたい場合は `--break-system-packages` オプションを使用することもできますが、非推奨です。

```bash
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    ...
```

### 使い方
- 端末からスクリプトを実行します（ループマウントやパッケージのインストールを行うため、内部で `sudo` 権限を使用します）。
- GUIを開いて操作をしているときに `sudo` を使用するためパスワードを求められることがあります。そのため端末をとPythonコードのより出力されるGUIの両方を見ることを推奨します。
- 画面上の 「参照...」 ボタンから、対象の `system.img` を選択します。
- 同様に、適用したい GAppsのZIPファイル を選択します。展開したファイルではなくてダウンロードしたzipそのままです。
- 「GAppsを自動展開して適用する」 ボタンをクリックすると、自動で依存関係チェック、展開、マウント、ファイル統合、権限・SELinux設定、アンマウントが行われます。
