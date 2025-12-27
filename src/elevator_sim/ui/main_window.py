from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication, QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog, QGridLayout, QPushButton, QWidget

from ..core.controller import ElevatorController
from ..core.events import format_event
from ..core.model import DoorState
from ..core.scheduler import FifoScheduler, ScanScheduler, SimpleScheduler
from ..render.pygame_canvas import PygameCanvas


class MainWindow:
    def __init__(self) -> None:
        ui_path = Path(__file__).resolve().parent / "ui_files" / "Elevator_Interface_updated.ui"
        loader = QUiLoader()
        self.ui = loader.load(str(ui_path))
        if self.ui is None:
            raise RuntimeError(f"Failed to load UI: {ui_path}")

        self.ui.setWindowTitle("Elevator Simulation")
        self._info_dialog = self._load_info_dialog()

        self.controller = ElevatorController()
        self.renderer = PygameCanvas(width=480, height=520, floor_count=self.controller.floor_count)
        self._running = False
        self._last_tick = time.monotonic()
        self._floor_layout: Optional[QGridLayout] = None
        self._floor_buttons: Dict[int, QPushButton] = {}

        self.timer = QTimer()
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._on_tick)

        self._apply_assets()
        self._setup_controls()
        self._rebuild_floor_buttons()
        self._render_frame()
        self._show_start_page()

    def show(self) -> None:
        self.ui.show()

    def _apply_assets(self) -> None:
        assets_dir = Path(__file__).resolve().parent / "assets"
        open_icon = QIcon(str(assets_dir / "open_doors.png"))
        close_icon = QIcon(str(assets_dir / "close_doors.png"))
        self.ui.open_door_button.setIcon(open_icon)
        self.ui.close_door_button.setIcon(close_icon)
        self.ui.open_door_button.setIconSize(self.ui.open_door_button.sizeHint())
        self.ui.close_door_button.setIconSize(self.ui.close_door_button.sizeHint())

    def _setup_controls(self) -> None:
        self.ui.start_button.clicked.connect(self._show_config_page)
        self.ui.back_button.clicked.connect(self._show_start_page)
        self.ui.simulate_button.clicked.connect(self._start_simulation)
        self.ui.back_to_config_button.clicked.connect(self._show_config_page)
        self.ui.about_button.clicked.connect(self._show_about_dialog)

        self.ui.start_pause_button.clicked.connect(self._toggle_running)
        self.ui.reset_button.clicked.connect(self._reset_simulation)
        self.ui.emergency_button.toggled.connect(self._toggle_emergency)
        self.ui.open_door_button.clicked.connect(self._open_door)
        self.ui.close_door_button.clicked.connect(self._close_door)

        self.ui.clear_log_button.clicked.connect(self.ui.log_output.clear)
        self.ui.copy_log_button.clicked.connect(self._copy_logs)
        self.ui.export_log_button.clicked.connect(self._export_logs)
        self.ui.logs_toggle_button.toggled.connect(self._toggle_logs_drawer)

        self.ui.simulation_label.setFixedSize(520, 520)
        self.ui.simulation_label.setScaledContents(True)
        self.ui.log_output.setReadOnly(True)
        self.ui.emergency_button.setCheckable(True)
        self.ui.logs_toggle_button.setChecked(False)
        self.ui.logs_content.setVisible(False)

        self.ui.floor_count_spin.setValue(self.controller.floor_count)
        self._change_mode(self.ui.mode_combo.currentText())

    def _show_start_page(self) -> None:
        self._stop_timer()
        self.ui.stacked_widget.setCurrentWidget(self.ui.start_page)

    def _show_config_page(self) -> None:
        self._stop_timer()
        self.ui.stacked_widget.setCurrentWidget(self.ui.config_page)

    def _start_simulation(self) -> None:
        self._apply_config()
        self.ui.stacked_widget.setCurrentWidget(self.ui.sim_page)
        self._last_tick = time.monotonic()
        self._start_timer()
        self._update_status()
        self._update_controls()

    def _apply_config(self) -> None:
        floor_count = self.ui.floor_count_spin.value()
        self.controller.reset()
        self.controller.set_floor_count(floor_count)
        self.renderer.set_floor_count(self.controller.floor_count)
        self._change_mode(self.ui.mode_combo.currentText())
        self._rebuild_floor_buttons()
        self._log_message(f"Configured for {floor_count} floors")

    def _toggle_running(self) -> None:
        self._running = not self._running
        label = "Pause" if self._running else "Start"
        self.ui.start_pause_button.setText(label)

    def _reset_simulation(self) -> None:
        self._running = False
        self.ui.start_pause_button.setText("Start")
        self.controller.reset()
        self.controller.set_floor_count(self.ui.floor_count_spin.value())
        self.renderer.set_floor_count(self.controller.floor_count)
        self._rebuild_floor_buttons()
        self._log_message("Simulation reset")

    def _toggle_emergency(self, active: bool) -> None:
        self.controller.set_emergency_stop(active)
        if active:
            self._running = False
            self.ui.start_pause_button.setText("Start")
        self._update_controls()

    def _open_door(self) -> None:
        if self.controller.request_open_door():
            self._log_message("Door command: open")

    def _close_door(self) -> None:
        if self.controller.request_close_door():
            self._log_message("Door command: close")

    def _change_mode(self, text: str) -> None:
        if text == "Simple":
            scheduler = SimpleScheduler()
        elif text == "SCAN":
            scheduler = ScanScheduler()
        else:
            scheduler = FifoScheduler()
        self.controller.set_scheduler(scheduler)
        self._update_status()

    def _rebuild_floor_buttons(self) -> None:
        container = self.ui.floor_button_container
        if self._floor_layout is not None:
            while self._floor_layout.count():
                item = self._floor_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            QWidget().setLayout(self._floor_layout)

        self._floor_layout = QGridLayout()
        self._floor_layout.setSpacing(6)
        container.setLayout(self._floor_layout)
        self._floor_buttons.clear()

        floor_count = self.controller.floor_count
        columns = 3 if floor_count > 6 else 2
        for index in range(floor_count):
            floor = index + 1
            button = QPushButton(str(floor))
            button.setMinimumSize(48, 42)
            button.clicked.connect(lambda _, f=floor: self._request_floor(f))
            row = index // columns
            col = index % columns
            self._floor_layout.addWidget(button, row, col)
            self._floor_buttons[floor] = button

        self._update_request_buttons()

    def _request_floor(self, floor: int) -> None:
        if self.controller.add_request(floor):
            self._log_message(f"Floor {floor} requested")
        self._update_request_buttons()

    def _on_tick(self) -> None:
        now = time.monotonic()
        dt = now - self._last_tick
        self._last_tick = now

        if self._running:
            self.controller.update(dt)

        self._render_frame()
        self._update_status()
        self._update_controls()
        self._drain_events()

    def _render_frame(self) -> None:
        image = self.renderer.draw(self.controller.state)
        pixmap = QPixmap.fromImage(image)
        self.ui.simulation_label.setPixmap(pixmap)

    def _update_status(self) -> None:
        state = self.controller.state
        self.ui.current_floor_value.setText(f"{state.current_floor:.2f}")
        self.ui.direction_value.setText(state.direction.value)
        self.ui.door_value.setText(state.door_state.value)
        next_stops = self.controller.pending_requests()
        next_text = ", ".join(str(floor) for floor in next_stops) if next_stops else "-"
        self.ui.next_stops_value.setText(next_text)
        self.ui.mode_value.setText(self.controller.scheduler.name)

    def _update_controls(self) -> None:
        door = self.controller.state.door_state
        emergency = self.controller.emergency_stop
        self.ui.open_door_button.setEnabled(not emergency and door in (DoorState.CLOSED, DoorState.CLOSING))
        self.ui.close_door_button.setEnabled(not emergency and door in (DoorState.OPEN, DoorState.OPENING))
        self._update_request_buttons()

    def _update_request_buttons(self) -> None:
        pending = set(self.controller.pending_requests())
        for floor, button in self._floor_buttons.items():
            button.setEnabled(floor not in pending)

    def _drain_events(self) -> None:
        for event in self.controller.consume_events():
            self._log_message(format_event(event))

    def _log_message(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.ui.log_output.appendPlainText(f"[{timestamp}] {message}")
        self.ui.log_output.ensureCursorVisible()

    def _start_timer(self) -> None:
        if not self.timer.isActive():
            self.timer.start()

    def _stop_timer(self) -> None:
        if self.timer.isActive():
            self.timer.stop()

    def _toggle_logs_drawer(self, expanded: bool) -> None:
        self.ui.logs_content.setVisible(expanded)
        self.ui.logs_toggle_button.setText("Logs ▲" if expanded else "Logs ▼")

    def _copy_logs(self) -> None:
        QGuiApplication.clipboard().setText(self.ui.log_output.toPlainText())

    def _export_logs(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self.ui, "Export Logs", "elevator_logs.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(self.ui.log_output.toPlainText())

    def _load_info_dialog(self) -> Optional[QWidget]:
        info_path = Path(__file__).resolve().parent / "ui_files" / "Info_window_gui.ui"
        loader = QUiLoader()
        dialog = loader.load(str(info_path))
        if dialog is None:
            return None
        return dialog

    def _show_about_dialog(self) -> None:
        if self._info_dialog is not None:
            self._info_dialog.show()
