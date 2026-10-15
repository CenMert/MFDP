"""DND denemesi için test bildirimi gönderir.

Kullanım: python notif_test.py [mesaj] [--delay SANİYE]
DND açıkken bildirim ekranda görünmemeli (KDE geçmişine düşer).
"""
import argparse
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument("message", nargs="?", default="DND testi: bu bildirimi görüyorsan DND kapalı.")
parser.add_argument("--delay", type=int, default=0, help="göndermeden önce bekle (sn)")
args = parser.parse_args()

if args.delay:
    print(f"{args.delay} sn sonra gönderiliyor...")
    time.sleep(args.delay)

subprocess.run(["notify-send", "--app-name=MFDP Test", "MFDP Test", args.message], check=True)
print("Bildirim gönderildi.")
