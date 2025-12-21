import subprocess
import shutil

class DNDManager:
    def __init__(self):
        self.cookie = None # Sistemden alacağımız 'Sessizlik Bileti'
        self.is_active = False
        
        # 'busctl' komutu sistemde var mı kontrol et (Arch'ta kesin vardır)
        self.has_busctl = shutil.which("busctl") is not None

    def enable_dnd(self):
        """Bildirimleri sustur (KDE/Gnome uyumlu)."""
        if not self.has_busctl or self.is_active:
            return

        try:
            # Sistemden "Inhibit" (Baskılama) talep ediyoruz.
            # Parametreler: AppName="MFDP", Reason="Focus", Hints={} (Boş)
            # ssa{sv} -> String, String, Array of Dict (DBus imzası)
            cmd = [
                "busctl", "--user", "call",
                "org.freedesktop.Notifications",
                "/org/freedesktop/Notifications",
                "org.freedesktop.Notifications",
                "Inhibit",
                "ssa{sv}",
                "MFDP", "Focus Mode", "0" # 0 = Boş dictionary
            ]
            
            # Komutu çalıştır ve çıktıyı al (Örn: "u 15")
            output = subprocess.check_output(cmd).decode("utf-8").strip()
            
            # Çıktıdan cookie ID'sini ayıkla ("u 15" -> 15)
            if output.startswith("u "):
                self.cookie = output.split(" ")[1]
                self.is_active = True
                print(f"DND Aktif. (Token: {self.cookie})")
            else:
                print(f"DND Token alınamadı. Çıktı: {output}")

        except Exception as e:
            print(f"DND Açma Hatası: {e}")

    def disable_dnd(self):
        """Bildirimleri serbest bırak."""
        if not self.has_busctl or not self.is_active or not self.cookie:
            return

        try:
            # Aldığımız bileti (cookie) geri veriyoruz
            cmd = [
                "busctl", "--user", "call",
                "org.freedesktop.Notifications",
                "/org/freedesktop/Notifications",
                "org.freedesktop.Notifications",
                "UnInhibit",
                "u", # uint32 tipinde
                str(self.cookie)
            ]
            
            subprocess.run(cmd, check=True)
            self.is_active = False
            self.cookie = None
            print("DND Pasif. Bildirimler açık.")

        except Exception as e:
            print(f"DND Kapatma Hatası: {e}")