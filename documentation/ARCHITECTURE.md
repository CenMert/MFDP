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

Uygulamanın kalbi core/timer.py içindeki PmdrCountdownTimer (Pomodoro) ve CountUpTimer (Free Timer) sınıflarıdır; FocusSession dataclass'ı oturumun çalışma zamanı verisini tutar. (Eski PomodoroTimer sınıfı yalnızca geriye uyumluluk için duruyor.) Pomodoro timer bir State Machine (Durum Makinesi) gibi davranır.

    States: Focus, Short Break, Long Break, Idle.

    Observer Pattern: Qt'nin Signal ve Slot yapısı kullanılarak, zamanlayıcıdaki her değişiklik (saniye azalması, mod değişimi, bitiş) asenkron olarak arayüze (UI) bildirilir. Bu sayede donma (freezing) yaşanmaz.

B. Data Layer (Model)

Veritabanı işlemleri mfdp_app/db/ altındaki repository sınıflarında izole edilmiştir (SessionRepository, AtomicEventRepository, TaskRepository, TagRepository, SettingsRepository, CalendarRepository). db_manager.py yalnızca geriye uyumluluk facade'ı olarak duruyor; uygulama kodu artık doğrudan repository'leri çağırıyor.

    Abstraction: UI katmanı asla SQL sorgusu bilmez. Sadece SessionRepository.log_session() veya get_daily_trend() gibi metotları çağırır.

    Connection Management: BaseRepository içindeki thread-safe ConnectionPool (5 bağlantı) bağlantıları yeniden kullanır; her işlem sonunda bağlantı havuza iade edilir.

    Tüm tabloların, kolonların, formatların ve kimin hangi veriyi okuyup yazdığının güncel listesi: documentation/VERI_HARITASI.md

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
start_time	TEXT	Oturumun başlama anı, yerel saat, 'YYYY-MM-DD HH:MM:SS'.
end_time	TEXT	Oturumun bitiş anı (aynı format).
duration_seconds	INTEGER	Gerçekleşen net süre (duraklatmalar hariç).
planned_duration_minutes	INTEGER	Kullanıcının hedeflediği süre (Free Timer / manuel girişte NULL).
mode	TEXT	Focus, Short Break, Long Break veya Free Timer.
task_name	TEXT	Görev bağlamı (görevin adı).
category	TEXT	Görevin etiketi (tag).
interruption_count	INTEGER	Oturum sırasında kaç kez duraklatıldığı (+ reset / mod değişimi / kapanış).
completed	BOOLEAN	Başarıyla bitti mi, yarıda mı kesildi?

V2 ile birlikte oturum içi ayrıntılar ayrıca atomic_events tablosunda ham olay akışı olarak tutulur (oturum başlangıcı, duraklama/devam, %25-50-75 milestone, tamamlanma/terk, DND). Ayrıca tasks, tags, settings, calendar_events ve calendar_ranges tabloları vardır.

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

Gelecek Hedefleri (Roadmap) — durum 2026-10-16:

    Görev (Task) bazlı detaylı raporlama. → Kısmen var: "Gün" paneli ve blok raporu (core/daily_report.py) tag + görev bazında blokları gösteriyor.

    CSV/JSON formatında veri dışa aktarma (Data Export). → Yalnızca takvim için JSON dışa/içe aktarma var; oturum/olay verisi için henüz yok.

    Pomodoro tekniğine ek olarak Flowtime tekniğinin eklenmesi. → Free Timer (CountUpTimer) modu eklendi.

    Hedef (Goal) sistemi. → Tasarlandı (documentation/HedefSistemi.md), henüz uygulanmadı.

    Aktif pencere takibi (focus shift). → AtomicAnalyzer API'si ve SystemMonitor var, ancak birbirine bağlı değil; veri toplanmıyor.
