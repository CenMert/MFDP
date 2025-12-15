import subprocess
import time

class SystemMonitor:
    """
    Linux (KDE/Wayland öncelikli) üzerinde aktif pencere takibini yönetir.
    D-Bus (KDE) ve yedek olarak geleneksel X11 araçlarını (xdotool/wmctrl) kullanır.
    """
    
    def __init__(self):
        self.wmctrl_available = self._check_command_available('wmctrl')
        self.xdotool_available = self._check_command_available('xdotool')
        self.qdbus_available = self._check_command_available('qdbus')

        if not self.qdbus_available and not (self.wmctrl_available or self.xdotool_available):
            print("HATA: Aktif pencere takibi için 'qdbus', 'wmctrl' veya 'xdotool' komutlarından hiçbiri yüklü değil. Lütfen kurun.")

    def _check_command_available(self, command):
        """Verilen komutun PATH'de bulunup bulunmadığını kontrol eder."""
        try:
            subprocess.run([command, '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_info_via_dbus_kde(self):
        """
        KDE KWin D-Bus arayüzünü kullanarak aktif pencere bilgisini alır.
        Bu, Wayland oturumlarında en güvenilir yöntemdir.
        """
        if not self.qdbus_available:
            return None, None
            
        try:
            # KWin'den aktif pencerenin ID'sini (obje yolu) al
            cmd_id = ['qdbus', 'org.kde.KWin', '/KWin/ActiveWindow', 'activeWindow']
            window_id_hex = subprocess.run(cmd_id, capture_output=True, text=True, check=True).stdout.strip()

            if not window_id_hex or window_id_hex == '0':
                return "KWIN_ID_YOK", "Masaüstü/Panel"

            # Pencerenin objesi üzerinden başlığını al
            # qdbus org.kde.KWin /Windows/<window_id> windowTitle
            cmd_title = ['qdbus', 'org.kde.KWin', window_id_hex, 'caption']
            window_title = subprocess.run(cmd_title, capture_output=True, text=True, check=True).stdout.strip()
            
            # Pencerenin objesi üzerinden process adını/sınıfını (Class) al
            # QDBus'ta doğrudan PID almak zor olabilir, bunun yerine 'resourceClass' veya 'pid' arayüzlerini kullanalım.
            # KDE uygulamaları genellikle 'resourceClass'ı kullanır.
            try:
                # resourceClass: Uygulamanın genel sınıfı (ör: Firefox, code)
                cmd_class = ['qdbus', 'org.kde.KWin', window_id_hex, 'resourceClass']
                process_name = subprocess.run(cmd_class, capture_output=True, text=True, check=True).stdout.strip()
            except:
                process_name = "KWIN_SINIF_YOK"

            # D-Bus'tan gelen başlık genellikle tırnak işaretleriyle gelir, temizleyelim.
            if window_title.startswith('"') and window_title.endswith('"'):
                window_title = window_title[1:-1]
            
            # Process adı boşsa, başlık kelimelerini kullanabiliriz (yedek)
            if not process_name or process_name == "KWIN_SINIF_YOK":
                 # Process adını pencere başlığından tahmin et
                process_name = window_title.split()[-1].replace('-', '').lower()
                
            return process_name, window_title
        
        except Exception as e:
            # print(f"D-Bus/KDE KWin hatası: {e}") # Debug amaçlı
            return None, None # X11 yedeğine geç

    def get_active_window_info(self):
        """Aktif pencereyi bulmak için öncelikli olarak D-Bus'ı, sonra X11 araçlarını kullanır."""
        
        # 1. KDE D-Bus denemesi (Wayland uyumlu)
        process_name, window_title = self._get_info_via_dbus_kde()
        
        if process_name is not None and process_name != "KWIN_ID_YOK":
            return process_name, window_title

        # 2. Geleneksel X11 araçları (Firefox, Cursor gibi XWayland uygulamaları için yedek)
        # Önceki kodumuzun wmctrl/xdotool mantığını buraya taşıyalım.
        # Bu kısım, KDE Wayland'da XWayland uygulamaları için yine de çalışabilir.
        
        # Eğer D-Bus başarısız olduysa veya bir XWayland uygulaması ise, önceki X11 mantığını kullan:
        
        # [ÖNCEKİ X11 MANTIĞI BURAYA GELİR, YUKARIDAKİ SystemMonitor KODUNUN wmctrl/xdotool KISMINI BURAYA AKTARABİLİRİZ]
        # Basitçe, eğer process_name hala None ise:
        
        if process_name is None and (self.wmctrl_available or self.xdotool_available):
            # ... eski kodun wmctrl/xdotool bloğunu buraya ekleyebiliriz ...
            return "X11_YEDEK", "Yedek Kodu Kullan" # Şimdilik sadece işaretleyelim

        return process_name or "BILINMIYOR", window_title or "BILINMIYOR"

# --- Test Kodları ---
if __name__ == '__main__':
    monitor = SystemMonitor()
    print("Aktif pencere takibi başlatıldı (5 saniyede bir kontrol ediliyor). Çıkmak için Ctrl+C.")
    
    for i in range(10):
        app, title = monitor.get_active_window_info()
        print(f"[{time.strftime('%H:%M:%S')} - Deneme {i+1}] Uygulama: {app:<20} | Başlık: {title}")
        time.sleep(5)