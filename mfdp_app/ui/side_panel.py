"""
SidePanel - Ana pencerenin solunda açılıp kapanan panel.

Üstte GitHub tarzı süreklilik ızgarası ve seri özeti, altta bugünün eğer-ise planları.
"""

import datetime

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QWidget)
from PySide6.QtCore import Qt, Signal

from mfdp_app.core.streak import build_streak_data, ACTIVE_MINUTES, GRID_WEEKS
from mfdp_app.core.daily_report import logical_day, format_duration
from mfdp_app.core.plan_scheduler import PlanScheduler
from mfdp_app.db.plan_repository import PlanRepository
from mfdp_app.ui.streak_widget import StreakGrid, LEVEL_COLORS

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


class SidePanel(QFrame):
    edit_plans_requested = Signal()

    WIDTH = 330

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidePanel")
        self.setFixedWidth(self.WIDTH)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(8)

        title = QLabel("Süreklilik")
        title.setObjectName("SideTitle")
        root.addWidget(title)

        self.grid = StreakGrid()
        root.addWidget(self.grid, 0, Qt.AlignLeft)

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
        self.lbl_streak.setToolTip(
            f"Bir gün ≥{ACTIVE_MINUTES} dk çalışıldıysa aktif sayılır.\n"
            "Tek boş gün seriyi bozmaz; iki gün üst üste boşluk bozar.")
        root.addWidget(self.lbl_streak)
        self.lbl_week = QLabel()
        self.lbl_week.setObjectName("SideMuted")
        root.addWidget(self.lbl_week)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("SideLine")
        root.addWidget(line)

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
        self.lbl_adherence.setToolTip("Saatli planlarda: başlanan / zamanı gelen. "
                                      "Uygulama kapalıyken geçenler 'kaçırıldı' sayılır.")
        root.addWidget(self.lbl_adherence)

        btn_edit = QPushButton("Planları düzenle")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.clicked.connect(self.edit_plans_requested.emit)
        root.addWidget(btn_edit)
        root.addStretch()

    def refresh(self, *_):
        data = build_streak_data()
        self.grid.set_data(data)
        self.lbl_streak.setText(f"🔥 Seri: {data.current_streak} gün   ·   en iyi {data.best_streak}")
        self.lbl_week.setText(
            f"Son 7 gün: {data.active_last_7}/7 aktif   ·   {GRID_WEEKS} hafta: "
            f"{format_duration(data.total_minutes * 60)}")
        self._refresh_plans()

    def _refresh_plans(self):
        while self.plans_layout.count():
            item = self.plans_layout.takeAt(0)
            if item.widget():
                item.widget().hide()  # deleteLater'a kadar eskisi üst üste çizilmesin
                item.widget().deleteLater()

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
                mark, color = "✓", "#a6e3a1"
            elif outcome == 'skipped':
                mark, color = "✗", "#f38ba8"
            elif plan['time'] and now > PlanScheduler.due_time(plan, day) + datetime.timedelta(
                    minutes=PlanScheduler.GRACE_MINUTES):
                mark, color = "–", "#7f849c"
            else:
                mark, color = "•", "#f9e2af"
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
