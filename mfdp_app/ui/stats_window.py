from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QWidget, 
                               QScrollArea, QHBoxLayout, QComboBox, QTabWidget)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mfdp_app.db.session_repository import SessionRepository
from mfdp_app.db.tag_repository import TagRepository
from mfdp_app.db.atomic_event_repository import AtomicEventRepository
import numpy as np


class StatsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verimlilik Analizi - MFDP")
        self.resize(700, 800)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")
        
        # Non-modal yap - arka plandaki pencereyi kullanılabilir tut
        self.setModal(False)
        # Kapanınca belleği otomatik serbest bırak
        self.setAttribute(Qt.WA_DeleteOnClose)

        # State for atomic heatmap (set before rendering)
        self.atomic_filter_options = [
            ("Tüm Olaylar", None),
            ("Kesintiler", ["interruption_detected"]),
            ("Fokus Değişimleri", ["focus_shift_detected"]),
            ("Dikkat Dağıtıcılar", ["distraction_identified"]),
            ("Milestones", ["milestone_reached"]),
            ("DND / Çevre", ["dnd_toggled", "environment_changed"]),
        ]
        self.atomic_heatmap_canvas = None
        self.atomic_no_data_label = None

        # Track active figures/canvases for cleanup
        self._active_figures = []

        main_layout = QVBoxLayout(self)

        # Header (lightweight, always visible)
        self.init_header(main_layout)

        # Tab widget for lazy chart loading
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #45475a; background-color: #1e1e2e; }
            QTabBar::tab { background: #313244; color: #bac2de; padding: 8px 16px; 
                           border: 1px solid #45475a; border-bottom: none; border-radius: 4px 4px 0 0; margin-right: 2px; }
            QTabBar::tab:selected { background: #45475a; color: #cdd6f4; font-weight: bold; }
            QTabBar::tab:hover { background: #585b70; }
        """)
        main_layout.addWidget(self.tabs)

        # Tab definitions: (title, builder_method)
        self._tab_builders = [
            ("Günlük Trend", self._build_daily_chart),
            ("Tag Bazlı", self._build_daily_chart_by_tag),
            ("Tag Dağılımı", self._build_tag_distribution),
            ("Saatlik", self._build_hourly_chart),
            ("Atomic Harita", self._build_atomic_heatmap_section),
            ("Kalite", self._build_quality_section),
        ]
        self._tab_loaded = {}

        for title, _ in self._tab_builders:
            placeholder = QWidget()
            placeholder.setLayout(QVBoxLayout())
            self.tabs.addTab(placeholder, title)
            self._tab_loaded[title] = False

        # Connect tab change -> lazy load
        self.tabs.currentChanged.connect(self._on_tab_changed)
        # Load the first tab
        self._on_tab_changed(0)

    def init_header(self, parent_layout):
        stats = SessionRepository.get_completion_rate()
        total = stats['completed'] + stats['interrupted']
        rate = int((stats['completed'] / total * 100)) if total > 0 else 0
        header_text = f"Tamamlama Oranı: %{rate} ({stats['completed']} Tam / {total} Toplam)"
        
        lbl = QLabel(header_text)
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1; padding: 10px; background-color: #313244; border-radius: 8px;")
        lbl.setAlignment(Qt.AlignCenter)
        parent_layout.addWidget(lbl)

    # =========================================================================
    # LAZY TAB LOADING
    # =========================================================================

    def _on_tab_changed(self, index):
        """Load chart content only when the tab is first selected."""
        if index < 0 or index >= len(self._tab_builders):
            return
        title, builder = self._tab_builders[index]
        if self._tab_loaded.get(title):
            return
        
        widget = self.tabs.widget(index)
        layout = widget.layout()
        
        # Build the chart into this tab's layout
        builder(layout)
        self._tab_loaded[title] = True

    # =========================================================================
    # CHART HELPERS
    # =========================================================================

    def _create_figure(self, figsize=(6, 4)):
        fig = Figure(figsize=figsize, dpi=100, facecolor='#1e1e2e')
        self._active_figures.append(fig)
        return fig

    def _add_canvas(self, layout, fig):
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        return canvas

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

    # =========================================================================
    # CHART BUILDERS (called lazily per-tab)
    # =========================================================================

    def _build_daily_chart(self, layout):
        data = SessionRepository.get_daily_trend(days=7)
        days = [x[0] for x in data]
        minutes = [x[1] for x in data]

        fig = self._create_figure()
        ax = fig.add_subplot(111)
        bars = ax.bar(days, minutes, color='#89b4fa', width=0.6, alpha=0.8)
        self._setup_ax(ax, "Son 7 Günlük Trend (Toplam)", "Günler", "Dakika")

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
                        ha='center', va='bottom', color='#cdd6f4', fontsize=8)
        fig.tight_layout()
        self._add_canvas(layout, fig)
    
    def _build_daily_chart_by_tag(self, layout):
        """Tag bazlı günlük trend grafiği (grouped bar chart)."""
        tags = TagRepository.get_all_tags()
        if not tags:
            layout.addWidget(QLabel("Tag verisi bulunamadı."))
            return
        
        # Her tag için veri al
        tag_data = {}
        days_set = set()
        for tag_info in tags:
            tag = tag_info['name']
            data = TagRepository.get_daily_trend_by_tag(tag, days=7)
            tag_data[tag] = {day: minutes for day, minutes in data}
            days_set.update([day for day, _ in data])
        
        if not days_set:
            layout.addWidget(QLabel("Görüntülenecek veri yok."))
            return
        
        days = sorted(list(days_set))
        if not days:
            return
        
        fig = self._create_figure()
        ax = fig.add_subplot(111)
        
        # Tag renklerini al
        tag_colors = {}
        default_colors = ['#89b4fa', '#a6e3a1', '#f9e2af', '#f38ba8', '#cba6f7', '#fab387', '#94e2d5', '#f5c2e7']
        for i, tag_info in enumerate(tags):
            tag = tag_info['name']
            tag_colors[tag] = tag_info.get('color') or default_colors[i % len(default_colors)]
        
        x = np.arange(len(days))
        width = 0.8 / len(tags)
        
        for i, tag in enumerate(tags):
            tag_name = tag['name']
            minutes = [tag_data[tag_name].get(day, 0) for day in days]
            offset = (i - len(tags) / 2 + 0.5) * width
            bars = ax.bar(x + offset, minutes, width, label=tag_name, 
                         color=tag_colors[tag_name], alpha=0.8)
            
            for j, (bar, val) in enumerate(zip(bars, minutes)):
                if val > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., val, f'{int(val)}',
                           ha='center', va='bottom', color='#cdd6f4', fontsize=7)
        
        ax.set_xlabel("Günler", color='#bac2de')
        ax.set_ylabel("Dakika", color='#bac2de')
        ax.set_title("Son 7 Günlük Trend (Tag Bazlı)", color='#cdd6f4', fontsize=12, pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(days, rotation=45, color='#bac2de')
        ax.tick_params(axis='y', colors='#bac2de')
        ax.legend(loc='upper left', facecolor='#313244', edgecolor='#45475a', labelcolor='#cdd6f4')
        ax.set_facecolor('#1e1e2e')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#45475a')
        ax.spines['left'].set_color('#45475a')
        ax.grid(color='#45475a', linestyle='--', linewidth=0.5, alpha=0.5, axis='y')
        
        fig.tight_layout()
        self._add_canvas(layout, fig)
    
    def _build_tag_distribution(self, layout):
        """Tag bazlı zaman dağılımı pasta grafiği."""
        tags = TagRepository.get_all_tags()
        if not tags:
            layout.addWidget(QLabel("Tag verisi bulunamadı."))
            return
        
        tag_times = {}
        for tag_info in tags:
            tag = tag_info['name']
            total_minutes = TagRepository.get_tag_time_summary(tag)
            if total_minutes > 0:
                tag_times[tag] = {
                    'minutes': total_minutes,
                    'color': tag_info.get('color') or '#89b4fa'
                }
        
        if not tag_times:
            layout.addWidget(QLabel("Görüntülenecek veri yok."))
            return
        
        labels = list(tag_times.keys())
        sizes = [tag_times[tag]['minutes'] for tag in labels]
        colors = [tag_times[tag]['color'] for tag in labels]
        
        fig = self._create_figure()
        ax = fig.add_subplot(111)
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%',
               startangle=90, colors=colors,
               textprops=dict(color="#cdd6f4"))
        
        ax.set_title("Tag Bazlı Zaman Dağılımı", color='#cdd6f4', fontsize=12)
        fig.patch.set_facecolor('#1e1e2e')
        
        fig.tight_layout()
        self._add_canvas(layout, fig)

    def _build_hourly_chart(self, layout):
        hours_data = SessionRepository.get_hourly_productivity()
        hours = list(range(24))
        
        fig = self._create_figure()
        ax = fig.add_subplot(111)
        ax.fill_between(hours, hours_data, color='#a6e3a1', alpha=0.2)
        ax.plot(hours, hours_data, color='#a6e3a1', linewidth=2, marker='o', markersize=4)
        self._setup_ax(ax, "Saatlik Verimlilik", "Saat (00-23)", "Toplam Dakika")
        ax.set_xticks(range(0, 24, 3))
        fig.tight_layout()
        self._add_canvas(layout, fig)

    def _build_atomic_heatmap_section(self, layout):
        lbl = QLabel("Atomic Olay Isı Haritası (Son 14 Gün)")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #cdd6f4;")
        layout.addWidget(lbl)

        # Filter dropdown
        self.atomic_filter = QComboBox()
        self.atomic_filter.setStyleSheet("background-color: #313244; color: #cdd6f4; padding: 6px;")
        for label, _ in self.atomic_filter_options:
            self.atomic_filter.addItem(label)
        self.atomic_filter.currentIndexChanged.connect(self._render_atomic_heatmap)
        layout.addWidget(self.atomic_filter)

        # Store the layout ref for dynamic canvas insertion
        self.atomic_heatmap_layout = layout
        self._render_atomic_heatmap()

    def _render_atomic_heatmap(self):
        # Clean previous widgets
        if self.atomic_heatmap_canvas:
            self._active_figures = [f for f in self._active_figures 
                                     if f is not self.atomic_heatmap_canvas.figure]
            plt.close(self.atomic_heatmap_canvas.figure)
            self.atomic_heatmap_canvas.setParent(None)
            self.atomic_heatmap_canvas.deleteLater()
            self.atomic_heatmap_canvas = None
        if self.atomic_no_data_label:
            self.atomic_no_data_label.setParent(None)
            self.atomic_no_data_label.deleteLater()
            self.atomic_no_data_label = None

        idx = self.atomic_filter.currentIndex() if hasattr(self, 'atomic_filter') else 0
        _, event_types = self.atomic_filter_options[idx]

        day_labels, matrix = AtomicEventRepository.get_heatmap(days=14, event_types=event_types)

        # No data case
        if not matrix or not day_labels:
            self.atomic_no_data_label = QLabel("Görüntülenecek veri yok.")
            self.atomic_no_data_label.setStyleSheet("color: #bac2de; padding: 8px;")
            self.atomic_heatmap_layout.addWidget(self.atomic_no_data_label)
            return

        data = np.array(matrix)

        # Create figure with TWO subplots: heatmap + bar chart
        fig = self._create_figure(figsize=(14, 6))
        
        # Left: Heatmap
        ax1 = fig.add_subplot(121)
        im = ax1.imshow(data, aspect='auto', cmap='YlOrRd', origin='upper', interpolation='nearest')

        ax1.set_yticks(range(len(day_labels)))
        ax1.set_yticklabels(day_labels, color='#bac2de', fontsize=9)
        ax1.set_xticks(range(0, 24, 2))
        ax1.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)], color='#bac2de', fontsize=8, rotation=45)
        ax1.set_xlabel("Saat", color='#bac2de', fontsize=10)
        ax1.set_ylabel("Gün", color='#bac2de', fontsize=10)
        ax1.set_title("Saatlik Olay Dağılımı", color='#cdd6f4', fontsize=12, pad=12, fontweight='bold')
        ax1.tick_params(axis='both', colors='#bac2de')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_color('#45475a')
        ax1.spines['left'].set_color('#45475a')

        cbar = fig.colorbar(im, ax=ax1, shrink=0.8)
        cbar.ax.yaxis.set_tick_params(color='#bac2de')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#bac2de')
        cbar.set_label("Olay Sayısı", color='#bac2de')

        # Right: Hourly Summary (Bar chart)
        ax2 = fig.add_subplot(122)
        hourly_totals = np.sum(data, axis=0)
        hours = np.arange(24)
        
        bars = ax2.bar(hours, hourly_totals, color='#f38ba8', alpha=0.7, edgecolor='#f5c2e7', linewidth=1.5)
        
        # Highlight top 3 hours
        top_3_indices = np.argsort(hourly_totals)[-3:]
        for i in top_3_indices:
            bars[i].set_color('#f9e2af')
            bars[i].set_edgecolor('#f9e2af')
        
        ax2.set_xlabel("Saat", color='#bac2de', fontsize=10)
        ax2.set_ylabel("Toplam Olay", color='#bac2de', fontsize=10)
        ax2.set_title("Saat Bazlı Toplam Olay", color='#cdd6f4', fontsize=12, pad=12, fontweight='bold')
        ax2.set_xticks(range(0, 24, 3))
        ax2.set_xticklabels([f"{h:02d}" for h in range(0, 24, 3)], color='#bac2de', fontsize=9)
        ax2.tick_params(axis='y', colors='#bac2de')
        ax2.set_facecolor('#1e1e2e')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_color('#45475a')
        ax2.spines['left'].set_color('#45475a')
        ax2.grid(color='#45475a', linestyle='--', linewidth=0.5, alpha=0.5, axis='y')

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', color='#cdd6f4', fontsize=7)

        fig.tight_layout()
        self.atomic_heatmap_canvas = FigureCanvas(fig)
        self.atomic_heatmap_layout.addWidget(self.atomic_heatmap_canvas)
    
    def _build_quality_section(self, layout):
        # Yatay düzen: Solda Grafik, Sağda Sözel Özet
        container = QWidget()
        hlayout = QHBoxLayout(container)

        # 1. Pasta Grafik (Pie Chart)
        stats = SessionRepository.get_focus_quality_stats()
        labels = list(stats.keys())
        sizes = list(stats.values())

        # Eğer hiç veri yoksa boş gösterme
        if sum(sizes) > 0:
            fig = self._create_figure()
            ax = fig.add_subplot(111)

            # Renkler: Yeşil (Deep), Sarı (Moderate), Kırmızı (Distracted)
            colors = ["#175611", "#7e5f1c", "#821628"]

            ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                   startangle=90, colors=colors,
                   textprops=dict(color="#C3CDEF"))

            ax.set_title("Odaklanma Kalitesi", color='#cdd6f4', fontsize=12)
            fig.patch.set_facecolor('#1e1e2e')
            fig.tight_layout()
            hlayout.addWidget(FigureCanvas(fig), stretch=2)

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
            hlayout.addWidget(lbl_insight, stretch=1)
        else:
            hlayout.addWidget(QLabel("Analiz için yeterli veri yok."))

        layout.addWidget(container)

    def _generate_insight(self, stats):
        """Verilere bakarak kullanıcıya özel bir özet metni çıkarır."""
        deep = stats.get('Deep Work (0 Kesinti)', 0)
        moderate = stats.get('Moderate (1-2 Kesinti)', 0)
        distracted = stats.get('Distracted (3+ Kesinti)', 0)
        total = deep + moderate + distracted

        if total == 0: return "Analiz için yeterli veri yok."

        deep_ratio = (deep / total) * 100
        moderate_ratio = (moderate / total) * 100
        distracted_ratio = (distracted / total) * 100

        text = "<b>📊 Odaklanma Karnesi</b><br><br>"

        if deep_ratio > 70:
            text += "🚀 <b>Mükemmel Disiplin!</b><br>Oturumlarının büyük çoğunluğu kesintisiz. 'Deep Work' moduna girmekte ustasın.<br><br>"
        elif deep_ratio > 40:
            text += "⚖️ <b>Dengeli Performans.</b><br>Genellikle iyi odaklanıyorsun ama bazen dikkat dağıtıcılar araya giriyor. Küçük molaları kontrol etmeyi deneyebilirsin.<br><br>"
        else:
            text += "⚠️ <b>Dikkat Dağınıklığı Yüksek.</b><br>Çoğu oturumun bölünmüş durumda. Bildirimleri kapatmayı veya ortamını değiştirmeyi dene.<br><br>"

        text += f"• Toplam <b>{total}</b> oturumun <b>{deep}</b> tanesi (%{int(deep_ratio)}) tamamen kesintisizdi.<br>"
        if moderate > 0:
            text += f"• <b>{moderate}</b> oturum (%{int(moderate_ratio)}) orta düzeyde kesinti yaşadı (1-2 kez).<br>"
        if distracted > 0:
            text += f"• <b>{distracted}</b> oturum (%{int(distracted_ratio)}) yüksek kesinti yaşadı (3+ kez). Bu zaman aralıklarını incelemelisin."

        return text

    # =========================================================================
    # CLEANUP
    # =========================================================================

    def closeEvent(self, event):
        """Pencere kapanırken tüm matplotlib figürlerini temizle."""
        for fig in self._active_figures:
            try:
                plt.close(fig)
            except Exception:
                pass
        self._active_figures.clear()
        event.accept()