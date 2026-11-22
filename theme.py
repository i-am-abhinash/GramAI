"""Central modern Deep Space / Aurora theme tokens + global QSS stylesheet for GramAI."""

# Color tokens
BG          = "#080F21"
PANEL       = "#122440"
PANEL_HI    = "#20395E"
BORDER      = "#344B6C"
ACCENT      = "#55C9FF"
ACCENT_HI   = "#B9E7FF"
PURPLE_GLOW = "#A58CFF"

SUCCESS     = "#10B981"
WARNING     = "#F59E0B"
DANGER      = "#EF4444"
TEXT        = "#F8FAFC"
TEXT_MUTED  = "#CBD5E1" # Better contrast for muted text (was 94A3B8)
TEXT_DIM    = "#94A3B8" # Better contrast for dim text (was 64748B)

RADIUS = 24

APP_QSS = f"""
* {{
    font-family: "Inter", "Segoe UI", sans-serif;
    color: {TEXT};
    outline: none;
    border: none;
}}
QWidget {{
    background-color: {BG};
}}

/* Headings */
QLabel#H1     {{ font-size: 36px; font-weight: 800; letter-spacing: -0.5px; color: {TEXT}; }}
QLabel#H2     {{ font-size: 26px; font-weight: 700; color: {TEXT}; }}
QLabel#H3     {{ font-size: 18px; font-weight: 600; color: {TEXT}; }}
QLabel#Muted  {{ color: {TEXT_MUTED}; font-size: 15px; }}
QLabel#Dim    {{ color: {TEXT_DIM};   font-size: 13px; }}
QLabel#Brand  {{ font-size: 30px; font-weight: 900; color: {ACCENT}; letter-spacing: -1px; }}

/* Top header bar */
QFrame#HeaderBar {{
    background-color: rgba(18, 26, 47, 0.85);
    border-bottom: 1px solid rgba(0, 229, 255, 0.15);
}}

/* Panels / cards */
QFrame#Card {{
    background-color: rgba(25, 39, 65, 0.91);
    border: 1px solid rgba(184, 216, 250, 0.19);
    border-radius: {RADIUS}px;
}}
QFrame#CardHover:hover {{
    background-color: {PANEL_HI};
    border: 1px solid {ACCENT};
}}
QFrame#Glass {{
    background-color: rgba(38, 55, 83, 0.72);
    border: 1px solid rgba(225,242,255,0.20);
    border-radius: {RADIUS}px;
}}

/* Buttons */
QPushButton {{
    background-color: {PANEL_HI};
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 13px 25px;
    font-size: 15px;
    font-weight: 600;
    color: {TEXT};
}}
QPushButton:hover  {{ 
    background-color: rgba(28, 39, 66, 0.9); 
    border: 1px solid {ACCENT}; 
    color: {ACCENT};
}}
QPushButton:pressed{{ background-color: {PANEL}; }}

QPushButton#Primary {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT}, stop:1 #61D9C4);
    border: none;
    color: #0A2C2B;
    font-weight: 700;
}}
QPushButton#Primary:hover  {{ 
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_HI}, stop:1 {ACCENT}); 
    color: #000000;
}}
QPushButton#Primary:pressed{{ background-color: #00B4CC; }}

QPushButton#Ghost {{
    background-color: transparent;
    border: 1px solid {BORDER};
    color: {TEXT_MUTED};
}}
QPushButton#Ghost:hover {{
    border-color: {TEXT};
    color: {TEXT};
}}

QPushButton#Danger {{
    background-color: rgba(239, 68, 68, 0.15); 
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: {DANGER};
}}
QPushButton#Danger:hover {{
    background-color: {DANGER};
    color: #FFFFFF;
}}

QPushButton#IconBtn {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 24px;
    min-width: 48px; min-height: 48px;
    font-size: 20px;
}}
QPushButton#IconBtn:hover {{ 
    background-color: rgba(0, 229, 255, 0.1);
    border-color: {ACCENT}; 
    color: {ACCENT}; 
}}

/* Inputs */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
    background-color: rgba(10, 15, 28, 0.6);
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 15px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: #000000;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 1px solid {ACCENT};
    background-color: rgba(18, 26, 47, 0.8);
}}

/* Sidebar */
QFrame#Sidebar {{
    background-color: rgba(14, 25, 46, 0.96);
    border-right: 1px solid rgba(198,227,255,0.16);
}}
QPushButton#NavItem {{
    background-color: transparent;
    border: none;
    border-radius: 18px;
    text-align: left;
    padding: 16px 22px;
    font-size: 15px;
    font-weight: 600;
    color: {TEXT_MUTED};
}}
QPushButton#NavItem:hover  {{ background-color: {PANEL_HI}; color: {TEXT}; }}
QPushButton#NavItem:checked{{ 
    background-color: rgba(0, 229, 255, 0.15); 
    color: {ACCENT}; 
    border: 1px solid rgba(140,243,208,0.28);
    border-radius: 18px;
}}

/* Tables */
QTableWidget, QTableView {{
    background-color: transparent;
    gridline-color: rgba(255,255,255,0.05);
    border: none;
    font-size: 14px;
}}
QHeaderView::section {{
    background-color: transparent;
    color: {TEXT_MUTED};
    padding: 14px 10px;
    border: none;
    border-bottom: 2px solid {BORDER};
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
}}
QTableWidget::item {{ padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.02); }}
QTableWidget::item:selected {{ background-color: rgba(0, 229, 255, 0.1); color: {ACCENT}; }}

/* Scrollbars */
QScrollBar:vertical {{
    background: transparent; width: 8px; margin: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* Status pills */
QLabel#PillOk {{
    background-color: rgba(16, 185, 129, 0.15); color: {SUCCESS};
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 12px; padding: 4px 12px; font-size: 12px; font-weight: 700;
}}
QLabel#PillWarn {{
    background-color: rgba(245, 158, 11, 0.15); color: {WARNING};
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 12px; padding: 4px 12px; font-size: 12px; font-weight: 700;
}}
QLabel#PillErr {{
    background-color: rgba(239, 68, 68, 0.15); color: {DANGER};
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px; padding: 4px 12px; font-size: 12px; font-weight: 700;
}}
"""

# iOS-inspired additional styles; applied without altering backend or signal wiring.
APP_QSS += f"""
QToolTip {{ background: #223453; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 8px; padding: 8px; }}
QPushButton:disabled {{ color: #71849F; background: #1C2941; }}
QPushButton#Primary:disabled {{ color: #71849F; background: #1C2941; }}
QFrame#Glass QLabel {{ background: transparent; }}
QFrame#Sidebar QLabel {{ background: transparent; }}
"""

# Shared dark-glass styling for every screen, admin panel, form and popup.
APP_QSS += """
QMainWindow, QStackedWidget, QDialog { background: #080F21; }
QWidget { font-family: "Inter", "Segoe UI", sans-serif; }
QFrame#Card, QFrame#Glass, QFrame#AdminPanel, QFrame#AnswerGlass {
 background-color: rgba(24, 46, 78, 0.88); border: 1px solid rgba(137, 191, 247, 0.29); border-radius: 22px;
}
QFrame#HeaderBar { background-color: rgba(11, 25, 49, 0.96); border-bottom: 1px solid rgba(120, 190, 255, 0.25); }
QFrame#Sidebar { background-color: rgba(11, 25, 49, 0.97); border-right: 1px solid rgba(120, 190, 255, 0.22); }
QPushButton#NavItem:checked { background: #1668C2; color: white; border: 1px solid #4586BD; border-radius: 15px; }
QPushButton#Primary { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #36B7F5,stop:1 #286BE5); color: white; border: 1px solid #68CBFF; }
QPushButton#Primary:hover { background: #368DF4; color: white; }
QPushButton#Ghost { background: rgba(26, 54, 94, 0.65); border: 1px solid rgba(141, 199, 255, 0.3); color: #EAF5FF; }
QPushButton#Ghost:hover { background: rgba(47, 94, 151, 0.72); color: white; }
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDateEdit { background-color: rgba(11, 30, 56, 0.88); border: 1px solid #355477; border-radius: 13px; padding: 10px 13px; color: #F3F9FF; }
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus { border: 1px solid #5CCAFF; background: #18365C; }
QTableWidget, QTableView, QListWidget, QTreeWidget { background-color: #0D1F38; color: #EAF5FF; border: 1px solid #2D4D70; border-radius: 14px; alternate-background-color: #172C49; selection-background-color: #1D5A9D; }
QHeaderView::section { background: #193456; color: #B8D7F6; border: 0; border-bottom: 1px solid #355B82; padding: 12px; }
QTableCornerButton::section { background: #193456; }
QComboBox QAbstractItemView { background: #142844; color: white; selection-background-color: #236BB7; }
QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; border: none; }
QTabWidget::pane { border: 1px solid #315477; border-radius: 15px; }
QTabBar::tab { background: #152B4B; color: #BDD7F1; border-radius: 10px; padding: 12px 18px; margin-right: 6px; }
QTabBar::tab:selected { background: #216DBB; color: white; }
QCheckBox, QRadioButton { color: #EDF5FF; spacing: 10px; }
QMessageBox, QInputDialog, QFileDialog { background: #101F38; }
"""
