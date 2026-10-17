"""
SidePanel - Ana pencerenin solunda açılıp kapanan panel.

Üstte GitHub tarzı süreklilik ızgarası ve seri özeti, altta bugünün eğer-ise planları.
"""

import datetime

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QWidget, QScrollArea)
from PySide6.QtCore import Qt, Signal

from mfdp_app.core import review_scheduler
from mfdp_app.db.review_repository import ReviewRepository

from mfdp_app.core.streak import build_streak_data, ACTIVE_MINUTES, GRID_WEEKS
from mfdp_app.core.daily_report import logical_day, format_duration
from mfdp_app.core.plan_scheduler import PlanScheduler
from mfdp_app.db.plan_repository import PlanRepository
from mfdp_app.ui.streak_widget import StreakGrid, LEVEL_COLORS
from mfdp_app.ui.widgets import ElidedButton

_TR_DAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


def plan_sentence(plan: dict, with_days: bool = True) -> str:
    """'EĞER Pzt, Çar 10:00 · kahvaltıdan sonra → SSP: soru çöz'"""
    cond = []
    if with_days:
        days = plan['weekdays']
        cond.append("Her gün" if len(days) == 7 else ", ".join(_TR_DAYS[d] for d in days))
    if plan.get('time'):
        cond.append(plan['time'])
    if plan.get('cue'):
        cond.append(plan['cue'])
    then = [x for x in (plan.get('task_name'), plan.get('action')) if x]
    return f"EĞER {' · '.join(cond)}  →  {': '.join(then) or 'çalışmaya başla'}"


class ClickLabel(QLabel):
    """Tıklanabilir, satır kaydıran etiket."""
    clicked = Signal()

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setWordWrap(True)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class SidePanel(QFrame):
    edit_plans_requested = Signal()
    review_start_requested = Signal(int)
    lecture_requested = Signal()
    tracking_requested = Signal()

    back_requested = Signal()

    # Genişlik sabit değil: MainWindow pencereye göre MIN_WIDTH..MAX_WIDTH arasında verir
    # (dar pencerede tüm alanı kaplar, ← ile kapatılır).
    MIN_WIDTH = 240
    MAX_WIDTH = 330

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidePanel")
        self.setMinimumWidth(1)

        frame = QVBoxLayout(self)
        frame.setContentsMargins(10, 10, 4, 10)
        frame.setSpacing(6)

        # Başlık satırı: dar pencerede (panel tüm alanı kaplarken) geri butonu görünür
        header = QHBoxLayout()
        header.setSpacing(6)
        self.btn_back = QPushButton("←")
        self.btn_back.setObjectName("SideBack")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setToolTip("Sayaca dön (Esc / Ctrl+B)")
        self.btn_back.clicked.connect(self.back_requested.emit)
        self.btn_back.hide()
        header.addWidget(self.btn_back)
        title = QLabel("Süreklilik")
        title.setObjectName("SideTitle")
        header.addWidget(title, 1)
        frame.addLayout(header)

        # Gövde kaydırılabilir: kısa pencerede dikeyde taşmaz
        scroll = QScrollArea()
        scroll.setObjectName("SideScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        body = QWidget()
        body.setObjectName("SideBody")
        scroll.setWidget(body)
        frame.addWidget(scroll, 1)

        root = QVBoxLayout(body)
        root.setContentsMargins(0, 0, 8, 0)
        root.setSpacing(8)

        self.grid = StreakGrid()
        root.addWidget(self.grid)

        legend = QHBoxLayout()
        legend.setSpacing(3)
        legend.addStretch()
        less = QLabel("az")
        less.setObjectName("SideMuted")
        legend.addWidget(less)
        for color in LEVEL_COLORS:
            sw = QLabel()
            sw.setFixedSize(10, 10)
            sw.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
            legend.addWidget(sw)
        more = QLabel("çok")
        more.setObjectName("SideMuted")
        legend.addWidget(more)
        root.addLayout(legend)

        self.lbl_streak = QLabel()
        self.lbl_streak.setObjectName("SideStat")
        self.lbl_streak.setWordWrap(True)
        self.lbl_streak.setToolTip(
            f"Bir gün ≥{ACTIVE_MINUTES} dk çalışıldıysa aktif sayılır.\n"
            "Tek boş gün seriyi bozmaz; iki gün üst üste boşluk bozar.")
        root.addWidget(self.lbl_streak)
        self.lbl_week = QLabel()
        self.lbl_week.setObjectName("SideMuted")
        self.lbl_week.setWordWrap(True)
        root.addWidget(self.lbl_week)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("SideLine")
        root.addWidget(line)

        reviews_title = QLabel("Bugünün tekrarları")
        reviews_title.setObjectName("SideTitle")
        root.addWidget(reviews_title)

        self.reviews_box = QWidget()
        self.reviews_layout = QVBoxLayout(self.reviews_box)
        self.reviews_layout.setContentsMargins(0, 0, 0, 0)
        self.reviews_layout.setSpacing(4)
        root.addWidget(self.reviews_box)

        btn_lecture = ElidedButton("+ Derste işlenen")
        btn_lecture.setCursor(Qt.PointingHandCursor)
        btn_lecture.setToolTip("Derste ne işlendiğini kaydet; tekrar takvimi o günden başlar")
        btn_lecture.clicked.connect(self.lecture_requested.emit)
        btn_tracking = ElidedButton("Hangi dersler takipte?")
        btn_tracking.setCursor(Qt.PointingHandCursor)
        btn_tracking.setToolTip("Tekrar hatırlatması istediğin dersleri seç; diğer işler hatırlatma üretmez")
        btn_tracking.clicked.connect(self.tracking_requested.emit)
        root.addWidget(btn_lecture)
        root.addWidget(btn_tracking)

        self.lbl_review_stats = QLabel()
        self.lbl_review_stats.setObjectName("SideMuted")
        self.lbl_review_stats.setWordWrap(True)
        self.lbl_review_stats.setToolTip(
            "Geri bildirim: son 14 günde kaç iş oturumuna tür etiketi girdin.\n"
            "Bu oran düşerse sistem fazla yük oluyor demektir; sadeleştirilmeli.")
        root.addWidget(self.lbl_review_stats)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setObjectName("SideLine")
        root.addWidget(line2)

        plans_title = QLabel("Bugünün planları")
        plans_title.setObjectName("SideTitle")
        root.addWidget(plans_title)

        self.plans_box = QWidget()
        self.plans_layout = QVBoxLayout(self.plans_box)
        self.plans_layout.setContentsMargins(0, 0, 0, 0)
        self.plans_layout.setSpacing(4)
        root.addWidget(self.plans_box)

        self.lbl_adherence = QLabel()
        self.lbl_adherence.setObjectName("SideMuted")
        self.lbl_adherence.setWordWrap(True)
        self.lbl_adherence.setToolTip("Saatli planlarda: başlanan / zamanı gelen. "
                                      "Uygulama kapalıyken geçenler 'kaçırıldı' sayılır.")
        root.addWidget(self.lbl_adherence)

        btn_edit = ElidedButton("Planları düzenle")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.clicked.connect(self.edit_plans_requested.emit)
        root.addWidget(btn_edit)
        root.addStretch()

    def set_overlay(self, overlay: bool):
        """Panel tüm alanı kaplıyorsa (dar pencere) geri butonunu göster."""
        self.btn_back.setVisible(overlay)

    def refresh(self, *_):
        data = build_streak_data()
        self.grid.set_data(data)
        self.lbl_streak.setText(f"🔥 Seri: {data.current_streak} gün   ·   en iyi {data.best_streak}")
        self.lbl_week.setText(
            f"Son 7 gün: {data.active_last_7}/7 aktif   ·   {GRID_WEEKS} hafta: "
            f"{format_duration(data.total_minutes * 60)}")
        self._refresh_reviews()
        self._refresh_plans()

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().hide()  # deleteLater'a kadar eskisi üst üste çizilmesin
                item.widget().deleteLater()

    def _refresh_reviews(self):
        self._clear_layout(self.reviews_layout)
        today = logical_day(datetime.datetime.now())
        queue = review_scheduler.build_queue(today, limit=None)
        shown = queue[:review_scheduler.MAX_QUEUE]
        if not shown:
            tracked = ReviewRepository.get_tracked_course_ids()
            empty = QLabel("Bugün tekrar yok." if tracked else
                           "Takipte ders yok. Derste işlediklerini \"+ Derste işlenen\" ile gir ya da "
                           "\"Hangi dersler takipte?\" ile bir ders seç; diğer işler hatırlatma üretmez.")
            empty.setObjectName("SideMuted")
            empty.setWordWrap(True)
            self.reviews_layout.addWidget(empty)
        for item in shown:
            exam = f" · sınava {item.days_to_exam} gün" if item.days_to_exam is not None else ""
            course = f" <span style='color:#8f8273'>({item.course_name})</span>" \
                if item.course_name != item.display_name else ""
            lapse = f" · {item.lapses}× unutuldu" if item.lapses else ""
            learned = ""
            if item.learned_on:
                ago = (today - item.learned_on).days
                learned = " · derste işlendi " + ("bugün" if ago == 0 else f"{ago} gün önce")
            row = ClickLabel(
                f"<span style='color:#e8ac65; font-weight:bold'>↻</span>&nbsp; {item.display_name}{course}<br>"
                f"<span style='color:#8f8273; font-size:11px'>{item.reason_text}{learned}{exam}{lapse}</span>")
            row.setObjectName("SidePlanRow")
            row.setToolTip("Tıkla: bu konuyu aç ve sayacı başlat")
            row.clicked.connect(lambda tid=item.task_id: self.review_start_requested.emit(tid))
            self.reviews_layout.addWidget(row)
        if len(queue) > len(shown):
            more = QLabel(f"+{len(queue) - len(shown)} konu daha sırada")
            more.setObjectName("SideMuted")
            self.reviews_layout.addWidget(more)

        done = ReviewRepository.count_reviews_on(today.isoformat())
        tagged, total = ReviewRepository.feedback_fill_rate(
            datetime.datetime.now() - datetime.timedelta(days=14))
        parts = [f"Bugün {done} tekrar yapıldı"]
        if total:
            parts.append(f"Etiketleme (14 gün): {tagged}/{total}")
        self.lbl_review_stats.setText(" · ".join(parts))

    def _refresh_plans(self):
        self._clear_layout(self.plans_layout)

        now = datetime.datetime.now()
        day = logical_day(now)
        outcomes = PlanRepository.get_outcomes_for_day(day)
        plans = PlanRepository.get_plans_for_weekday(day.weekday())
        if not plans:
            empty = QLabel("Bugün için plan yok.\n\"Eğer ... ise ...\" planları ertelemeyi azaltır.")
            empty.setObjectName("SideMuted")
            empty.setWordWrap(True)
            self.plans_layout.addWidget(empty)
        for plan in plans:
            outcome = outcomes.get(plan['id'])
            if outcome == 'started':
                mark, color = "✓", "#9b9b7a"
            elif outcome == 'skipped':
                mark, color = "✗", "#d08c60"
            elif plan['time'] and now > PlanScheduler.due_time(plan, day) + datetime.timedelta(
                    minutes=PlanScheduler.GRACE_MINUTES):
                mark, color = "–", "#8f8273"
            else:
                mark, color = "•", "#ffcb69"
            row = QLabel(f"<span style='color:{color}; font-weight:bold'>{mark}</span>&nbsp; "
                         f"{plan_sentence(plan, with_days=False)}")
            row.setObjectName("SidePlanRow")
            row.setWordWrap(True)
            self.plans_layout.addWidget(row)

        st = PlanRepository.get_adherence(28)
        if st['due']:
            self.lbl_adherence.setText(
                f"Son 28 gün: {st['started']}/{st['due']} plana başlandı "
                f"· {st['skipped']} atlandı · {st['missed']} kaçırıldı")
        else:
            self.lbl_adherence.setText("")
