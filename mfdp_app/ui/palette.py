# mfdp_app/ui/palette.py
"""Toprak tonları paleti (Catppuccin Mocha'nın yerine).

Kaynak palet (10 renk):
    Dusty Olive   #797D62   Palm Leaf      #9B9B7A
    Khaki Beige   #BAA587   Desert Sand    #D9AE94
    Soft Peach    #F1DCA7   Golden Pollen  #FFCB69
    Sunlit Clay   #E8AC65   Toasted Almond #D08C60
    Faded Copper  #B58463   Dusty Taupe    #997B66

Arka plan / yüzey tonları paletteki kahverengilerin koyulaştırılmış
halleridir (koyu tema korunur). Aşağıdaki CATPPUCCIN_TO_EARTHY tablosu
kod tabanındaki eski hex değerlerinin hangi yeni renge taşındığını
gösterir — bir rolün rengini değiştirmek için ilgili hex'i projede
bul/değiştir yapmak yeterli.
"""

# --- Kaynak palet ---
DUSTY_OLIVE = "#797d62"
PALM_LEAF = "#9b9b7a"
KHAKI_BEIGE = "#baa587"
DESERT_SAND = "#d9ae94"
SOFT_PEACH = "#f1dca7"
GOLDEN_POLLEN = "#ffcb69"
SUNLIT_CLAY = "#e8ac65"
TOASTED_ALMOND = "#d08c60"
FADED_COPPER = "#b58463"
DUSTY_TAUPE = "#997b66"

# --- Türetilmiş koyu yüzeyler ---
BG_DEEP = "#1c1915"      # panel içleri, grafik zeminleri
BG = "#24201b"           # pencere arka planı
SURFACE_0 = "#35302a"    # buton, hover
SURFACE_1 = "#4a4238"    # kenarlıklar, seçili öğe
SURFACE_2 = "#5e5448"    # hover kenarlık
OVERLAY_0 = "#7a6e60"    # tamamlanmış/pasif öğeler
OVERLAY_1 = "#8f8273"    # ikincil saat/metin
SUBTEXT_0 = "#b8a99a"
SUBTEXT_1 = "#d2c2a8"
TEXT = SOFT_PEACH

# Eski (Catppuccin) -> yeni rol eşlemesi
CATPPUCCIN_TO_EARTHY = {
    # yüzeyler / metin
    "#181825": BG_DEEP,
    "#1e1e2e": BG,
    "#313244": SURFACE_0,
    "#45475a": SURFACE_1,
    "#585b70": SURFACE_2,
    "#6c7086": OVERLAY_0,
    "#7f849c": OVERLAY_1,
    "#a6adc8": SUBTEXT_0,
    "#bac2de": SUBTEXT_1,
    "#c3cdef": SUBTEXT_1,
    "#cdd6f4": TEXT,
    "#ffffff": TEXT,
    # vurgular
    "#a6e3a1": PALM_LEAF,        # yeşil: başlat, süre, tamamlandı
    "#94e2d5": DUSTY_OLIVE,      # turkuaz
    "#94d990": KHAKI_BEIGE,      # birincil buton hover
    "#89b4fa": SUNLIT_CLAY,      # mavi: ana vurgu, varsayılan etiket
    "#f9e2af": GOLDEN_POLLEN,    # sarı: durum, başlık hover
    "#f38ba8": TOASTED_ALMOND,   # kırmızı: hata/sil
    "#fab387": DESERT_SAND,      # turuncu
    "#cba6f7": DUSTY_TAUPE,      # mor
    "#f5c2e7": FADED_COPPER,     # pembe
    # istatistik pastası (Deep / Moderate / Distracted)
    "#175611": "#5f6349",
    "#7e5f1c": "#a67a3e",
    "#821628": "#8f4f36",
}

# Yeni etiketlere sırayla atanan renkler
TAG_COLORS = [
    SUNLIT_CLAY, PALM_LEAF, GOLDEN_POLLEN, TOASTED_ALMOND,
    DUSTY_TAUPE, DESERT_SAND, DUSTY_OLIVE, FADED_COPPER,
]
