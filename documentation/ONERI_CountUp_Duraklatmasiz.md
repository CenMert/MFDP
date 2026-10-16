# Öneri: Count-up birincil, duraklatma yok

*2026-10-16 · Kaynaklar: `focus_tracker.db` (salt okunur, 169 oturum, 2026-01-09 → 2026-10-16),
`reports/Çalışma verimi ve Pomodoro.md`, `documentation/VERI_HARITASI.md`*

## Karar (2026-10-16) — uygulandı: `countup-first` branch'i

Kullanıcının kararı öneriyi sadeleştirdi: **ayrı mola akışı yok.**
- Count-up açılışta varsayılan mod. Butonlar: **Başlat/Bitir · İç kesinti (I) · Dış kesinti (E)**. Duraklatma ve Sıfırla yok.
- **Bitir = oturum biter.** Devam etmek yeni bir oturumdur. Böylece:
  - **Mola süresi** iki oturum arasındaki boşluktan ölçülür, ayrı bir mola zamanlayıcısına gerek kalmaz.
  - **Odak süresinin nasıl düştüğü** count-up oturum uzunluklarından görülür (gün içinde k'ıncı oturum, haftalar boyunca trend).
- 60 sn altındaki oturumlar yanlış başlatma sayılıp kaydedilmez.
- Yeni oturumlar `timer_model: "countup_v1"` ile etiketlenir. `end_reason` ve iç/dış kesinti `reason`'ı `atomic_events`'e yazılır.
- Mini pencere ve panel tıklaması count-up'ta başlat/bitir yapar.
- Pomodoro (geri sayım) modu şimdilik **olduğu gibi** duruyor (duraklatmalı). Kaldırma kararı Faz 6 değerlendirmesine kaldı.
- Aşağıdaki plandaki Faz 3 (mola diyaloğu) **iptal**. Hedef/zil (Faz 1) ve odak puanı (Faz 4) henüz yapılmadı.

Analiz için örnek sorgu (mola = iki oturum arası boşluk):
```sql
WITH s AS (
  SELECT id, start_time, end_time, duration_seconds,
         LAG(end_time) OVER (ORDER BY start_time) AS prev_end
  FROM sessions_v2 WHERE mode = 'Free Timer'
)
SELECT id, duration_seconds / 60.0 AS focus_min,
       (julianday(start_time) - julianday(prev_end)) * 1440 AS break_min
FROM s
WHERE prev_end IS NOT NULL
  AND (julianday(start_time) - julianday(prev_end)) * 1440 < 120;  -- aynı çalışma bloğu
```

## Kısa cevap (ilk öneri)

**İkisine de evet, ama iki düzeltmeyle:**

1. Count-up birincil olsun, fakat **geri sayımı silme; count-up'ın içine "isteğe bağlı hedef" olarak göm.**
   Tek bir zamanlayıcı olur: yukarı sayar; hedef koyarsan hedefte çalar ama durmaz.
2. Duraklatmayı kaldır, fakat yerine iki şey koy:
   - **"Bitir"**: oturumu kaydeder. Aynı göreve 30 dk içinde dönersen gün paneli zaten aynı bloğa birleştiriyor (`BLOCK_GAP_MINUTES`). Yani veri kaybı olmaz, sadece dürüstleşir.
   - **"Kesinti işaretle"**: oturumu durdurmadan iç/dış kesinti kaydeder (Cirillo'nun `'` ve `-` çetelesi).

En büyük risk molaların tamamen kaybolması (aşağıda verisi var). O yüzden plana **açık bir mola akışı** ekliyorum.

---

## 1. Verin ne söylüyor

| Gözlem | Sayı | Yorum |
|--------|------|-------|
| Focus'ta seçtiğin süre | 60 dk ×43, 90 dk ×17, 45 dk ×14, 10 dk ×11; **25 dk hiç yok** | Zaten klasik Pomodoro kullanmıyorsun; uzun, değişken bloklar seçiyorsun. |
| Free Timer oturum süresi | medyan **52 dk**, çeyrekler 29–75 dk, en uzun 180 dk | Doğal odak süren Focus hedeflerinle aynı bölgede. Geri sayım pek bir şey eklemiyor. |
| Free Timer payı | Ocak: 10/44 oturum → Haziran: 20/40 → Ekim: 7/13 | Count-up'a zaten kendiliğinden kayıyorsun. |
| Hiç kesilmeyen Focus oturumları | **46/46 tamamlandı** | |
| Duraklatılan veya resetlenen Focus oturumları | **31/59 tamamlandı, 28'i yarım kaldı** | ⚠️ Reset de sayacı 1 artırıyor, bu yüzden yarım kalanlar otomatik olarak bu grupta. Yine de 31 tamamlanan oturum gerçek bir duraklatma içeriyor. |
| Duraklatılan Focus oturumlarında duvar saati − net süre | ortalama **40 dk** | Duraklatma pratikte kısa bir ara değil, **oturumu bırakıp sonra dönmek**. Ayrı oturum olarak kaydedilmesi daha doğru. |
| Duraklatılan Free Timer'da aynı fark | ortalama 21 dk | Aynı durum. |
| Mola kullanımı | 105 Focus oturumuna karşı **17** mola oturumu (%16) | Molaları zaten çoğunlukla atlıyorsun. Count-up'ta bu daha da kötüleşebilir. |

Veri sınırları:
- Ocak verisinin bir kısmı seed olabilir.
- Atomik olayların çoğu seed veya eski formatta (yalnızca 2 kesintide `reason` var, 1 `pause_seconds` var). Bu yüzden duraklatma analizi oturum tablosuna dayanıyor.

## 2. Literatür ne söylüyor (rapordan)

- **Smits ve ark. 2025 (N=94):** Pomodoro, Flowtime ve serbest mola arasında **görev tamamlama farkı yok** (%70, %69, %67). Count-up'a geçmek verimi düşürmez.
- **Biwer ve ark. 2023 (N=87):** Molalarını kendi seçenler daha uzun çalıştı ama **daha fazla yorgunluk ve daha az konsantrasyon** bildirdi. Count-up'ın asıl riski bu, mola tasarımı bunun için şart.
- **Albulescu ve ark. 2022:** Kısa molalar enerjiyi artırıp yorgunluğu azaltıyor. **Telefonla geçen mola mola sayılmaz** (Kang & Kurtzberg 2019).
- **Cirillo'nun kendi kuralı:** Pomodoro bölünemez; kesilirse **iptal edilir, duraklatılmaz.** Senin duraklatmayı kaldırma fikrin aslında yöntemin orijinaline daha yakın.
- **Mark ve ark. 2008:** Kesintiler çıktıyı değil **stresi** artırıyor. Bu yüzden kesintiyi saklamak yerine görünür kılmak gerekiyor.
- **Goodhart riski:** Count-up'ta "dakika" tek başına hedef olursa oturumlar şişer. Kalite sinyali şart (1–5 odak puanı).

## 3. Analitik kazanç

Geri sayım veriyi **sansürlüyor**: zil çalınca durduğun için gerçekte ne kadar odaklanabildiğini hiç görmüyorsun.
Count-up + duraklatmasız model ise her oturumun **doğal bitiş süresini** veriyor. Bununla şunlar hesaplanabilir:

- **Kişisel odak süresi eğrisi:** "X dakikayı geçen oturumların oranı" (survival curve). Medyan ve %75 noktası, sana önerilecek hedefin kendisi olur.
- **Saate, güne ve göreve göre doğal süre:** hangi görevde ve hangi saatte daha uzun dayanıyorsun.
- **Kesinti yoğunluğu:** `interruption_detected` (iç/dış) bölü net saat. Artık reset ve duraklatmayla kirlenmez.
- **Hedef tutturma oranı:** hedef koyduğun oturumlarda `süre ≥ hedef` olma oranı. Bu, `completed` alanının count-up'taki anlamlı karşılığı.
- **Mola uyumu ve mola taşması:** mola sayısı ve süresi, önerilen molaya göre ne kadar uzadığı.
- **Puan ile süre ilişkisi:** uzun oturumlar gerçekten iyi mi geçiyor, yoksa şişiyor mu.

## 4. Tasarım

### 4.1 Tek zamanlayıcı
```
[ 00:47:12 ]   Görev: Sinyaller ve Sistemler   Hedef: 60 dk (isteğe bağlı)
[ Bitir ]  [ Kesinti: İç (I) ]  [ Kesinti: Dış (E) ]  [ İptal ]
```
- **Hedef:** boş bırakılabilir. Varsayılan olarak kişisel medyan süren önerilir.
  - Hedefte bir kez ses çalar, sayaç akmaya devam eder.
  - Hedef × 1.5 aşılınca nazik bir uyarı gelir ("90 dk oldu, mola?").
- **Bitir:** oturumu kaydeder ve mola önerisini açar.
- **Kesinti tuşları:** oturumu durdurmaz. `interruption_detected` olayını `reason = internal|external` ile yazar.
- **İptal:** 1 dakikanın altındaki yanlış başlatmaları kaydetmeden atar. Daha uzun oturumlarda "Bitir" ile aynı şeyi yapar ama `end_reason = cancelled` yazar.
- **Klasik Pomodoro:** "Hedef 25 + otomatik mola" ön ayarı olarak kalır. Ayrı bir mod gerekmez.

### 4.2 Mola akışı
- Bitir'e basınca önerilen mola gelir: **çalışma süresi / 5** (Flowtime oranı), en az 5, en fazla 20 dakika. Kullanıcı süreyi değiştirebilir.
- Mola **geri sayar** (molada geri sayım işe yarar: dönüş saatini belirler).
  - `break_started` ve `break_ended` olayları kaydedilir. Bu olaylar zaten tanımlı ama şu an hiçbir yerden çağrılmıyor; mola akışıyla bağlanır.
  - Mola bitince ses çalar. Molanın ne kadar uzadığı kaydedilir.
- "Molayı atla" seçeneği var ama atlama da kaydedilir. Mola uyumu metriği bu kayıttan hesaplanır.

### 4.3 Oturum sonu (2 saniyelik)
- **Odak puanı 1–5**, tek tıkla; atlanabilir. `session_completed` olayının metadata'sına `focus_rating` olarak yazılır, böylece şema değişmez.

### 4.4 Veri modeli değişiklikleri (minimum)
| Alan | Değişiklik |
|------|-----------|
| `sessions_v2.mode` | Yeni oturumlar `Free Timer` olarak kalır. Böylece mevcut istatistik sorguları bozulmaz. |
| `sessions_v2.planned_duration_minutes` | Hedef varsa hedef dakikası, yoksa `NULL`. |
| `sessions_v2.completed` | Yeni anlamı: hedef varsa `süre ≥ hedef`; hedef yoksa normal Bitir = 1, iptal veya uygulama kapanışı = 0. |
| `sessions_v2.interruption_count` | Yeni anlamı: yalnızca işaretlenen kesintiler. Reset artık bu sayaca eklenmez. |
| `session_started` metadata | `timer_model: "countup_v1"` eklenir. Analizlerde eski ve yeni veri **bu alana göre ayrılır**, çünkü iki dönemin `completed` ve `interruption_count` anlamları farklı. |
| `session_completed` / `session_abandoned` metadata | `end_reason` (`finish`, `cancelled`, `app_exit`), `target_minutes` ve `focus_rating` eklenir. |
| Yeni olaylar | `break_started`, `break_ended` (`suggested_seconds`, `actual_seconds`, `skipped`). |

## 5. Uygulama planı

| Faz | İş | Dosyalar | Bitti sayılır |
|-----|----|----------|---------------|
| **0. Referans** | Bugünkü metrikleri `documentation/` altına kaydet (bu dokümandaki tablo). | — | ✅ |
| **1. Tek zamanlayıcı** | `CountUpTimer`'a hedef, hedefte zil ve aşım uyarısı ekle. Ana ekranda count-up varsayılan olsun; geri sayım "Klasik Pomodoro" ön ayarına dönüşsün. | `core/timer.py`, `ui/main_window.py`, `ui/settings_dialog.py` (varsayılan hedef, mola oranı) | Hedefli ve hedefsiz oturum doğru kaydediliyor. |
| **2. Duraklatmayı kaldır** | `start_stop` yerine `start` ve `finish`. Kesinti tuşları I ve E. Mini pencere tıklaması ile panel widget'ının `Toggle` çağrısı başlat/bitir olur. | `core/timer.py`, `ui/main_window.py`, `ui/mini_window.py`, `core/panel_bridge.py`, plasmoid QML | Hiçbir yolla duraklatma yapılamıyor; kesinti tuşları olay yazıyor. |
| **3. Mola akışı** | Önerilen mola diyaloğu, mola geri sayımı, `break_*` olayları, atlama ve taşma kaydı. | `core/timer.py` (mola sayacı), yeni `ui/break_dialog.py`, `core/atomic_analyzer.py` (zaten hazır) | Mola uyumu DB'den hesaplanabiliyor. |
| **4. Oturum sonu puanı** | 1–5 tek tık; `focus_rating` metadata'ya yazılır. | `ui/main_window.py` veya küçük bir diyalog | — |
| **5. Analitik** | İstatistiklere sekmeler ekle: doğal süre eğrisi, hedef tutturma, kesinti/saat, mola uyumu, puan-süre ilişkisi. Hepsi `timer_model`'e göre filtrelenir. `daily_report` blok mantığı aynen kalır. | `db/session_repository.py`, `db/atomic_event_repository.py`, `ui/stats_window.py` | — |
| **6. Değerlendirme (2–4 hafta sonra)** | Faz 0 referansıyla karşılaştır (aşağıdaki ölçütler). İyiyse `PmdrCountdownTimer` ve eski `PomodoroTimer` kodunu sil. | `core/timer.py` | Karar verildi. |

**Faz 6 başarı ölçütleri** (N-of-1 deney; kesin kanıt değil, yön gösterir):
- Günlük net odak süresi referansın altına düşmedi.
- Ortalama odak puanı ≥ 3.5 ve uzun oturumlarda düşmüyor.
- Mola uyumu %16'dan anlamlı şekilde arttı (hedef: ≥ %50).
- Kesinti/saat ölçülebilir hale geldi. İlk kez gerçek bir referans değerimiz olacak.

## 6. Riskler

| Risk | Önlem |
|------|-------|
| Molalar kaybolur, yorgunluk artar (Biwer 2023) | Bitir'den sonra varsayılan olarak mola gelir; atlamak bilinçli bir tık ister. Aşım uyarısı var. |
| Oturumlar şişer, "dakika avcılığı" (Goodhart) | Odak puanı ve kesinti/saat dakikanın yanında gösterilir. Süre sıralaması veya rozeti yok. |
| Tuvalet veya kapı gibi kısa aralar duraklatmadan nasıl? | Kısa dış kesinti: E'ye bas, devam et. Uzun süreceksen Bitir; dönünce aynı bloğa birleşir. |
| Eski ve yeni veri karışır | `timer_model` etiketi. Ayrıca istatistik sorgularına bu alana göre filtre eklenir. |
| Panel widget'ı ve mini pencere davranışı değişir | Faz 2'de üçü birlikte güncellenir. Tıklama artık duraklatma değil, başlat/bitir. |
