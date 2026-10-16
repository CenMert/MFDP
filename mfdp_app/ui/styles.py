# mfdp_app/ui/styles.py

MODERN_DARK_THEME = """
/* Toprak tonları paleti — eşleme için bkz. mfdp_app/ui/palette.py */
/* Genel Pencere Ayarları */
QMainWindow {
    background-color: #24201b; /* Koyu Lacivert/Gri (Modern IDE teması gibi) */
}

QWidget {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 14px;
    color: #f1dca7; /* Yumuşak Beyaz */
}

/* Etiketler (Labels) */
QLabel {
    color: #f1dca7;
}

/* Zamanlayıcıya özel stil (ID ile yakalayacağız) */
QLabel#TimerLabel {
    font-size: 90px;
    font-weight: bold;
    color: #9b9b7a; /* Pastel Yeşil */
    margin: 20px 0;
}

/* Durum Etiketi (Focus/Break) */
QLabel#StatusLabel {
    font-size: 28px;
    font-weight: 600;
    color: #ffcb69; /* Pastel Sarı */
}

/* Butonlar */
QPushButton {
    background-color: #35302a;
    border: 2px solid #4a4238;
    border-radius: 8px; /* Yuvarlatılmış köşeler */
    color: #f1dca7;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4a4238; /* Üzerine gelince biraz açıl */
    border-color: #5e5448;
}

QPushButton:pressed {
    background-color: #24201b; /* Tıklayınca gömül */
    border-color: #9b9b7a;
}

/* Başlat Butonu için özel renk */
QPushButton#StartButton {
    background-color: #9b9b7a;
    color: #24201b; /* Yazı rengi koyu olsun */
    border: none;
}
QPushButton#StartButton:hover {
    background-color: #baa587;
}

/* Mod Butonları (Focus, Short, Long) */
QPushButton#ModeButton {
    background-color: transparent;
    border: 1px solid #4a4238;
    color: #d2c2a8;
}
QPushButton#ModeButton:checked {
    background-color: #4a4238;
    color: white;
}

/* Checkbox Stili */
QCheckBox {
    color: #d2c2a8;
    spacing: 10px;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #4a4238;
    border-radius: 4px;
    background: transparent;
}

QCheckBox::indicator:checked {
    background-color: #9b9b7a; /* Yeşil tik arka planı */
    border-color: #9b9b7a;
}

/* İsteğe bağlı: Tik işareti görseli kullanmadan renk değişimi yeterli olabilir 
   veya basit bir stil ile devam edebiliriz. */

/* mfdp_app/ui/styles.py içine eklenebilir */

/* Gün Paneli (timer altındaki açılır özet) */
QFrame#DayPanel {
    background-color: #1c1915;
    border: 1px solid #35302a;
    border-radius: 8px;
}
QPushButton#DayPanelHeader {
    background-color: transparent;
    border: none;
    padding: 6px 8px;
    text-align: left;
    color: #f1dca7;
    font-size: 13px;
}
QPushButton#DayPanelHeader:hover {
    color: #ffcb69;
}
QPushButton#DayNavButton {
    background-color: transparent;
    border: none;
    padding: 4px 6px;
    color: #b8a99a;
    font-size: 12px;
}
QPushButton#DayNavButton:hover {
    color: #f1dca7;
    background-color: #35302a;
}
QPushButton#DayNavButton:disabled {
    color: #4a4238;
}
QScrollArea#DayPanelScroll, QWidget#DayPanelBody {
    background: transparent;
    border: none;
}
QFrame#DayBlockRow {
    border-radius: 5px;
}
QFrame#DayBlockRow:hover {
    background-color: #35302a;
}
QLabel#DayTagLabel {
    font-size: 11px;
    font-weight: bold;
    color: #b8a99a;
}
QLabel#DayBlockTime, QLabel#DayEmptyLabel {
    font-size: 12px;
    color: #8f8273;
}
QLabel#DayBlockDuration {
    font-size: 12px;
    font-weight: bold;
    color: #9b9b7a;
}

/* Pasif butonlar (ör. oturum yokken kesinti butonları) */
QPushButton:disabled {
    color: #5e5448;
    background-color: #24201b;
    border-color: #35302a;
}

/* Sol yan panel: süreklilik ızgarası + eğer-ise planları */
QFrame#SidePanel {
    background-color: #1c1915;
    border: 1px solid #35302a;
    border-radius: 8px;
}
QLabel#SideTitle {
    font-size: 13px;
    font-weight: bold;
    color: #f1dca7;
}
QLabel#SideStat {
    font-size: 13px;
    font-weight: bold;
    color: #ffcb69;
}
QLabel#SideMuted {
    font-size: 11px;
    color: #8f8273;
}
QLabel#SidePlanRow {
    font-size: 12px;
    color: #d2c2a8;
}
QFrame#SideLine {
    color: #35302a;
}
QPushButton#SideToggle {
    background-color: #35302a;
    border: 1px solid #4a4238;
    border-radius: 5px;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: bold;
}
QPushButton#SideToggle:checked {
    background-color: #9b9b7a;
    color: #24201b;
}

/* Oturum sonu geri bildirim şeridi */
QFrame#FeedbackStrip {
    background-color: #1c1915;
    border: 1px solid #4a4238;
    border-radius: 8px;
}
QLabel#FeedbackLabel {
    font-size: 12px;
    color: #b8a99a;
}
QPushButton#FeedbackChip {
    padding: 4px 8px;
    font-size: 12px;
    border-radius: 5px;
}
QPushButton#FeedbackChip:checked {
    background-color: #ffcb69;
    color: #24201b;
    font-weight: bold;
}
QPushButton#FeedbackClose {
    background: transparent;
    border: none;
    color: #8f8273;
    padding: 2px 6px;
}
"""
