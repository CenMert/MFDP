MFDP - Yazılım Mimari ve Mühendislik Raporu
1. Proje Özeti ve Felsefesi

MFDP, Linux masaüstü ortamları için geliştirilmiş, yerel öncelikli (local-first) ve gizlilik odaklı bir üretkenlik asistanıdır.

Bu projenin temel mühendislik hedefi; kullanıcı verilerini buluta göndermeden, ham (raw) veri saklama prensibiyle çalışarak, gelecekte farklı analiz yöntemlerine imkan tanıyan, sürdürülebilir ve genişletilebilir bir mimari kurmaktır.

Temel Prensipler:

    Local-First: Tüm veriler kullanıcının cihazında SQLite içinde saklanır.

    Event-Sourcing Yaklaşımı: Skor veya puan yerine, her oturum atomik bir "olay" (event) olarak kaydedilir.

    Loose Coupling (Gevşek Bağlılık): Arayüz (UI), İş Mantığı (Core) ve Veri Katmanı (DB) birbirinden ayrılmıştır.

2. Teknik Yığın (Tech Stack)

    Programlama Dili: Python 3.10+

    GUI Framework: PySide6 (Qt for Python) - Neden?: Native performans, güçlü sinyal-slot mekanizması ve modern stil (QSS) desteği için.

    Veritabanı: SQLite3 - Neden?: Sunucusuz, dosya tabanlı, taşınabilir ve SQL gücüyle karmaşık analitik sorgulara uygun olduğu için.

    Veri Görselleştirme: Matplotlib - Neden?: Bilimsel düzeyde grafik çizim yeteneği ve Qt arayüzüne (FigureCanvas) gömülebilmesi.

3. Sistem Mimarisi

Uygulama, Modüler Monolitik bir yapıda tasarlanmış olup, MVC (Model-View-Controller) desenine benzer bir ayrım kullanır.
A. Core Layer (Controller/Logic)

Uygulamanın kalbi PomodoroTimer sınıfıdır. Bu sınıf bir State Machine (Durum Makinesi) gibi davranır.

    States: Focus, Short Break, Long Break, Idle.

    Observer Pattern: Qt'nin Signal ve Slot yapısı kullanılarak, zamanlayıcıdaki her değişiklik (saniye azalması, mod değişimi, bitiş) asenkron olarak arayüze (UI) bildirilir. Bu sayede donma (freezing) yaşanmaz.

B. Data Layer (Model)

Veritabanı işlemleri db_manager.py modülünde izole edilmiştir.

    Abstraction: UI katmanı asla SQL sorgusu bilmez. Sadece log_session() veya get_daily_trend() gibi fonksiyonları çağırır.

    Connection Management: Her işlem için güvenli bağlantı açılıp kapatılır (Context management), böylece "Database Locked" hataları önlenir.

C. UI Layer (View)

    Modern Styling: Arayüz, CSS benzeri QSS dosyalarıyla özelleştirilmiştir. Kod içine gömülü stiller yerine merkezi bir stil dosyası kullanılarak bakım kolaylığı sağlanmıştır.

    Component Based: İstatistik ekranı (StatsWindow), ayarlar (SettingsDialog) gibi parçalar modüler tasarlanmıştır.

4. Veritabanı Mühendisliği: V2 Mimarisi

Projenin en kritik mühendislik kararı, veritabanı şemasının V2 sürümüne geçirilmesidir.
Sorun (V1 Yaklaşımı):

İlk tasarımda sadece "X dakika çalışıldı" bilgisi tutuluyordu. Bu, "Verimlilik analizi" ve "Kesinti takibi" için yetersizdi.
Çözüm (V2 - Event-Based Schema):

Veriler "özet" olarak değil, "gerçekleşen olay" olarak saklanmaya başlandı. sessions_v2 tablosu şu yapıda tasarlandı:
Alan Adı	Tip	Açıklama
start_time	TIMESTAMP	Oturumun tam başlama anı (ISO8601).
duration_seconds	INTEGER	Gerçekleşen süre.
planned_duration	INTEGER	Kullanıcının hedeflediği süre.
task_name	TEXT	Görev bağlamı (Context).
interruption_count	INTEGER	Oturum sırasında kaç kez duraklatıldığı.
completed	BOOLEAN	Başarıyla bitti mi, yarıda mı kesildi?

Kazanım: Bu ham veri yapısı sayesinde, veritabanını değiştirmeden geriye dönük olarak "Hangi saatte verimliyim?", "Hangi görevde çok bölünüyorum?" gibi sorulara SQL sorgularıyla cevap verilebilir hale gelindi.
5. İstatistik ve Veri Analitiği Motoru

Uygulama, toplanan ham verileri işleyerek kullanıcıya içgörü (insight) sunar.
A. Veri İşleme Hattı (Pipeline)

    Extract (Çıkar): SQL ile ham veriler filtrelenir (Örn: WHERE start_time >= date('now', '-7 days')).

    Aggregate (Topla): SQL GROUP BY kullanılarak saatlik veya günlük toplamlar hesaplanır.

    Visualize (Görselleştir): Matplotlib kullanılarak veriler grafiklere dökülür.

B. Grafik Türleri ve Algoritmalar

    Günlük Trend (Bar Chart): Son 7 günün performansını gösterir. Eksik günler (veri olmayan günler) algoritma tarafından "0" değeriyle doldurularak zaman ekseninin bozulması engellenir.

    Saatlik Verimlilik (Area Chart): strftime('%H', start_time) fonksiyonu ile günün 24 saati dilimlenir ve kullanıcının sirkadiyen ritmi (biyolojik saati) görselleştirilir.

    Odak Kalitesi (Pie Chart): Oturumlar interruption_count değerine göre kümelenir (Cluster):

        Deep Work: 0 kesinti.

        Moderate: 1-2 kesinti.

        Distracted: 3+ kesinti.

6. Sonuç ve Gelecek Planları

Bu proje ile, basit bir sayaç uygulamasının ötesine geçilerek, veri odaklı bir kişisel asistan mimarisi kurulmuştur.

Mühendislik Kazanımları:

    Genişletilebilir veri şeması.

    Event-driven (olay güdümlü) UI yönetimi.

    Platform bağımsız (Linux/Windows/Mac uyumlu) çekirdek yapı.

Gelecek Hedefleri (Roadmap):

    Görev (Task) bazlı detaylı raporlama.

    CSV/JSON formatında veri dışa aktarma (Data Export).

    Pomodoro tekniğine ek olarak Flowtime tekniğinin eklenmesi.
