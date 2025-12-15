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
"""