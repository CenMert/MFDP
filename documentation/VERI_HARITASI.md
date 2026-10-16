# MFDP — Veri Haritası

*Son güncelleme: 2026-10-16 (`calendar` branch'i, commit 59621c1 üzerinden koddan doğrulandı)*

Bu doküman MFDP'nin **hangi veriyi, nerede, hangi formatta, ne amaçla** tuttuğunu ve
o verinin **kim tarafından yazılıp kim tarafından okunduğunu** özetler. Kod değiştikçe
güncel tutulmalıdır; çelişki olursa kaynak koddur.

---

## 1. Genel Bakış

| Depo | Konum | Format | Ömür | Amaç |
|------|-------|--------|------|------|
| SQLite veritabanı | `focus_tracker.db` (**çalışma dizinine göre**, `run.sh` proje köküne `cd` eder) | SQLite 3, 7 tablo | Kalıcı | Tüm kullanıcı verisi |
| Panel durum dosyası | `$XDG_RUNTIME_DIR/mfdp/state.json` (yoksa `/tmp/mfdp-<uid>/`) | JSON, her saniye üzerine yazılır | Geçici; uygulama kapanınca silinir | KDE Plasma widget'ına canlı durum |
| Qt ayar dosyası | `~/.config/MFDP/MFDP.conf` (`QSettings("MFDP","MFDP")`) | INI | Kalıcı | Yalnızca mini pencerenin konumu |
| Takvim JSON dışa/içe aktarma | Kullanıcının seçtiği dosya (varsayılan `takvim.json`) | JSON (UTF-8, girintili) | Kullanıcıya ait | Yedekleme / AI ile takvim üretme |
| Test/seed veritabanları | `mfdp_app/MyDataBases/*.db` | SQLite | Geliştirme | Elle test, örnek veri |

Ağ: Uygulama kullanıcı verisini **hiçbir yere göndermez**. Tek dış istek
`core/updater.py`'nin GitHub Releases API'sine yaptığı sürüm kontrolüdür (yalnızca
okuma; veri yazmaz, yerelde bir şey saklamaz).

---

## 2. Veritabanı Erişim Katmanı

- **Bağlantı:** `db/base_repository.py` → `ConnectionPool` (5 bağlantı, `check_same_thread=False`,
  `row_factory = sqlite3.Row`). Havuz boşsa yeni bağlantı açılır.
- **Şema:** `db/database_initializer.py` → `setup_database()` her açılışta çalışır;
  `CREATE TABLE IF NOT EXISTS` + `tasks` için iki `ALTER TABLE` göçü (`parent_id`, `is_completed`).
  Ayrı bir şema sürüm numarası **yok**.
- **Repository'ler:** `SessionRepository`, `AtomicEventRepository`, `TaskRepository`,
  `TagRepository`, `SettingsRepository`, `CalendarRepository`.
- **`db_manager.py` (facade):** Geriye uyumluluk için duruyor ama uygulama kodunun hiçbir yeri
  artık onu import etmiyor; tüm `core/` ve `ui/` modülleri doğrudan repository'leri çağırıyor.
  `CalendarRepository` facade'da yer almıyor.

> ⚠️ **Foreign key'ler fiilen uygulanmıyor.** SQLite'ta FK kontrolü bağlantı başına
> `PRAGMA foreign_keys = ON` ile açılır; kodda bu PRAGMA hiç çağrılmıyor. Dolayısıyla şemadaki
> `ON DELETE CASCADE` (atomic_events → sessions_v2, tasks → tasks) **çalışmaz**.
> `SessionRepository.delete_session()` docstring'i "olaylar cascade silinir" dese de silinmez.
> (Şu an hiçbir UI oturum silmediği için pratikte sorun çıkmıyor.)

---

## 3. Tablolar

### 3.1 `sessions_v2` — Oturum özeti (her timer oturumu = 1 satır)

| Kolon | Tip | Format / Değerler | Not |
|-------|-----|-------------------|-----|
| `id` | INTEGER PK | otomatik | `atomic_events.session_id` bunu gösterir |
| `start_time` | TEXT | `YYYY-MM-DD HH:MM:SS`, **yerel saat** | İndeksli. Sıralama/aralık sorguları string karşılaştırması |
| `end_time` | TEXT | aynı | |
| `duration_seconds` | INTEGER | **net** süre (duraklatmalar hariç, `active_seconds`) | |
| `planned_duration_minutes` | INTEGER | Pomodoro/mola: ayardaki süre; Free Timer ve manuel giriş: `NULL` | |
| `mode` | TEXT | `Focus`, `Short Break`, `Long Break`, `Free Timer` | Molalar da kaydedilir |
| `completed` | BOOLEAN | Pomodoro: `1` = süre doldu; `0` = reset, mod değişimi, uygulama kapanışı. Count-up (`countup_v1`): `1` = Bitir, `0` = uygulama kapanışı | |
| `task_name` | TEXT | Görevin **adı** (id değil) | Görev yeniden adlandırılırsa eski oturumlarla bağ kopar |
| `category` | TEXT | Görevin **tag**'i | `tags.name` ile eşleşir ama FK değil |
| `focus_rating` | INTEGER | 1–5 öznel odak puanı ya da `NULL` (atlandı) | Bitir sonrası geri bildirim şeridi (`ui/feedback_strip.py`) |
| `session_kind` | TEXT | `okuma`, `soru`, `tekrar`, `uretim`, `diger` ya da `NULL` | Aynı şerit; SM-2/FSRS tekrar planlaması için temel |
| `interruption_count` | INTEGER | Pomodoro: duraklatma sayısı + kapanış nedenleri (reset/mod değişimi/app_exit). Count-up (`countup_v1`): **yalnızca işaretlenen iç/dış kesintiler** | Analizde `timer_model` ile ayırın |

**Yazanlar**
- `core/timer.py` → `PmdrCountdownTimer._save_current_session()` ve `CountUpTimer._save_current_session()`
  (oturum biterken, reset'te, mod değişiminde ve uygulama kapanırken `save_on_exit()`).
  Yalnızca `active_seconds > 0` ise yazılır.
- `ui/manual_session_dialog.py` → İstatistik penceresinden elle oturum ekleme. Her zaman
  `mode='Free Timer'` olarak yazılır (istatistik sorguları yalnızca Focus/Free Timer'ı saydığı için).
- `core/timer.py` → `PomodoroTimer` (eski sınıf, kullanılmıyor, geriye uyumluluk için duruyor).

**Okuyanlar**
- `ui/stats_window.py` (SessionRepository üzerinden): 7 günlük trend, saatlik verimlilik,
  tamamlanma oranı, odak kalitesi (0 / 1-2 / 3+ kesinti). Hepsi `mode IN ('Focus','Free Timer')`.
- `ui/stats_window.py` (TagRepository üzerinden): etiket bazlı toplam süre ve 7 günlük trend
  (`category` kolonuna göre).
- `core/daily_report.py` → `ui/day_panel.py` ve `ui/block_detail_dialog.py`: "Gün" paneli ve blok raporu.
- `core/task_manager.py` → görev bazlı toplam süre (`task_name` ile eşleşme).

### 3.2 `atomic_events` — Ham olay akışı (event sourcing)

| Kolon | Tip | Format | Not |
|-------|-----|--------|-----|
| `id` | INTEGER PK | | |
| `session_id` | INTEGER | `sessions_v2.id` | Olaylar önce bellekte birikir, oturum DB'ye yazılınca id geriye dönük atanır |
| `event_type` | TEXT | aşağıdaki tablo | İndeksli |
| `timestamp` | TEXT | ISO8601, **`T` ayraçlı + mikrosaniye**, yerel saat (`2026-10-11T22:16:48.493455`) | `sessions_v2` formatından farklı! |
| `elapsed_seconds` | INTEGER | Oturum başından beri geçen **duvar saati** süresi (duraklatmalar dahil) | Net süre gerekiyorsa metadata'daki `active_seconds` |
| `metadata` | TEXT | JSON nesnesi (`json.dumps`) ya da `NULL` | Okurken `json.loads` → dict |
| `created_at` | TEXT | SQLite `CURRENT_TIMESTAMP` → **UTC**, `YYYY-MM-DD HH:MM:SS` | Diğer zaman alanları yerel saattir |

**Count-up modeli (`countup_v1`, 2026-10-16'dan itibaren varsayılan mod):** duraklatma yok.
Başlat → (iç/dış kesinti işaretle) → Bitir. Devam etmek yeni bir oturumdur, dolayısıyla
**mola süresi = aynı gün ardışık iki oturum arasındaki boşluk** (`next.start_time − prev.end_time`) ve
odak süresinin seyri = oturum uzunluklarının zamana göre değişimi. 60 saniyenin altındaki oturumlar kaydedilmez.

**Akış:** `AtomicAnalyzer` olayları `event_buffer` listesinde tutar → timer oturumu kaydedince
`flush_events(session_id=...)` tek transaction'da `AtomicEventRepository.insert_events()` ile yazar.
Oturum DB'ye yazılmazsa (ör. 0 saniyelik oturum) buffer'daki olaylar atılır.

**Gerçekten üretilen olaylar**

| `event_type` | Kim tetikler | `metadata` alanları |
|--------------|-------------|---------------------|
| `session_started` | Timer, yeni oturum başlarken (Focus, molalar ve Free Timer dahil) | `planned_duration` (sn; Free Timer'da `0`), `session_type` (= mode), `app_before` (hep `null`); count-up'ta ayrıca `timer_model: "countup_v1"` |
| `interruption_detected` | Pomodoro: kullanıcı duraklatınca (`reason`=`user_pause`, `severity`=`low`). Count-up: İç kesinti / Dış kesinti butonu veya I / E tuşu, oturum **durmadan** (`reason`=`internal`/`external`, `severity`=`low`/`medium`) | `reason`, `severity`, `interruption_number`, `first_interruption_at`, `recovery_app` (`null`), `active_seconds` |
| `session_resumed` | Pomodoro timer, duraklatmadan devam edince (count-up'ta duraklatma yok) | `app_context` (`null`), `pause_seconds`, `active_seconds` |
| `milestone_reached` | Pomodoro timer, **yalnızca Focus**, net sürenin %25/50/75'i | `milestone_type` (`quarter`/`halfway`/`three_quarters`), `percentage` |
| `session_completed` | Süre doldu (`completed_by=timer`) / count-up'ta Bitir (`user`) | `actual_duration`, `planned_duration`, `completed_by`, `interruption_count`, `focus_completion_ratio`; count-up'ta ayrıca `end_reason: "finish"`, `timer_model` |
| `session_abandoned` | Reset, mod değişimi, uygulama kapanışı | `reason` (`reset`/`mode_change`/`app_exit`), `interruption_count`, `partial_completion`. Count-up'ta 60 sn altı Bitir (`too_short`) olayı DB'ye **yazılmaz**, oturum atılır |
| `dnd_toggled` | `MainWindow.on_dnd_changed` (🔕 butonu / Ctrl+D), yalnızca oturum aktifken | `dnd_enabled` |

**Tanımlı ama hiçbir yerden çağrılmayan olaylar** (API var, entegrasyon yok):
`focus_shift_detected` (`record_focus_shift` — `SystemMonitor` hiçbir yerde oluşturulmuyor),
`distraction_identified`, `environment_changed`, `break_started`, `break_ended`.
Canlı DB'de bu türlerden görünen kayıtlar `seeder.py` / `seed_atomic_events.py` ile eklenmiş örnek verilerdir.

**Okuyanlar**
- `ui/stats_window.py` → 14 günlük gün × saat ısı haritası (`get_heatmap`, olay türü filtresiyle).
- `core/daily_report.py` → oturum içi duraklamaları (interruption → resume çiftleri, `pause_seconds`,
  `active_seconds`) blok raporunda göstermek için (`get_events_for_sessions`).
- `check_atomic_events.py` → elle inceleme betiği.
- İleride: ML / davranış analizi (tasarım amacı ham veriyi kaybetmemek).

### 3.3 `tasks` — Görevler (düz + ağaç)

| Kolon | Tip | Format | Not |
|-------|-----|--------|-----|
| `id` | INTEGER PK | | |
| `name` | TEXT UNIQUE | | Oturumlara bu ad yazılır |
| `tag` | TEXT NOT NULL | etiket adı | Görev eklenirken `tags`'ta yoksa otomatik oluşturulur |
| `planned_duration_minutes` | INTEGER | dakika | Bilgi amaçlı |
| `created_at` | TEXT | `YYYY-MM-DD HH:MM:SS` yerel | |
| `is_active` | BOOLEAN | `0` = silinmiş (**soft delete**) | Satır fiziksel olarak silinmez |
| `color` | TEXT | `#rrggbb` | Etiket rengi değişince o etiketin tüm görevlerine yayılır |
| `parent_id` | INTEGER | üst görev id'si / `NULL` | Ağaç yapısı (`recursive_task_manager.py`) |
| `is_completed` | BOOLEAN | | Tüm çocuklar tamamlanınca üst otomatik tamamlanır |

**Yazanlar:** `core/task_manager.py`, `core/recursive_task_manager.py` (ui: `task_window.py`, `recursive_task_window.py`).
**Okuyanlar:** görev pencereleri, timer (aktif görevin adı + tag'i oturuma kopyalanır),
`manual_session_dialog.py`, mini pencere / panel (aktif görevin rengi).

### 3.4 `tags` — Etiketler / kategoriler

| Kolon | Tip | Format |
|-------|-----|--------|
| `name` | TEXT PK | |
| `color` | TEXT | `#rrggbb` |
| `created_at` | TEXT | `YYYY-MM-DD HH:MM:SS` yerel |

Kullanım: görev gruplama, istatistiklerde etiket bazlı grafikler, gün panelindeki blok renkleri.

### 3.5 `settings` — Anahtar/değer ayarları

Tüm değerler **TEXT** olarak saklanır (`str(value)`), okuyan taraf `int()` ile çevirir.

| Anahtar | Varsayılan | Birim | Yazan | Okuyan |
|---------|-----------|-------|-------|--------|
| `focus_duration` | 25 | dakika | `settings_dialog.py` | `timer.py` (`reload_settings`) |
| `short_break_duration` | 5 | dakika | `settings_dialog.py` | `timer.py` |
| `long_break_duration` | 15 | dakika | `settings_dialog.py` | `timer.py` |
| `sound_volume` | 100 | 0–100 | `settings_dialog.py` | `notifier.py` |

### 3.6 `calendar_events` — Tek günlük takvim kayıtları

| Kolon | Tip | Format |
|-------|-----|--------|
| `id` | INTEGER PK | |
| `title` | TEXT | |
| `date` | TEXT | `YYYY-MM-DD` (string sırası = tarih sırası) |
| `time` | TEXT | `HH:MM` (24 saat) ya da `NULL` |
| `kind` | TEXT | `sinav`, `odev`, `toplanti`, `diger` |
| `note` | TEXT | serbest / `NULL` |
| `task_id` | INTEGER | Yalnızca `kind='sinav'` için anlamlı: sınavın ait olduğu **ders** (`tasks.id`, ana görev) ya da `NULL`. Tekrar planı bu bağa göre çalışır |
| `created_at` | TEXT | `CURRENT_TIMESTAMP` (UTC) |

> Takvim JSON dışa/içe aktarma formatı `task_id`'yi **taşımaz**: içe aktarılan sınavlar derse bağlı gelmez, takvimde sınav satırından ders seçilmelidir.

### 3.7 `calendar_ranges` — Çok günlük dönemler

| Kolon | Tip | Format |
|-------|-----|--------|
| `id` | INTEGER PK | |
| `label` | TEXT | |
| `start_date`, `end_date` | TEXT | `YYYY-MM-DD`, `end_date >= start_date` |
| `color` | TEXT | `#rrggbb` (varsayılan `#a6e3a1`) |
| `created_at` | TEXT | `CURRENT_TIMESTAMP` (UTC) |

Takvim tabloları yalnızca `ui/calendar_window.py` tarafından (`CalendarRepository` ile) okunup yazılır.
Oturum verileriyle henüz bağlantılı değildir.

### 3.8 `if_then_plans` — Eğer-ise planları (implementation intentions)

| Kolon | Tip | Format |
|-------|-----|--------|
| `id` | INTEGER PK | |
| `weekdays` | TEXT | `0,2,4` (0 = Pazartesi) |
| `time` | TEXT | `HH:MM` ya da `NULL` (yalnızca durum ipuçlu plan; zamanla sorulmaz) |
| `cue` | TEXT | durum ipucu: "kahvaltıdan sonra" |
| `task_id` | INTEGER | `tasks.id` ya da `NULL` |
| `action` | TEXT | "1 oturum soru çöz" |
| `is_active` | BOOLEAN | `0` = silindi (soft delete; geçmiş sonuçlar kalır) |
| `created_at` | TEXT | `YYYY-MM-DD HH:MM:SS` yerel |

### 3.9 `plan_log` — Plan sonuçları

| Kolon | Tip | Format |
|-------|-----|--------|
| `plan_id` | INTEGER | `if_then_plans.id` |
| `day` | TEXT | mantıksal gün `YYYY-MM-DD` |
| `outcome` | TEXT | `started`, `skipped`, `snoozed` |
| `session_id` | INTEGER | "Başla" sonrası kaydedilen ilk oturum (`sessions_v2.id`) |
| `logged_at` | TEXT | yerel zaman |

Yazan: `core/plan_scheduler.py` (saati gelince sorar, 60 dk pencere) + `ui/main_window.py` (Başla / 10 dk ertele / Bugün atla).
Okuyan: `ui/side_panel.py` (bugünün planları, 28 günlük uyum). Kayıt düşmeyen geçmiş saatli plan = **kaçırıldı**
(uygulama kapalıydı); bugün henüz cevaplanmamış plan sayılmaz.

### 3.10 `review_state` — Konu başına aralıklı tekrar durumu

Konu = görev (alt görev varsa yaprak görevler, yoksa dersin kendisi). Tekrar takvimi 1 → 3 → 7 → 14 → 30 gün.

| Kolon | Tip | Format |
|-------|-----|--------|
| `task_id` | INTEGER PK | `tasks.id` |
| `step` | INTEGER | başarılı tekrar sayısı (0 = ilk tekrar bekleniyor) |
| `next_due` | TEXT | `YYYY-MM-DD` doğal vade |
| `last_review` | TEXT | `YYYY-MM-DD` son tekrar ya da konunun takvime alındığı gün |
| `lapses` | INTEGER | yalnızca kötü hatırlama (1–2) cevabıyla artar; kaçırılan gün sayılmaz |
| `created_at` | TEXT | yerel zaman |

### 3.11 `review_log` — Tekrar geçmişi

| Kolon | Tip | Format |
|-------|-----|--------|
| `task_id`, `session_id` | INTEGER | konu ve tekrar oturumu |
| `recall` | INTEGER | 1 Hiç · 2 Zor · 3 İyi · 4 Kolay |
| `day`, `reviewed_at` | TEXT | mantıksal gün / yerel zaman |
| `prev_step`, `prev_next_due`, `prev_last_review`, `prev_lapses` | | tekrardan önceki durum; aynı oturum için cevap değiştirilirse geri alınıp yeniden uygulanır |

**Akış** (`core/review_scheduler.py`, kullanıcıdan ek giriş istemez):
- Geri bildirim şeridinde **Okuma / Soru / Üretim** → konu takvime alınır, ilk tekrar yarın.
- **Tekrar** + 1–4 hatırlama puanı → ≥3: bir sonraki adım; ≤2: başa dön, yarın tekrar.
- Sınava bağlı derslerde (`calendar_events.task_id`): doğal vade sınavdan sonraya düşüyorsa sınavdan **bir gün öncesine** çekilir
  (o güne kadar tekrar yapılmadıysa); sınava ≤14 gün kala hiç çalışılmamış ya da >7 gündür dokunulmamış konular kuyruğa girer.
- Kuyruk günde en fazla 5 konu gösterir (sınava en yakın önce, sonra çok unutulan); gecikmiş konular borç olarak yığılmaz.
- Oturumun konusu `sessions_v2.task_name` üzerinden `tasks.name` (UNIQUE) ile bulunur.

**Süreklilik ızgarası** (`core/streak.py`, `ui/side_panel.py`) yeni veri tutmaz: `sessions_v2`'den son 18 haftanın
mantıksal gün bazında iş dakikalarını hesaplar. Renk seviyesi çalışılan günlerin çeyreklerine göre (GitHub gibi);
gün ≥25 dk ise aktif; tek boş gün seriyi bozmaz, iki gün üst üste boşluk bozar.

---

## 4. Veritabanı Dışındaki Veriler

### 4.1 Panel durum dosyası — `state.json`
- **Yazan:** `core/panel_bridge.py`, her saniye, atomik yazma (`.tmp` + `os.replace`).
- **Okuyan:** `plasmoid/org.mfdp.timer/contents/ui/main.qml` (`cat` ile okur; `ts` 3 sn'den eskiyse uygulamayı kapalı sayar).
- **Format:**
  ```json
  {"running": true, "mode": "countdown", "seconds": 1432, "color": "#89b4fa", "ts": 1760000000.12}
  ```
  `mode`: `countdown` | `countup`; `seconds`: timer'daki güncel değer; `color`: aktif görevin rengi; `ts`: Unix zamanı.
- Ters yön veri değil komut: widget `org.mfdp.Timer.Toggle()` D-Bus çağrısıyla duraklat/devam ettirir.

### 4.2 Takvim JSON değişim formatı
- **Kod:** `core/calendar_io.py` (`build_export`, `parse_import`, `AI_PROMPT`).
- **Amaç:** Kullanıcının dağınık ders/sınav listesini bir AI asistanına verip bu şablonda JSON almak ve içe aktarmak; ayrıca yedekleme.
- **Format:**
  ```json
  {
    "events": [{"title": "...", "date": "YYYY-MM-DD", "time": "HH:MM|null", "kind": "sinav|odev|toplanti|diger", "note": "...|null"}],
    "ranges": [{"label": "...", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "color": "#rrggbb"}]
  }
  ```
- İçe aktarmada doğrulama: geçersiz tarih → kayıt atlanır; geçersiz saat → `null`; bilinmeyen `kind` → `diger`;
  geçersiz renk → varsayılan. Sorunlar önizleme ekranında listelenir. İçe aktarma **ekler**, mevcut kayıtları silmez;
  aynı (`title`, `date`, `time`) olay veya aynı (`label`, `start_date`, `end_date`) aralık zaten varsa atlanır.

### 4.3 `QSettings` — mini pencere konumu
- `ui/mini_window.py`, anahtar `mini_window/pos` (QPoint). Diğer tüm ayarlar SQLite'tadır.

### 4.4 Bellekte tutulan çalışma zamanı verisi (kalıcı değil)
- `FocusSession` (core/timer.py): `active_seconds`, `total_seconds`, duraklama durumu, kesinti sayısı, aktif görev. Oturum kaydedilince `sessions_v2`'ye dönüşür.
- `AtomicAnalyzer.event_buffer`: oturum boyunca biriken olaylar (bkz. 3.2).
- `TaskManager._active_task_id`: seçili görev — **kalıcı değil**, uygulama yeniden açılınca seçim sıfırlanır.

---

## 5. Zaman ve "Gün" Kuralları

- Tüm zaman damgaları **saat dilimi bilgisi olmadan, yerel saat** olarak tutulur — istisna:
  `CURRENT_TIMESTAMP` kullanan `created_at` kolonları (UTC).
- **Mantıksal gün 03:00'te başlar** (`daily_report.DAY_START_HOUR = 3`): gece 01:30'da başlayan oturum
  önceki güne yazılır. Gün paneli, blok raporu ve manuel oturum girişi bu kuralı kullanır.
  `stats_window` grafikleri (`get_daily_trend`, `get_hourly_productivity`) ise **takvim günü** (00:00) kullanır —
  iki ekran gece yarısı ile 03:00 arasındaki oturumları farklı günlere sayabilir.
- **Blok:** aynı tag + görev için art arda gelen iş oturumları; aradaki boşluk ≤ 30 dk ise birleşir
  (`BLOCK_GAP_MINUTES`), molalar bloğu bölmez.

---

## 6. Bilinen Tutarsızlıklar / Dikkat Edilecekler

1. **FK/CASCADE uygulanmıyor** (bkz. §2). Oturum silme eklenirse olaylar elle silinmeli ya da her bağlantıda `PRAGMA foreign_keys = ON` açılmalı.
2. **Oturum ↔ görev bağı ada göre.** `sessions_v2.task_name` metin; görev yeniden adlandırılırsa geçmiş oturumlar o göreve sayılmaz. `task_id` kolonu yok.
3. **İki farklı zaman formatı:** `sessions_v2` `YYYY-MM-DD HH:MM:SS`, `atomic_events.timestamp` ISO `T` ayraçlı. Karşılaştırmalı sorgu yazarken dikkat.
4. **`elapsed_seconds` duvar saati,** net süre değil; duraklama sonrası olaylarda `metadata.active_seconds` kullanın.
5. **DB yolu göreli** (`focus_tracker.db`) ve `notifier.py` ses dosyalarını `os.getcwd()`'ye göre arar: uygulama proje kökünden başlatılmazsa yeni boş bir DB oluşur. `run.sh` bu yüzden `cd` yapar.
6. **Focus-shift / dikkat dağınıklığı verisi toplanmıyor;** README'deki "aktif pencere takibi" özelliği şu an bağlı değil.
7. **İki timer modeli aynı `Free Timer` modunu paylaşıyor.** 2026-10-16 öncesi Free Timer oturumları duraklatmalı;
   `completed` ve `interruption_count` anlamları farklı. Ayırmak için `session_started.metadata.timer_model = 'countup_v1'` kullanın.
8. **Manuel oturumlar** `Free Timer` olarak işaretlendiği için gerçek Free Timer oturumlarından ayırt edilemez ve atomik olayları yoktur.
