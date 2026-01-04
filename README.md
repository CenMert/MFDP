# MFDP (Multi-Functional Distraction Preventer)
Projenin amacı genel olarak local-first, veri-analizi ve dikkat dağınıklığını önleyen bir sistem tasarlamak. Proje genel olarak bir sistem tasarımı yönünde gelişmemi sağlamak için seçildi. Aldığım kararların doğruluğunu ve mantığını test ettiğim bir proje olarak devam ediyor.

Henzü bitmiş değildir. Halen daha geliştirme ve genel olarak değişme aşamasındadır.

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
