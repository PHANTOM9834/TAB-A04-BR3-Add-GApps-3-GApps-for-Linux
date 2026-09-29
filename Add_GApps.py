import os
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import customtkinter as ctk
import tempfile

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class GAppsPatcherApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("Android GApps Patcher")
    self.geometry("620x560")

    # --- 1. system.img 選択部分 ---
    self.label_img = ctk.CTkLabel(self, text="system.imgのパス:")
    self.label_img.pack(pady=(20, 5), padx=30)

    self.frame_img = ctk.CTkFrame(self, fg_color="transparent")
    self.frame_img.pack(padx=30)

    self.entry_img = ctk.CTkEntry(self.frame_img, width=420)
    self.entry_img.pack(side="left", padx=(0, 10))

    self.btn_browse_img = ctk.CTkButton(
        self.frame_img, text="参照...", width=70, command=self.select_img
    )
    self.btn_browse_img.pack(side="left")

    # --- 2. GApps ZIP 選択部分 ---
    self.label_gapps = ctk.CTkLabel(self, text="GAppsのZIPファイルパス:")
    self.label_gapps.pack(pady=(15, 5), padx=30)

    self.frame_gapps = ctk.CTkFrame(self, fg_color="transparent")
    self.frame_gapps.pack(padx=30)

    self.entry_gapps = ctk.CTkEntry(self.frame_gapps, width=420)
    self.entry_gapps.pack(side="left", padx=(0, 10))

    self.btn_browse_gapps = ctk.CTkButton(
        self.frame_gapps, text="参照...", width=70, command=self.select_gapps_zip
    )
    self.btn_browse_gapps.pack(side="left")

    # --- 3. 実行ボタン ---
    self.btn_run = ctk.CTkButton(
        self,
        text="GAppsを自動展開して適用する",
        fg_color="green",
        hover_color="darkgreen",
        command=self.run_gapps_patch,
        height=40,
    )
    self.btn_run.pack(pady=25)

    # --- 4. ログ表示部分 ---
    self.text_log = ctk.CTkTextbox(self, width=560, height=150)
    self.text_log.pack(padx=30, pady=(0, 20))

    # --- 警告・免責事項のスペース ---
    warning_text = (
        "【重要なお知らせと免責事項 このツールを使用した場合下記に同意したことになります。】\n"
        "1. 本ツールはAndroidシステムのパーティション書き換えを行う高度なツールです。\n"
        "2. 誤った操作や不具合により、デバイスが起動しなくなる等のリスクがあります。\n"
        "3. 本ツールの使用によるいかなるデータの損失、機器の破損についても、\n"
        "   作者は一切の責任を負いません。自己責任でご利用ください。 \n"
        "4.本ツールを使用するにあたって絶対に以下のことは守ってください。 \n" \
        "   adb fastboot MTKClientのすべてのツールが必ず使用できること。 \n"
        "   特にMTKClientの場合依存関係が複雑かつAndroidの深い場所を扱うためfastbootが失敗したときに使えないと文鎮化します。 \n" 
        "   重要なパーティション、できればすべてのパーティションのバックアップをとっておくこと。 \n"
        "   パソコンとAndroidについてある程度の知識があること。"
        "5.今回作者が使用した環境はPython 3.12 ZorinOS18.1です。 \n"
        "   これはUbuntuベース向けに作られておりLinux系でも動作しないOSも存在しています。 \n"
        "   LinuxMintではsudoを使用してもマウントが読み込み専用であったためZorinOSであることを強く推奨します。"
    )

    self.text_warning = ctk.CTkTextbox(
        self, width=560, height=110, text_color="red"
    )
    self.text_warning.pack(padx=30, pady=(0, 15))

    self.text_warning.insert("0.0", warning_text)
    self.text_warning.configure(state="disabled")

  def select_img(self):
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.img"), ("All Files", "*.*")]
    )
    if file_path:
      self.entry_img.delete(0, tk.END)
      self.entry_img.insert(0, file_path)

  def select_gapps_zip(self):
    file_path = filedialog.askopenfilename(
        filetypes=[("ZIP Files", "*.zip"), ("All Files", "*.*")]
    )
    if file_path:
      self.entry_gapps.delete(0, tk.END)
      self.entry_gapps.insert(0, file_path)

  def log(self, message):
    self.text_log.insert(tk.END, message + "\n")
    self.text_log.see(tk.END)

  def check_and_install_dependencies(self):
    """必要なシステムコマンド（lzip）の有無をチェックし、なければ自動インストールを試みる"""
    self.log("システム依存ツール（lzip）の有無を確認中...")
    check = subprocess.run(["which", "lzip"], capture_output=True, text=True)

    if check.returncode != 0:
      self.log(
          "警告: 'lzip' が見つかりません。自動インストールを試みます..."
      )
      messagebox.showinfo(
          "依存ツールのインストール",
          "OpenGAppsの展開に必要な 'lzip' が見つかりません。\n"
          "「OK」を押すと、自動的に管理者権限でインストールを実行します。",
      )
      try:
        install_res = subprocess.run(
            ["sudo", "apt", "update"], capture_output=True, text=True
        )
        install_res = subprocess.run(
            ["sudo", "apt", "install", "-y", "lzip"],
            capture_output=True,
            text=True,
        )

        if install_res.returncode == 0:
          self.log("'lzip' のインストールに成功しました！")
        else:
          raise Exception(f"インストール失敗: {install_res.stderr}")
      except Exception as e:
        raise Exception(
            f"依存ツールの自動インストールに失敗しました:\n{e}\n\n"
            "手動で 'sudo apt install lzip' を実行してください。"
        )
    else:
      self.log("依存ツール（lzip）は正常に導入されています。")

  def mount_image(self, img_path, mount_point):
    """共通のマウント処理"""
    self.log(f"マウント先を作成中: {mount_point}")
    subprocess.run(["sudo", "mkdir", "-p", mount_point], check=True)

    self.log("system.imgをマウント中...")
    subprocess.run(
        ["sudo", "mount", "-o", "loop,rw", img_path, mount_point], check=True
    )

    mount_check = subprocess.run(
        ["findmnt", "-n", "-o", "OPTIONS", mount_point],
        capture_output=True,
        text=True,
    )
    if "ro" in mount_check.stdout:
      raise Exception("エラー: system.imgが読み込み専用 (ro) でマウントされました！")

  def run_gapps_patch(self):
    img_path = self.entry_img.get()
    gapps_zip = self.entry_gapps.get()

    if not img_path:
      messagebox.showerror("エラー", "system.imgを選択してください。")
      return
    if not gapps_zip:
      messagebox.showerror("エラー", "GAppsのZIPファイルを選択してください。")
      return

    mount_point = tempfile.mkdtemp(prefix="android_sys_")
    self.log("=== [GApps自動適用] 処理を開始します ===")

    try:
      # 0. 依存ツールの自動チェック＆インストール
      self.check_and_install_dependencies()

      # 1. system.imgのマウント
      self.mount_image(img_path, mount_point)

      # 2. 一時ディレクトリにZIPを展開
      self.log("GAppsのZIPファイルを一時解凍中...")
      with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(gapps_zip, "r") as zf:
          zf.extractall(temp_dir)

        target_dirs = ["Core", "GApps"]
        found_folders = []
        for root, dirs, files in os.walk(temp_dir):
          for d in dirs:
            if d in target_dirs:
              found_folders.append(os.path.join(root, d))

        if not found_folders:
          raise Exception(
              "エラー: ZIP内に 'Core' または 'GApps' フォルダが見つかりませんでした。"
          )

        extracted_count = 0
        for sub_path in found_folders:
          for file_name in os.listdir(sub_path):
            if file_name.endswith(".tar.lz"):
              tarlz_path = os.path.join(sub_path, file_name)
              extract_sub = os.path.join(temp_dir, "extracted_" + file_name)
              os.makedirs(extract_sub, exist_ok=True)

              cmd = f"lzip -d -c '{tarlz_path}' | tar -xf - -C '{extract_sub}'"
              res = subprocess.run(
                  cmd, shell=True, capture_output=True, text=True
              )
              if res.returncode != 0:
                continue

              # 中間フォルダの中も含めて system や app を再帰的に探す
              merged_any = False
              for root_ex, dirs_ex, files_ex in os.walk(extract_sub):
                if os.path.basename(root_ex) == "system":
                  cp_res = subprocess.run(
                      ["sudo", "cp", "-r", f"{root_ex}/.", mount_point],
                      capture_output=True,
                      text=True,
                  )
                  if cp_res.returncode == 0:
                    merged_any = True
                elif os.path.basename(root_ex) in [
                    "app",
                    "priv-app",
                    "etc",
                    "framework",
                    "lib",
                    "lib64",
                ]:
                  dest_sub_path = os.path.join(
                      mount_point, os.path.basename(root_ex)
                  )
                  os.makedirs(dest_sub_path, exist_ok=True)
                  cp_res = subprocess.run(
                      ["sudo", "cp", "-r", f"{root_ex}/.", dest_sub_path],
                      capture_output=True,
                      text=True,
                  )
                  if cp_res.returncode == 0:
                    merged_any = True

              if merged_any:
                extracted_count += 1
                self.log(f"  -> 統合成功: {file_name}")

        self.log(
            f"合計 {extracted_count} 個のパッケージを展開・統合しました。"
        )

      # 3. 権限とSELinux、同期処理
      self.log("システム領域全体の権限とSELinuxコンテキストを再設定中...")
      for folder in ["app", "priv-app", "etc", "framework", "lib", "lib64"]:
        target_f = os.path.join(mount_point, folder)
        if os.path.exists(target_f):
          subprocess.run(["sudo", "chown", "-R", "0:0", target_f], check=False)
          subprocess.run(
              [
                  "sudo",
                  "find",
                  target_f,
                  "-type",
                  "d",
                  "-exec",
                  "chmod",
                  "755",
                  "{}",
                  "+",
              ],
              check=False,
          )
          subprocess.run(
              [
                  "sudo",
                  "find",
                  target_f,
                  "-type",
                  "f",
                  "-exec",
                  "chmod",
                  "644",
                  "{}",
                  "+",
              ],
              check=False,
          )
          subprocess.run(
              [
                  "sudo",
                  "chcon",
                  "-R",
                  "u:object_r:system_file:s0",
                  target_f,
              ],
              check=False,
          )

      self.log("変更をディスクに同期中 (sync)...")
      subprocess.run(["sudo", "sync"], check=True)

      self.log("GAppsの自動適用が完了しました！")
      messagebox.showinfo(
          "成功", "GAppsの自動展開と適用が正常に完了しました。"
      )

    except Exception as e:
      self.log(f"[エラー発生]: {e}")
      messagebox.showerror("エラー", f"処理に失敗しました:\n{e}")

    finally:
      self.log("アンマウント処理を実行中...")
      try:
        subprocess.run(["sudo", "umount", mount_point], check=True)
        self.log("アンマウント完了。")
      except Exception as ex:
        self.log(f"アンマウント時のエラー: {ex}")

if __name__ == "__main__":
  app = GAppsPatcherApp()
  app.mainloop()