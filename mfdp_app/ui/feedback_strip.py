"""
FeedbackStrip - Bir iş oturumu kaydedilince timer'ın altında beliren geri bildirim şeridi.

- Odak puanı 1-5 (öznel; dakikanın yanında kalite sinyali — Goodhart'a karşı).
- Oturum türü: ne yaptığın, ne kadar çalıştığından daha çok şey söyler
  (kendini test etme ve tekrar en güçlü öğrenme teknikleri — Dunlosky ve ark. 2013).
İkisi de isteğe bağlı; seçim anında kaydedilir. Yeni oturum başlayınca şerit kapanır.
Düğmeler FlowLayout'tadır: pencere daraldıkça satırlara dağılır, üst üste binmez.
"""

from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
                               QButtonGroup, QWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal

from mfdp_app.ui.flow_layout import FlowLayout

RATING_HINTS = {
    1: "Hiç odaklanamadım",
    2: "Çoğunlukla dağınıktım",
    3: "Ara ara dağıldım",
    4: "Çoğunlukla odaktaydım",
    5: "Tamamen içindeydim",
}

RECALL_CHOICES = [
    (1, "1 · Hiç", "Hatırlayamadım"),
    (2, "2 · Zor", "Büyük çoğunluğunu zor hatırladım"),
    (3, "3 · İyi", "Çoğunu hatırladım"),
    (4, "4 · Kolay", "Rahatça hatırladım"),
]

SESSION_KINDS = [
    ("okuma", "Okuma", "Okuma / ders dinleme / not çıkarma"),
    ("soru", "Soru", "Soru / problem çözme"),
    ("tekrar", "Tekrar", "Kendini test etme, ezberden hatırlama, tekrar"),
    ("uretim", "Üretim", "Proje, kod, yazı"),
    ("diger", "Diğer", "Diğer"),
]


def _chip(text, tooltip, checkable=True):
    btn = QPushButton(text)
    btn.setObjectName("FeedbackChip")
    btn.setCheckable(checkable)
    btn.setToolTip(tooltip)
    btn.setCursor(Qt.PointingHandCursor)
    return btn


class FeedbackStrip(QFrame):
    rating_selected = Signal(int)
    kind_selected = Signal(str)
    recall_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FeedbackStrip")
        # Takipte olmayan işte (tekrar hatırlatması istenmeyen ders) hatırlama sorusu sorulmaz
        self.recall_allowed = True
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 6, 6, 6)
        outer.setSpacing(4)

        # Satır 1: odak puanı + tür (FlowLayout: sığmayan alt satıra geçer), sağda kapat
        top = QHBoxLayout()
        top.setSpacing(4)
        flow_host = QWidget()
        flow = FlowLayout(flow_host, hspacing=4, vspacing=4)

        lbl = QLabel("Odak:")
        lbl.setObjectName("FeedbackLabel")
        flow.addWidget(lbl)
        self.rating_group = QButtonGroup(self)
        for value in range(1, 6):
            btn = _chip(str(value), RATING_HINTS[value])
            btn.setFixedWidth(30)
            self.rating_group.addButton(btn, value)
            flow.addWidget(btn)
        self.rating_group.idClicked.connect(self.rating_selected.emit)

        lbl2 = QLabel("Tür:")
        lbl2.setObjectName("FeedbackLabel")
        flow.addWidget(lbl2)
        self.kind_group = QButtonGroup(self)
        self._kind_keys = {}
        for i, (key, text, tip) in enumerate(SESSION_KINDS):
            btn = _chip(text, tip)
            self.kind_group.addButton(btn, i)
            self._kind_keys[i] = key
            flow.addWidget(btn)
        self.kind_group.idClicked.connect(lambda i: self.kind_selected.emit(self._kind_keys[i]))
        top.addWidget(flow_host, 1)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("FeedbackClose")
        btn_close.setToolTip("Geç")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.hide)
        top.addWidget(btn_close, 0, Qt.AlignTop)
        outer.addLayout(top)

        # 'Tekrar' türünde: ne kadar hatırladın? (aralıklı tekrar takvimini ilerletir)
        self.recall_row = QWidget()
        recall = QVBoxLayout(self.recall_row)
        recall.setContentsMargins(0, 0, 0, 0)
        recall.setSpacing(4)
        lbl3 = QLabel("Notlara bakmadan ne kadar hatırladın?")
        lbl3.setObjectName("FeedbackLabel")
        lbl3.setWordWrap(True)   # dar şeritte satır kaydırır
        recall.addWidget(lbl3)
        chips_host = QWidget()
        chips = FlowLayout(chips_host, hspacing=4, vspacing=4)
        self.recall_group = QButtonGroup(self)
        for value, text, tip in RECALL_CHOICES:
            btn = _chip(text, tip)
            self.recall_group.addButton(btn, value)
            chips.addWidget(btn)
        recall.addWidget(chips_host)
        self.recall_group.idClicked.connect(self.recall_selected.emit)
        outer.addWidget(self.recall_row)
        self.recall_row.hide()
        self.kind_group.idClicked.connect(
            lambda i: self.recall_row.setVisible(self.recall_allowed and self._kind_keys[i] == "tekrar"))

        self.hide()

    def open_for_session(self):
        self.recall_row.hide()
        for group in (self.rating_group, self.kind_group, self.recall_group):
            group.setExclusive(False)
            for btn in group.buttons():
                btn.setChecked(False)
            group.setExclusive(True)
        self.show()
