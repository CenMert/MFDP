# MFDP İkon Listesi

Uygulamanın ihtiyaç duyduğu ikonların kontrol listesi. Hazırladığın ikonu ilgili
klasöre koy ve satırdaki kutuyu işaretle.

## Format

- **SVG**, `viewBox="0 0 24 24"`, tek renk, stroke 1.5–2px
- Varsayılan renk `#cdd6f4` (Catppuccin Mocha "text" — `ui/styles.py` ile uyumlu);
  durum ikonlarında accent: yeşil `#a6e3a1`, kırmızı `#f38ba8`, sarı `#f9e2af`, mavi `#89b4fa`
- Dosya adı `kebab-case.svg` (aşağıdaki adlarla birebir)
- Öncelik: **P1** = ana pencere + DND + takvim · **P2** = görev / istatistik · **P3** = dekoratif

> Not: İkonların koda bağlanması (`QIcon` + `setIcon`) henüz yapılmadı. İkonlar hazır
> olduğunda ayrı bir adım olarak yapılacak. Şu an `mfdp.svg` dışındaki her yer metin/emoji.

---

## app/

| ✓ | Dosya | Kullanım yeri | Şu an | Öncelik |
|---|---|---|---|---|
| [x] | `../mfdp.svg` | `main.py:44`, `mfdp.desktop` | uygulama ikonu (mevcut, taşıma!) | P1 |
| [ ] | `mfdp-tray.svg` | sistem tepsisi (ileride) | — monokrom versiyon | P3 |

## timer/

| ✓ | Dosya | Kullanım yeri | Şu an | Öncelik |
|---|---|---|---|---|
| [ ] | `play.svg` | `ui/main_window.py:190,206` | "Başlat" / "Devam Et" | P1 |
| [ ] | `pause.svg` | `ui/main_window.py:387,398` | "Duraklat" | P1 |
| [ ] | `reset.svg` | `ui/main_window.py:197,214` | "Sıfırla" | P1 |
| [ ] | `complete.svg` | `ui/main_window.py:221` | "Tamamla" | P1 |
| [ ] | `mode-countdown.svg` | `ui/main_window.py:100,359` | "Count Down - Pomodoro" | P1 |
| [ ] | `mode-countup.svg` | `ui/main_window.py:337` | "Count Up - Free Timer" | P1 |
| [ ] | `focus.svg` | `ui/main_window.py:233` | "Focus" mod butonu | P1 |
| [ ] | `short-break.svg` | `ui/main_window.py:233` | "Kısa Mola" | P1 |
| [ ] | `long-break.svg` | `ui/main_window.py:233` | "Uzun Mola" | P1 |
| [ ] | `gong.svg` | `ui/main_window.py:246` | "Gong Sesi" (açık) | P2 |
| [ ] | `gong-off.svg` | `ui/main_window.py:246` | "Gong Sesi" (kapalı) | P2 |
| [ ] | `mini-window.svg` | `ui/main_window.py:308`, `ui/mini_window.py` | "Mini" | P2 |

## dnd/

| ✓ | Dosya | Kullanım yeri | Şu an | Öncelik |
|---|---|---|---|---|
| [ ] | `dnd-on.svg` | `ui/main_window.py:256` | 🔕 (DND açık, Ctrl+D) | P1 |
| [ ] | `dnd-off.svg` | `ui/main_window.py:256` | 🔕 (bildirimler açık) | P1 |

## tasks/

| ✓ | Dosya | Kullanım yeri | Şu an | Öncelik |
|---|---|---|---|---|
| [ ] | `tasks.svg` | `ui/main_window.py:268` | "Tasklar" | P1 |
| [ ] | `task-tree.svg` | `ui/main_window.py:278` | "Hiyerarşik Görevler" | P1 |
| [ ] | `tag.svg` | `ui/task_window.py:201`, `ui/main_window.py:138` | 🏷️ | P2 |
| [ ] | `task-done.svg` | `ui/task_window.py:210` | ✓ | P2 |
| [ ] | `set-active.svg` | `ui/task_window.py:65` | "Aktif Task Olarak Ayarla" | P2 |
| [ ] | `add.svg` | görev ekleme | — | P2 |
| [ ] | `add-subtask.svg` | `ui/recursive_task_window.py:99` | "Seçili Görevin Alt Görevi Olarak Ekle" | P2 |
| [ ] | `save.svg` | `ui/task_window.py:127`, `ui/recursive_task_window.py:157`, `ui/settings_dialog.py:93` | "Kaydet" | P2 |
| [ ] | `delete.svg` | `ui/task_window.py:132`, `ui/recursive_task_window.py:164` | "Sil" | P2 |
| [ ] | `clear.svg` | `ui/task_window.py:137`, `ui/recursive_task_window.py:169` | "Temizle" | P2 |
| [ ] | `color-picker.svg` | `ui/task_window.py:110` | "Renk Seç" | P2 |
| [ ] | `duration.svg` | `ui/task_window.py:93` | "Belirli süre ata" | P3 |
| [ ] | `tip.svg` | `ui/recursive_task_window.py:148` | 💡 | P3 |

## stats/

| ✓ | Dosya | Kullanım yeri | Şu an | Öncelik |
|---|---|---|---|---|
| [ ] | `stats.svg` | `ui/main_window.py:288` | "İstatistik" | P1 |
| [ ] | `add-session.svg` | `ui/stats_window.py:81` | "＋ Oturum Ekle" | P2 |
| [ ] | `chart-trend.svg` | `ui/stats_window.py:59` | sekme "Günlük Trend" | P2 |
| [ ] | `chart-tag.svg` | `ui/stats_window.py:60` | sekme "Tag Bazlı" | P2 |
| [ ] | `chart-pie.svg` | `ui/stats_window.py:61` | sekme "Tag Dağılımı" | P2 |
| [ ] | `chart-hourly.svg` | `ui/stats_window.py:62` | sekme "Saatlik" | P2 |
| [ ] | `heatmap.svg` | `ui/stats_window.py:63` | sekme "Atomic Harita" | P2 |
| [ ] | `quality.svg` | `ui/stats_window.py:64` | sekme "Kalite" | P2 |
| [ ] | `quality-excellent.svg` | `ui/stats_window.py:491` | 🚀 | P3 |
| [ ] | `quality-balanced.svg` | `ui/stats_window.py:493` | ⚖️ | P3 |
| [ ] | `quality-warning.svg` | `ui/stats_window.py:495` | ⚠️ | P3 |
| [ ] | `clock-picker.svg` | `ui/manual_session_dialog.py:216` | 🕒 | P2 |
| [ ] | `target.svg` | `ui/block_detail_dialog.py:239` | 🎯 | P3 |

## calendar/

| ✓ | Dosya | Kullanım yeri | Şu an | Öncelik |
|---|---|---|---|---|
| [ ] | `calendar.svg` | `ui/main_window.py:298`, pencere `ui/calendar_window.py:428` | "Takvim" | P1 |
| [ ] | `today.svg` | `ui/calendar_window.py:440` | "Bugün" | P1 |
| [ ] | `event-add.svg` | `ui/calendar_window.py:276,297` | "Ekle" | P1 |
| [ ] | `event-delete.svg` | `ui/calendar_window.py:252` | "Sil" | P1 |
| [ ] | `event-time.svg` | `ui/calendar_window.py:272` | "Saat" onay kutusu | P2 |
| [ ] | `import.svg` | `ui/calendar_window.py:364,447` | "İçe aktar" | P1 |
| [ ] | `export.svg` | `ui/calendar_window.py:448` | "Dışa aktar" | P1 |
| [ ] | `file-open.svg` | `ui/calendar_window.py:348` | "Dosyadan yükle" | P2 |
| [ ] | `ai-prompt-copy.svg` | `ui/calendar_window.py:347` | "YZ istemini kopyala" | P2 |
| [ ] | `preview.svg` | `ui/calendar_window.py:363` | "Önizle" | P2 |
| [ ] | `session-block.svg` | `ui/day_panel.py:46` | gün paneli oturum bloğu | P3 |

## common/

| ✓ | Dosya | Kullanım yeri | Şu an | Öncelik |
|---|---|---|---|---|
| [ ] | `chevron-left.svg` | `ui/calendar_window.py:439`, `ui/day_panel.py:112` | ◀ | P1 |
| [ ] | `chevron-right.svg` | `ui/calendar_window.py:439`, `ui/day_panel.py:113` | ▶ | P1 |
| [ ] | `settings.svg` | `ui/main_window.py:316` | "Ayarlar" | P1 |
| [ ] | `update-check.svg` | `ui/settings_dialog.py:76` | "Güncellemeleri Kontrol Et" | P3 |
| [ ] | `close.svg` | `ui/task_window.py:152`, `ui/recursive_task_window.py:184` | "Kapat" | P2 |
| [ ] | `cancel.svg` | `ui/manual_session_dialog.py:190` | "İptal" | P2 |
| [ ] | `warning.svg` | `ui/manual_session_dialog.py:281`, `ui/block_detail_dialog.py:132` | ⚠ | P2 |
| [ ] | `info.svg` | genel bilgi notları | — | P3 |
| [ ] | `expand.svg` | `ui/manual_session_dialog.py:252` | "Ayrıntılı ›" | P3 |
| [ ] | `collapse.svg` | `ui/manual_session_dialog.py:252` | "‹ Basit" | P3 |

---

**Toplam:** 63 ikon (1 mevcut) — P1: 24 · P2: 27 · P3: 12
