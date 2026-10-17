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
    /* font-size: MainWindow._fit_timer_font() pencere genişliğine göre hesaplar (28-90 px) */
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

/* Pasif butonlar (ör. oturum yokken kesinti butonları) */
QPushButton:disabled {
    color: #585b70;
    background-color: #1e1e2e;
    border-color: #313244;
}

/* Sol yan panel: süreklilik ızgarası + eğer-ise planları */
QFrame#SidePanel {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
}
QLabel#SideTitle {
    font-size: 13px;
    font-weight: bold;
    color: #cdd6f4;
}
QLabel#SideStat {
    font-size: 13px;
    font-weight: bold;
    color: #f9e2af;
}
QLabel#SideMuted {
    font-size: 11px;
    color: #7f849c;
}
QLabel#SidePlanRow {
    font-size: 12px;
    color: #bac2de;
}
QFrame#SideLine {
    color: #313244;
}
QPushButton#SideToggle {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: bold;
}
QPushButton#SideToggle:checked {
    background-color: #a6e3a1;
    color: #1e1e2e;
}

/* Oturum sonu geri bildirim şeridi */
QFrame#FeedbackStrip {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 8px;
}
QLabel#FeedbackLabel {
    font-size: 12px;
    color: #a6adc8;
}
QPushButton#FeedbackChip {
    padding: 4px 8px;
    font-size: 12px;
    border-radius: 5px;
}
QPushButton#FeedbackChip:checked {
    background-color: #f9e2af;
    color: #1e1e2e;
    font-weight: bold;
}
QPushButton#FeedbackClose {
    background: transparent;
    border: none;
    color: #7f849c;
    padding: 2px 6px;
}

/* Menüler (☰ menüsü): koyu zemin, açık yazı */
QMenu {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 22px 6px 14px;
    border-radius: 4px;
    color: #cdd6f4;
}
QMenu::item:selected {
    background-color: #313244;
}
QMenu::item:disabled {
    color: #585b70;
}
QMenu::separator {
    height: 1px;
    background: #45475a;
    margin: 4px 8px;
}

/* Ana içerik kaydırma alanı: içerik pencereye sığmazsa dikey kaydırma (yalnızca güvenlik ağı) */
QScrollArea#MainScroll, QScrollArea#MainScroll > QWidget > QWidget#MainContent {
    background: transparent;
    border: none;
}
QScrollArea#MainScroll QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollArea#MainScroll QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 4px;
    min-height: 24px;
}
QScrollArea#MainScroll QScrollBar::add-line:vertical, QScrollArea#MainScroll QScrollBar::sub-line:vertical {
    height: 0;
}

/* Yan panel: sıkı buton dolgusu, geri butonu, şeffaf kaydırma alanı */
QFrame#SidePanel QPushButton {
    padding: 6px 10px;
}
QPushButton#SideBack {
    padding: 2px 10px;
    font-size: 16px;
}
QScrollArea#SideScroll, QWidget#SideBody {
    background: transparent;
    border: none;
}

/* Duyarlı yoğunluk basamakları: MainWindow._apply_density içerik genişliğine göre
   MainContent'in "density" özelliğini wide / medium / narrow yapar. wide = varsayılan görünüm. */
QWidget#MainContent[density="medium"] QPushButton {
    padding: 6px 12px;
}
QWidget#MainContent[density="medium"] QLabel#StatusLabel {
    font-size: 22px;
}
QWidget#MainContent[density="medium"] QLabel#TimerLabel {
    margin: 6px 0;
}
QWidget#MainContent[density="narrow"] QPushButton {
    padding: 4px 6px;
}
QWidget#MainContent[density="narrow"] QLabel#StatusLabel {
    font-size: 15px;
}
QWidget#MainContent[density="narrow"] QLabel#TimerLabel {
    margin: 0;
}
QWidget#MainContent[density="narrow"] QCheckBox {
    font-size: 12px;
}
"""
