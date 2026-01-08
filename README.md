# MFDP (Multi-Functional Distraction Preventer)

**MFDP**, Linux ortamı için geliştirilmiş, yerel (local-first) çalışan, veri odaklı ve modern bir Pomodoro odaklanma asistanıdır.

Sadece bir zamanlayıcı değil; çalışma alışkanlıklarınızı analiz eden, sizi "ayık" tutan ve verilerinizi gizlilik içinde yerel olarak saklayan kişisel bir üretkenlik aracıdır.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active_Development-orange)

## ✨ Özellikler

* **Akıllı Zamanlayıcı:** Focus, Kısa Mola ve Uzun Mola modları. Özelleştirilebilir süreler. FreeTimer da eklendi.
* **💾 Local-First Veritabanı:** Tüm oturum verileri SQLite üzerinde, atomik ve ham (raw) formatta saklanır. Bulut yok, veri kaybı yok.
* **📊 Detaylı İstatistikler:**
    * **Günlük Trend:** Son 7 günlük performans grafiği.
    * **Saatlik Isı Haritası:** Günün hangi saatlerinde daha verimlisiniz?
    * **Kalite Analizi:** Kesintisiz (Deep Work) ve bölünmüş oturumların pasta grafiği ve yapay zeka benzeri sözel özetler.
* **🔔 Farkındalık (Gong) Modu:** Opsiyonel "Ayaklı Saat" özelliği ile her saatin başında ve buçuğunda (XX:00, XX:30) ince bir ses çalarak zaman algınızı korur.
* **🎨 Modern Dark UI:** Göz yormayan, "Süper Sade" tasarım felsefesiyle hazırlanmış PySide6 arayüzü.

## 🛠️ Teknolojiler

* **Dil:** Python 3
* **GUI:** PySide6 (Qt for Python)
* **Veri Görselleştirme:** Matplotlib
* **Veritabanı:** SQLite3
* **Stil:** QSS (Qt Style Sheets)

## 🚀 Kurulum

Projeyi yerel makinenize klonlayın ve gerekli bağımlılıkları kurun.

### Gereksinimler
* Python 3.x
* Linux (Arch, Ubuntu, Fedora vb.) - *Özellikle KDE/GNOME ortamlarında test edilmiştir.*

### Adım Adım

1.  **Repoyu klonlayın:**
    ```bash
    git clone [https://github.com/kullaniciadi/MFDP.git](https://github.com/kullaniciadi/MFDP.git)
    cd MFDP
    ```

2.  **Sanal Ortam Oluşturun (Önerilen):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    ```

3.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Not: Arch Linux kullanıcıları `qt6-tools` gibi sistem paketlerine ihtiyaç duyabilir, ancak pip kurulumu genellikle yeterlidir.)*

## ▶️ Kullanım

Uygulamayı proje kök dizininden modül olarak başlatın:

```bash
python3 -m mfdp_app.main