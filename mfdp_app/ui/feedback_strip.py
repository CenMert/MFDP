"""
FeedbackStrip - Bir iş oturumu kaydedilince timer'ın altında beliren tek satırlık geri bildirim.

- Odak puanı 1-5 (öznel; dakikanın yanında kalite sinyali — Goodhart'a karşı).
- Oturum türü: ne yaptığın, ne kadar çalıştığından daha çok şey söyler
  (kendini test etme ve tekrar en güçlü öğrenme teknikleri — Dunlosky ve ark. 2013).
İkisi de isteğe bağlı; seçim anında kaydedilir. Yeni oturum başlayınca şerit kapanır.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QButtonGroup, QWidget
from PySide6.QtCore import Qt, Signal

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


class FeedbackStrip(QFrame):
    rating_selected = Signal(int)
    kind_selected = Signal(str)
    recall_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FeedbackStrip")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 6, 6, 6)
        outer.setSpacing(4)
        row = QHBoxLayout()
        row.setSpacing(4)
        outer.addLayout(row)

        lbl = QLabel("Odak:")
        lbl.setObjectName("FeedbackLabel")
        row.addWidget(lbl)
        self.rating_group = QButtonGroup(self)
        for value in range(1, 6):
            btn = QPushButton(str(value))
            btn.setObjectName("FeedbackChip")
            btn.setCheckable(True)
            btn.setFixedWidth(30)
            btn.setToolTip(RATING_HINTS[value])
            btn.setCursor(Qt.PointingHandCursor)
            self.rating_group.addButton(btn, value)
            row.addWidget(btn)
        self.rating_group.idClicked.connect(self.rating_selected.emit)

        row.addSpacing(12)
        lbl2 = QLabel("Tür:")
        lbl2.setObjectName("FeedbackLabel")
        row.addWidget(lbl2)
        self.kind_group = QButtonGroup(self)
        self._kind_keys = {}
        for i, (key, text, tip) in enumerate(SESSION_KINDS):
            btn = QPushButton(text)
            btn.setObjectName("FeedbackChip")
            btn.setCheckable(True)
            btn.setToolTip(tip)
            btn.setCursor(Qt.PointingHandCursor)
            self.kind_group.addButton(btn, i)
            self._kind_keys[i] = key
            row.addWidget(btn)
        self.kind_group.idClicked.connect(lambda i: self.kind_selected.emit(self._kind_keys[i]))

        row.addStretch()
        btn_close = QPushButton("✕")
        btn_close.setObjectName("FeedbackClose")
        btn_close.setToolTip("Geç")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.hide)
        row.addWidget(btn_close)

        # 'Tekrar' türünde: ne kadar hatırladın? (aralıklı tekrar takvimini ilerletir)
        self.recall_row = QWidget()
        recall = QHBoxLayout(self.recall_row)
        recall.setContentsMargins(0, 0, 0, 0)
        recall.setSpacing(4)
        lbl3 = QLabel("Notlara bakmadan ne kadar hatırladın?")
        lbl3.setObjectName("FeedbackLabel")
        recall.addWidget(lbl3)
        self.recall_group = QButtonGroup(self)
        for value, text, tip in RECALL_CHOICES:
            btn = QPushButton(text)
            btn.setObjectName("FeedbackChip")
            btn.setCheckable(True)
            btn.setToolTip(tip)
            btn.setCursor(Qt.PointingHandCursor)
            self.recall_group.addButton(btn, value)
            recall.addWidget(btn)
        recall.addStretch()
        self.recall_group.idClicked.connect(self.recall_selected.emit)
        outer.addWidget(self.recall_row)
        self.recall_row.hide()
        self.kind_group.idClicked.connect(lambda i: self.recall_row.setVisible(self._kind_keys[i] == "tekrar"))

        self.hide()

    def open_for_session(self):
        self.recall_row.hide()
        for group in (self.rating_group, self.kind_group, self.recall_group):
            group.setExclusive(False)
            for btn in group.buttons():
                btn.setChecked(False)
            group.setExclusive(True)
        self.show()
