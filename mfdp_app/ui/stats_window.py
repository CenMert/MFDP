from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QWidget, QScrollArea, QHBoxLayout)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mfdp_app.db_manager import get_daily_trend_v2, get_hourly_productivity_v2, get_completion_rate_v2, get_focus_quality_stats

class StatsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verimlilik Analizi - MFDP")
        self.resize(700, 800)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;") 
        container = QWidget()
        scroll.setWidget(container)
        
        self.layout = QVBoxLayout(container)
        self.layout.setSpacing(30)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        self.init_header()
        self.init_daily_chart()
        self.init_hourly_chart()
        self.init_quality_section()

    def init_header(self):
        stats = get_completion_rate_v2()
        total = stats['completed'] + stats['interrupted']
        rate = int((stats['completed'] / total * 100)) if total > 0 else 0
        header_text = f"Tamamlama Oranı: %{rate} ({stats['completed']} Tam / {total} Toplam)"
        
        lbl = QLabel(header_text)
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1; padding: 10px; background-color: #313244; border-radius: 8px;")
        lbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(lbl)

    def _create_figure(self):
        fig = Figure(figsize=(6, 4), dpi=100, facecolor='#1e1e2e')
        return fig

    def _setup_ax(self, ax, title, xlabel, ylabel):
        ax.set_facecolor('#1e1e2e')
        ax.set_title(title, color='#cdd6f4', fontsize=12, pad=15)
        ax.set_xlabel(xlabel, color='#bac2de')
        ax.set_ylabel(ylabel, color='#bac2de')
        ax.tick_params(axis='x', colors='#bac2de', rotation=45)
        ax.tick_params(axis='y', colors='#bac2de')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#45475a')
        ax.spines['left'].set_color('#45475a')
        ax.grid(color='#45475a', linestyle='--', linewidth=0.5, alpha=0.5)

    def init_daily_chart(self):
        data = get_daily_trend_v2(7)
        days = [x[0] for x in data]
        minutes = [x[1] for x in data]

        fig = self._create_figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        bars = ax.bar(days, minutes, color='#89b4fa', width=0.6, alpha=0.8)
        self._setup_ax(ax, "Son 7 Günlük Trend", "Günler", "Dakika")

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
                        ha='center', va='bottom', color='#cdd6f4', fontsize=8)
        fig.tight_layout()
        self.layout.addWidget(canvas)

    def init_hourly_chart(self):
        hours_data = get_hourly_productivity_v2()
        hours = list(range(24))
        
        fig = self._create_figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.fill_between(hours, hours_data, color='#a6e3a1', alpha=0.2)
        ax.plot(hours, hours_data, color='#a6e3a1', linewidth=2, marker='o', markersize=4)
        self._setup_ax(ax, "Saatlik Verimlilik", "Saat (00-23)", "Toplam Dakika")
        ax.set_xticks(range(0, 24, 3))
        fig.tight_layout()
        self.layout.addWidget(canvas)
    
    def init_quality_section(self):
        # Yatay düzen: Solda Grafik, Sağda Sözel Özet
        container = QWidget()
        layout = QHBoxLayout(container)

        # 1. Pasta Grafik (Pie Chart)
        stats = get_focus_quality_stats()
        labels = list(stats.keys())
        sizes = list(stats.values())

        # Eğer hiç veri yoksa boş gösterme
        if sum(sizes) > 0:
            fig = self._create_figure()
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            # Renkler: Yeşil (Deep), Sarı (Moderate), Kırmızı (Distracted)
            colors = ['#a6e3a1', '#f9e2af', '#f38ba8']

            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                            startangle=90, colors=colors,
                                            textprops=dict(color="#cdd6f4"))

            ax.set_title("Odaklanma Kalitesi", color='#cdd6f4', fontsize=12)

            # Pasta grafik arka planı şeffaf olsun
            fig.patch.set_facecolor('#1e1e2e')

            fig.tight_layout()
            layout.addWidget(canvas, stretch=2) # Grafik 2 birim yer kaplasın

            # 2. Sözel Analiz (Insight)
            insight_text = self._generate_insight(stats)
            lbl_insight = QLabel(insight_text)
            lbl_insight.setWordWrap(True)
            lbl_insight.setStyleSheet("""
                font-size: 14px; 
                color: #cdd6f4; 
                background-color: #313244; 
                padding: 15px; 
                border-radius: 8px;
                line-height: 1.5;
            """)
            lbl_insight.setAlignment(Qt.AlignTop)
            layout.addWidget(lbl_insight, stretch=1) # Yazı 1 birim yer kaplasın

        self.layout.addWidget(container)

    def _generate_insight(self, stats):
        """Verilere bakarak kullanıcıya özel bir özet metni çıkarır."""
        deep = stats.get('Deep Work (0 Kesinti)', 0)
        moderate = stats.get('Moderate (1-2 Kesinti)', 0)
        distracted = stats.get('Distracted (3+ Kesinti)', 0)
        total = deep + moderate + distracted

        if total == 0: return "Analiz için yeterli veri yok."

        deep_ratio = (deep / total) * 100

        text = "<b>📊 Odaklanma Karnesi</b><br><br>"

        if deep_ratio > 70:
            text += "🚀 <b>Mükemmel Disiplin!</b><br>Oturumlarının büyük çoğunluğu kesintisiz. 'Deep Work' moduna girmekte ustasın.<br><br>"
        elif deep_ratio > 40:
            text += "⚖️ <b>Dengeli Performans.</b><br>Genellikle iyi odaklanıyorsun ama bazen dikkat dağıtıcılar araya giriyor. Küçük molaları kontrol etmeyi deneyebilirsin.<br><br>"
        else:
            text += "⚠️ <b>Dikkat Dağınıklığı Yüksek.</b><br>Çoğu oturumun bölünmüş durumda. Bildirimleri kapatmayı veya ortamını değiştirmeyi dene.<br><br>"

        text += f"• Toplam <b>{total}</b> oturumun <b>{deep}</b> tanesi (%{int(deep_ratio)}) tamamen kesintisizdi.<br>"

        if distracted > 0:
            text += f"• <b>{distracted}</b> oturumda 3'ten fazla kez bölündün. Bu zaman aralıklarını incelemelisin."

        return text