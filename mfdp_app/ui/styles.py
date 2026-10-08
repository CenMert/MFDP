# mfdp_app/ui/styles.py

MODERN_DARK_THEME = """
/* Genel Pencere Ayarları */
QMainWindow {
    background-color: #1e1e2e; /* Koyu Lacivert/Gri (Modern IDE teması gibi) */
}

QWidget {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 14px;
    color: #cdd6f4; /* Yumuşak Beyaz */
}

/* Etiketler (Labels) */
QLabel {
    color: #cdd6f4;
}

/* Zamanlayıcıya özel stil (ID ile yakalayacağız) */
QLabel#TimerLabel {
    font-size: 90px;
    font-weight: bold;
    color: #a6e3a1; /* Pastel Yeşil */
    margin: 20px 0;
}

/* Durum Etiketi (Focus/Break) */
QLabel#StatusLabel {
    font-size: 28px;
    font-weight: 600;
    color: #f9e2af; /* Pastel Sarı */
}

/* Butonlar */
QPushButton {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px; /* Yuvarlatılmış köşeler */
    color: #ffffff;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #45475a; /* Üzerine gelince biraz açıl */
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #1e1e2e; /* Tıklayınca gömül */
    border-color: #a6e3a1;
}

/* Başlat Butonu için özel renk */
QPushButton#StartButton {
    background-color: #a6e3a1;
    color: #1e1e2e; /* Yazı rengi koyu olsun */
    border: none;
}
QPushButton#StartButton:hover {
    background-color: #94e2d5;
}

/* Mod Butonları (Focus, Short, Long) */
QPushButton#ModeButton {
    background-color: transparent;
    border: 1px solid #45475a;
    color: #bac2de;
}
QPushButton#ModeButton:checked {
    background-color: #45475a;
    color: white;
}

/* Checkbox Stili */
QCheckBox {
    color: #bac2de;
    spacing: 10px;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #45475a;
    border-radius: 4px;
    background: transparent;
}

QCheckBox::indicator:checked {
    background-color: #a6e3a1; /* Yeşil tik arka planı */
    border-color: #a6e3a1;
}

/* İsteğe bağlı: Tik işareti görseli kullanmadan renk değişimi yeterli olabilir 
   veya basit bir stil ile devam edebiliriz. */

/* mfdp_app/ui/styles.py içine eklenebilir */
QCheckBox#DNDCheckbox::indicator:checked {
    background-color: #f38ba8; /* Pastel Kırmızı (Uyarı rengi) */
    border-color: #f38ba8;
}

/* Gün Paneli (timer altındaki açılır özet) */
QFrame#DayPanel {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
}
QPushButton#DayPanelHeader {
    background-color: transparent;
    border: none;
    padding: 6px 8px;
    text-align: left;
    color: #cdd6f4;
    font-size: 13px;
}
QPushButton#DayPanelHeader:hover {
    color: #f9e2af;
}
QPushButton#DayNavButton {
    background-color: transparent;
    border: none;
    padding: 4px 6px;
    color: #a6adc8;
    font-size: 12px;
}
QPushButton#DayNavButton:hover {
    color: #cdd6f4;
    background-color: #313244;
}
QPushButton#DayNavButton:disabled {
    color: #45475a;
}
QScrollArea#DayPanelScroll, QWidget#DayPanelBody {
    background: transparent;
    border: none;
}
QFrame#DayBlockRow {
    border-radius: 5px;
}
QFrame#DayBlockRow:hover {
    background-color: #313244;
}
QLabel#DayTagLabel {
    font-size: 11px;
    font-weight: bold;
    color: #a6adc8;
}
QLabel#DayBlockTime, QLabel#DayEmptyLabel {
    font-size: 12px;
    color: #7f849c;
}
QLabel#DayBlockDuration {
    font-size: 12px;
    font-weight: bold;
    color: #a6e3a1;
}
"""
