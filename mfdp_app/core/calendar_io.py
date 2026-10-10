"""
Calendar import/export helpers (pure logic, no UI, no DB writes).

The JSON format is the contract between the app and any AI assistant that
converts a user's messy schedule into calendar entries.
"""

import datetime
import json
import re
from typing import Dict, List, Tuple

EVENT_KINDS = ("sinav", "odev", "toplanti", "diger")
DEFAULT_RANGE_COLOR = "#a6e3a1"

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

AI_PROMPT = """Sen bir takvim dönüştürücüsüsün. Aşağıda vereceğim dosyayı/metni (ödev, sınav, toplantı listesi, akademik takvim vb.) okuyup, aşağıdaki JSON şablonuna birebir uyan TEK bir JSON çıktısı üreteceksin.

## ŞABLON
{
  "events": [
    {"title": "Fizik kısa sınav", "date": "2026-10-05", "time": "09:30", "kind": "sinav", "note": "Bölüm 1-3"}
  ],
  "ranges": [
    {"label": "Sınav haftası", "start_date": "2026-10-12", "end_date": "2026-10-21", "color": "#fab387"}
  ]
}

## KURALLAR
- "events": tek günlük kayıtlar (sınav, ödev teslimi, toplantı). "ranges": birden fazla günlük dönemler (sınav haftası, tatil, bütünleme vb.).
- "date", "start_date", "end_date": mutlaka YYYY-MM-DD biçiminde ve gerçek bir tarih olmalı.
- "time": HH:MM (24 saat) ya da null. Saat belli değilse null yaz, uydurma.
- "kind" yalnızca şunlardan biri: "sinav", "odev", "toplanti", "diger". Emin değilsen "diger" yaz.
- "note": isteğe bağlı kısa metin ya da null.
- "color": "#rrggbb" biçiminde. Emin değilsen "#a6e3a1" kullan.
- "end_date" asla "start_date"ten önce olamaz.
- Ders programı (haftalık ders saatleri) EKLEME. Sadece sınav, ödev, toplantı ve tarih aralıklarını al.

## EMİN OLMADIĞINDA (ÇOK ÖNEMLİ)
- Hiçbir bilgiyi tahmin etme, uydurma ve sessizce atlama.
- Yılın, tarihin, saatin, türün ya da bir kaydın neyi kastettiğinin belirsiz olduğu HER durumda JSON üretmeden ÖNCE bana numaralı sorular sor ve cevaplarımı bekle.
- Okuyamadığın ya da anlamadığın bir satır varsa, hangisi olduğunu söyleyip bana sor.
- Tüm belirsizlikler çözüldükten sonra JSON'u üret.

## ÇIKTI BİÇİMİ
- Son cevabında yalnızca geçerli JSON olsun. Açıklama, giriş ya da sonuç cümlesi ekleme. Tek bir ```json kod bloğu içinde ver.
- JSON'u vermeden hemen önce kontrol et: tüm tarihler geçerli mi, tüm "kind" değerleri izinli mi, her aralıkta bitiş >= başlangıç mi.

## DÖNÜŞTÜRÜLECEK İÇERİK
(Buraya dosyanın içeriğini yapıştır ya da dosyayı ekle.)
"""


def build_export(events: List[Dict], ranges: List[Dict]) -> str:
    """Serialize calendar data into the exchange format."""
    data = {
        "events": [
            {"title": e["title"], "date": e["date"], "time": e["time"],
             "kind": e["kind"], "note": e["note"]}
            for e in events
        ],
        "ranges": [
            {"label": r["label"], "start_date": r["start_date"],
             "end_date": r["end_date"], "color": r["color"]}
            for r in ranges
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def _strip_fences(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text


def _valid_date(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.date.fromisoformat(value)
        return len(value) == 10
    except ValueError:
        return False


def parse_import(text: str) -> Tuple[List[Dict], List[Dict], List[str]]:
    """
    Validate AI/user supplied JSON.

    Returns (events, ranges, problems). Invalid entries are skipped and
    reported in `problems`; a malformed document yields empty lists.
    """
    try:
        data = json.loads(_strip_fences(text))
    except json.JSONDecodeError as e:
        return [], [], [f"Geçerli JSON değil: {e}"]
    if not isinstance(data, dict):
        return [], [], ["Kök öğe bir nesne olmalı ({ \"events\": [...], \"ranges\": [...] })."]

    events, ranges, problems = [], [], []

    for i, e in enumerate(data.get("events") or [], 1):
        where = f"events[{i}]"
        if not isinstance(e, dict):
            problems.append(f"{where}: nesne değil, atlandı.")
            continue
        title = e.get("title")
        if not isinstance(title, str) or not title.strip():
            problems.append(f"{where}: başlık boş, atlandı.")
            continue
        if not _valid_date(e.get("date")):
            problems.append(f"{where} ({title}): geçersiz tarih {e.get('date')!r}, atlandı.")
            continue
        time = e.get("time")
        if time is not None and not (isinstance(time, str) and _TIME.match(time)):
            problems.append(f"{where} ({title}): geçersiz saat {time!r}, saat boş bırakıldı.")
            time = None
        kind = e.get("kind")
        if kind not in EVENT_KINDS:
            problems.append(f"{where} ({title}): bilinmeyen tür {kind!r}, 'diger' yapıldı.")
            kind = "diger"
        note = e.get("note")
        events.append({"title": title.strip(), "date": e["date"], "time": time,
                       "kind": kind, "note": note if isinstance(note, str) and note else None})

    for i, r in enumerate(data.get("ranges") or [], 1):
        where = f"ranges[{i}]"
        if not isinstance(r, dict):
            problems.append(f"{where}: nesne değil, atlandı.")
            continue
        label = r.get("label")
        if not isinstance(label, str) or not label.strip():
            problems.append(f"{where}: etiket boş, atlandı.")
            continue
        start, end = r.get("start_date"), r.get("end_date")
        if not _valid_date(start) or not _valid_date(end):
            problems.append(f"{where} ({label}): geçersiz tarih, atlandı.")
            continue
        if end < start:
            problems.append(f"{where} ({label}): bitiş başlangıçtan önce, atlandı.")
            continue
        color = r.get("color")
        if not (isinstance(color, str) and _HEX.match(color)):
            if color is not None:
                problems.append(f"{where} ({label}): geçersiz renk {color!r}, varsayılan kullanıldı.")
            color = DEFAULT_RANGE_COLOR
        ranges.append({"label": label.strip(), "start_date": start, "end_date": end, "color": color})

    if not events and not ranges and not problems:
        problems.append("Dosyada hiç olay ya da aralık yok.")
    return events, ranges, problems
