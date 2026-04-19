from PySide6.QtWidgets import QFormLayout, QDoubleSpinBox, QSpinBox, QCheckBox, QRadioButton, QButtonGroup, QHBoxLayout, QWidget, QComboBox
from hemobind_gui.widgets.stage_panel import StagePanel
from hemobind_gui.widgets.file_input import FileInputWidget

class PrepPanel(StagePanel):
    def __init__(self, parent=None):
        super().__init__("s5", "MD Setup & Prep", parent)
        self.setup_ui()

    def setup_ui(self):
        form = QFormLayout()
        
        # Backend Selection
        self.bg_backend = QButtonGroup(self)
        self.rb_openmm = QRadioButton("OpenMM (Open Source)")
        self.rb_schrod = QRadioButton("Schrödinger (Proprietary)")
        self.bg_backend.addButton(self.rb_openmm)
        self.bg_backend.addButton(self.rb_schrod)
        self.rb_openmm.setChecked(True)
        
        backend_layout = QHBoxLayout()
        backend_layout.addWidget(self.rb_openmm)
        backend_layout.addWidget(self.rb_schrod)
        form.addRow("Simulation Backend:", backend_layout)
        
        # Schrödinger Path (hidden by default)
        self.schrodinger_path = FileInputWidget("Schrödinger Path:", mode="dir")
        self.schrodinger_path.setText("/opt/schrodinger2025-2")
        self.schrodinger_path.setVisible(False)
        form.addRow(self.schrodinger_path)
        
        self.rb_schrod.toggled.connect(lambda checked: self.schrodinger_path.setVisible(checked))
        
        # Common Settings
        self.sp_ph = QDoubleSpinBox(); self.sp_ph.setRange(0, 14); self.sp_ph.setValue(7.0)
        form.addRow("Protonation pH:", self.sp_ph)
        
        # OpenMM Specific
        self.openmm_group = QWidget()
        omm_form = QFormLayout(self.openmm_group)
        omm_form.setContentsMargins(0, 0, 0, 0)
        
        self.cb_charge = QComboBox()
        self.cb_charge.addItems(["am1bcc", "existing"])
        omm_form.addRow("Ligand Charge Method:", self.cb_charge)
        
        self.cb_fill = QCheckBox("Fill side chains"); self.cb_fill.setChecked(True)
        omm_form.addRow(self.cb_fill)
        
        form.addRow(self.openmm_group)
        self.rb_openmm.toggled.connect(lambda checked: self.openmm_group.setVisible(checked))

        self.sp_parallel = QSpinBox(); self.sp_parallel.setRange(1, 64); self.sp_parallel.setValue(3)
        form.addRow("Parallel Jobs:", self.sp_parallel)
        
        self.main_layout.addLayout(form)
        self.main_layout.addStretch()

    def get_config(self) -> dict:
        return {
            "backend": "openmm" if self.rb_openmm.isChecked() else "schrodinger",
            "schrodinger": self.schrodinger_path.text(),
            "ph": self.sp_ph.value(),
            "fill_sidechains": self.cb_fill.isChecked(),
            "parallel_jobs": self.sp_parallel.value(),
            "ligand_charge_method": self.cb_charge.currentText()
        }

    def set_config(self, cfg: dict):
        backend = cfg.get("backend", "openmm")
        if backend == "openmm": self.rb_openmm.setChecked(True)
        else: self.rb_schrod.setChecked(True)
        
        self.schrodinger_path.setText(cfg.get("schrodinger", "/opt/schrodinger2025-2"))
        self.sp_ph.setValue(cfg.get("ph", 7.0))
        self.cb_fill.setChecked(cfg.get("fill_sidechains", True))
        self.sp_parallel.setValue(cfg.get("parallel_jobs", 3))
        self.cb_charge.setCurrentText(cfg.get("ligand_charge_method", "am1bcc"))
