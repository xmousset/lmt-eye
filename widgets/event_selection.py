import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from scripts.events_and_modules import ALL_EVENTS
from widgets.pyqt6_tools import get_btn_style


class EventSelectionWindow(QDialog):
    """PyQt6 Dialog to select which analysis to perform"""

    def __init__(
        self,
        parent: QWidget | None,
        events_package: Literal["official", "custom"] = "official",
        preselected_events: set[str] | None = None,
    ):
        super().__init__(parent)
        if preselected_events is None:
            preselected_events = set()
        self.selected_events: set[str] = preselected_events
        match events_package:
            case "official":
                self._init_ui(ALL_EVENTS)
            case "custom":
                custom_events = get_custom_events_dict()
                self._init_ui(custom_events)
            case _:
                raise ValueError(
                    f"Invalid events_package: {events_package}. "
                    "Expected 'official' or 'custom'."
                )

    def _init_ui(self, events_dict: dict[str, Any]):
        self.setWindowTitle("LMT-EYE - Analysis Settings - Event Selection")
        self.setFixedSize(1000, 400)
        layout = QVBoxLayout()

        label = QLabel("Available events:")
        label.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(
            label,
            alignment=Qt.AlignmentFlag.AlignHCenter
            | Qt.AlignmentFlag.AlignTop,
        )

        grid_layout = QGridLayout()
        self.analysis_options = []
        max_col = 4
        max_row = (len(events_dict) + max_col - 1) // max_col
        row = 0
        col = 0
        for name in list(events_dict.keys()):
            cb = QCheckBox(name)
            module = events_dict[name]
            if isinstance(module, ModuleType):
                if getattr(module, "EVENT_DESCRIPTION", None) is not None:
                    cb.setToolTip(module.EVENT_DESCRIPTION)
            grid_layout.addWidget(cb, row, col)
            self.analysis_options.append(cb)
            if name in self.selected_events:
                cb.setChecked(True)
            row += 1
            if row >= max_row:
                col += 1
                row = 0

        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(grid_widget)
        layout.addWidget(scroll_area)

        btn_style = get_btn_style(txt_color="white", bg_color="blue")
        self.proceed_btn = QPushButton("Validate Selection")
        self.proceed_btn.setStyleSheet(btn_style)
        self.proceed_btn.clicked.connect(self.on_validation)
        layout.addWidget(
            self.proceed_btn, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.setLayout(layout)

    def on_validation(self):
        """Get all selected events."""
        self.selected_events = self.get_selected_events()
        if self.selected_events:
            list_events = ", ".join(self.selected_events)
        else:
            list_events = "No event selected"
        print(f"Selected events: {list_events}.")
        self.accept()

    def get_selected_events(self) -> set[str]:
        """Return a set of event names for checked checkboxes."""
        return {cb.text() for cb in self.analysis_options if cb.isChecked()}


def get_custom_events_dict() -> dict[str, ModuleType]:
    """
    Load all custom event modules from events/custom directory.

    Returns
    -------
    dict[str, ModuleType]
        Dictionary with EVENT_NAME as key and module as value.
        Example: {"Speed": <module>, "Rearing": <module>, ...}
    """
    custom_events_dir = Path(__file__).parent.parent / "events" / "custom"
    events_dict = {}

    if not custom_events_dir.exists():
        print(f"Warning: {custom_events_dir} does not exist")
        return events_dict

    # Iterate through all .py files in events/custom
    for file_path in custom_events_dir.glob("BuildEvent*.py"):

        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                file_path.stem,
                file_path,
            )
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get EVENT_NAME from module and add to dict
            if hasattr(module, "EVENT_NAME"):
                event_name = module.EVENT_NAME
                events_dict[event_name] = module
                print(f"✓ Loaded event: {event_name}")
            else:
                print(
                    f"⚠ Warning: {file_path.name} has no EVENT_NAME attribute"
                )

        except Exception as e:
            print(f"✗ Error loading {file_path.name}: {e}")

    return events_dict


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    preselected = {"Flickering", "Stop"}
    dialog = EventSelectionWindow(
        None,
        # events_package="official",
        events_package="custom",
        preselected_events=preselected,
    )
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("Selected events:", dialog.selected_events)
