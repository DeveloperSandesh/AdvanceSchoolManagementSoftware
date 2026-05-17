#MADE BY SANDESH
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import uuid
from datetime import datetime, date
from pathlib import Path
from collections import defaultdict


try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation disabled.")
    print("Install with: pip install reportlab")


DATA_DIR = Path("school_data")
DATA_DIR.mkdir(exist_ok=True)

CLASS_LEVELS = ["Nursery", "LKG", "UKG"] + [str(i) for i in range(1, 11)]
SECTIONS = ["A", "B", "C", "D", "E"]

FILES = {
    "students": DATA_DIR / "students.json",
    "teachers": DATA_DIR / "teachers.json",
    "classes": DATA_DIR / "classes.json",
    "subjects": DATA_DIR / "subjects.json",
    "attendance": DATA_DIR / "attendance.json",
    "exams": DATA_DIR / "exams.json",
    "marks": DATA_DIR / "marks.json",
    "fees": DATA_DIR / "fees.json",
    "notices": DATA_DIR / "notices.json",
    "library": DATA_DIR / "library.json",
}

def load(key):
    if FILES[key].exists():
        with open(FILES[key], "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save(key, data):
    with open(FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def new_id():
    return str(uuid.uuid4())[:8].upper()

def today():
    return date.today().isoformat()

BG = "#0f172a"
SIDEBAR = "#1e293b"
CARD = "#1e293b"
ACCENT = "#3b82f6"
ACCENT2 = "#10b981"
DANGER = "#ef4444"
WARNING = "#f59e0b"
TEXT = "#f1f5f9"
SUBTEXT = "#94a3b8"
BORDER = "#334155"
HOVER = "#2d3f55"
WHITE = "#ffffff"
INPUT_BG = "#0f172a"

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_H2 = ("Segoe UI", 14, "bold")
FONT_H3 = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)

def styled_btn(parent, text, cmd, color=ACCENT, fg=WHITE, **kw):
    btn = tk.Button(parent, text=text, command=cmd, bg=color, fg=fg,
                    font=FONT_BODY, relief="flat", cursor="hand2", padx=12, pady=6, **kw)
    def on_enter(e): btn.config(bg=_darken(color))
    def on_leave(e): btn.config(bg=color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def _darken(hex_color):
    shades = {ACCENT: "#2563eb", ACCENT2: "#059669", DANGER: "#dc2626", WARNING: "#d97706"}
    return shades.get(hex_color, "#334155")

def label(parent, text, font=FONT_BODY, fg=TEXT, bg=None, **kw):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg or parent.cget("bg"), **kw)

def entry(parent, width=25, **kw):
    e = tk.Entry(parent, width=width, bg=INPUT_BG, fg=TEXT, insertbackground=TEXT,
                 font=FONT_BODY, relief="flat", highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=ACCENT, **kw)
    return e

def combo(parent, values, width=23, **kw):
    style = ttk.Style()
    style.configure("Dark.TCombobox", fieldbackground=INPUT_BG, background=INPUT_BG,
                    foreground=TEXT, selectbackground=ACCENT)
    return ttk.Combobox(parent, values=values, width=width, style="Dark.TCombobox", font=FONT_BODY, **kw)

def make_treeview(parent, columns, heights=14):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview", background=CARD, foreground=TEXT,
                    fieldbackground=CARD, rowheight=28, font=FONT_BODY, bordercolor=BORDER)
    style.configure("Custom.Treeview.Heading", background=SIDEBAR, foreground=ACCENT,
                    font=FONT_H3, relief="flat")
    style.map("Custom.Treeview", background=[("selected", ACCENT)])
    tree = ttk.Treeview(parent, columns=columns, show="headings", style="Custom.Treeview", height=heights)
    sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    return tree, sb

def card_frame(parent, **kw):
    return tk.Frame(parent, bg=CARD, relief="flat", highlightthickness=1, highlightbackground=BORDER, **kw)


class SchoolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🏫 School Management System - Professional Edition")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(bg=BG)
        self._build_ui()
        self.show_dashboard()

    def _build_ui(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=ACCENT, height=60)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        label(logo_frame, "🏫 SchoolMS", font=("Segoe UI", 13, "bold"), bg=ACCENT, fg=WHITE).pack(expand=True)

        nav_items = [
            ("🏠 Dashboard", self.show_dashboard),
            ("👨‍🎓 Students", self.show_students),
            ("👨‍🏫 Teachers", self.show_teachers),
            ("📋 Attendance", self.show_attendance),
            ("📝 Exams & Marks", self.show_exams),
            ("📚 Classes", self.show_classes),
            ("📖 Subjects", self.show_subjects),
            ("💰 Fees", self.show_fees),
            ("📢 Notices", self.show_notices),
            ("📗 Library", self.show_library),
            ("🔄 Promote Students", self.promote_students),
        ]
        self.nav_btns = []
        for text, cmd in nav_items:
            btn = tk.Button(self.sidebar, text=text, command=lambda c=cmd, t=text: self._nav(c, t),
                            bg=SIDEBAR, fg=TEXT, font=("Segoe UI", 10), relief="flat",
                            anchor="w", padx=20, pady=10, cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=HOVER) if b.cget("bg") != ACCENT else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=SIDEBAR) if b.cget("bg") != ACCENT else None)
            self.nav_btns.append((text, btn))

        label(self.sidebar, "v8.0 — PDF Reports", font=FONT_SMALL, fg=SUBTEXT, bg=SIDEBAR).pack(side="bottom", pady=8)

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

    def _nav(self, cmd, text):
        for t, b in self.nav_btns:
            b.config(bg=SIDEBAR if t != text else ACCENT, fg=TEXT if t != text else WHITE)
        cmd()

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def page_header(self, title, subtitle=""):
        hdr = tk.Frame(self.main, bg=BG, pady=16)
        hdr.pack(fill="x", padx=24)
        label(hdr, title, font=FONT_TITLE, bg=BG).pack(anchor="w")
        if subtitle:
            label(hdr, subtitle, font=FONT_BODY, fg=SUBTEXT, bg=BG).pack(anchor="w")
        tk.Frame(self.main, bg=BORDER, height=1).pack(fill="x", padx=24)

    
    def show_dashboard(self):
        self.clear_main()
        self.page_header("Dashboard", f"Today: {datetime.now().strftime('%B %d, %Y')}")

        students = load("students")
        teachers = load("teachers")
        fees = load("fees")
        notices = load("notices")

        active_students = [s for s in students if s.get("status") == "active"]
        active_teachers = [t for t in teachers if t.get("status") == "active"]
        total_fees = sum(float(f.get("amount", 0)) for f in fees if f.get("status") == "paid")

        stats_frame = tk.Frame(self.main, bg=BG)
        stats_frame.pack(fill="x", padx=24, pady=16)

        stats = [
            ("👨‍🎓 Total Students", len(active_students), ACCENT),
            ("👨‍🏫 Total Teachers", len(active_teachers), ACCENT2),
            ("💰 Fees Collected", f"Rs {total_fees:,.0f}", DANGER),
        ]
        for i, (title, val, color) in enumerate(stats):
            c = card_frame(stats_frame, padx=20, pady=16)
            c.grid(row=0, column=i, padx=8, sticky="ew")
            stats_frame.columnconfigure(i, weight=1)
            label(c, title, font=FONT_SMALL, fg=SUBTEXT, bg=CARD).pack(anchor="w")
            label(c, str(val), font=("Segoe UI", 22, "bold"), fg=color, bg=CARD).pack(anchor="w", pady=(4, 0))

        bottom = tk.Frame(self.main, bg=BG)
        bottom.pack(fill="both", expand=True, padx=24, pady=8)
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)

        sc = card_frame(bottom, padx=16, pady=12)
        sc.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        label(sc, "Recent Students", font=FONT_H3, bg=CARD).pack(anchor="w", pady=(0, 8))
        cols = ("Roll No", "Name", "Class")
        tree, sb = make_treeview(sc, cols, heights=8)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        for s in sorted(students, key=lambda x: x.get("created_at", ""), reverse=True)[:10]:
            if s.get("status") != "active":
                continue
            tree.insert("", "end", values=(
                s.get("roll_no", ""),
                f"{s['first_name']} {s['last_name']}",
                s.get("class_name", "")
            ))
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        nc = card_frame(bottom, padx=16, pady=12)
        nc.grid(row=0, column=1, sticky="nsew")
        label(nc, "📢 Latest Notices", font=FONT_H3, bg=CARD).pack(anchor="w", pady=(0, 8))
        for n in sorted(notices, key=lambda x: x.get("date", ""), reverse=True)[:6]:
            nf = tk.Frame(nc, bg=HOVER, pady=6, padx=8)
            nf.pack(fill="x", pady=3)
            label(nf, n.get("title", ""), font=("Segoe UI", 9, "bold"), bg=HOVER).pack(anchor="w")
            label(nf, n.get("date", ""), font=FONT_SMALL, fg=SUBTEXT, bg=HOVER).pack(anchor="w")

    
    def show_students(self):
        self.clear_main()
        self.page_header("Student Management", "Filter by class and section")

        # Filter toolbar
        filter_frame = tk.Frame(self.main, bg=BG, pady=10)
        filter_frame.pack(fill="x", padx=24)
        
        label(filter_frame, "Class:", bg=BG).pack(side="left")
        self.filter_class = combo(filter_frame, ["All"] + CLASS_LEVELS, width=10)
        self.filter_class.set("All")
        self.filter_class.pack(side="left", padx=6)
        
        label(filter_frame, "Section:", bg=BG).pack(side="left")
        self.filter_section = combo(filter_frame, ["All"] + SECTIONS, width=6)
        self.filter_section.set("All")
        self.filter_section.pack(side="left", padx=6)
        
        styled_btn(filter_frame, "🔍 Filter", self._refresh_students, ACCENT2).pack(side="left", padx=10)
        styled_btn(filter_frame, "📊 Export to CSV", self._export_students_csv, WARNING).pack(side="left")
        
        # Add student button
        btn_frame = tk.Frame(self.main, bg=BG, pady=10)
        btn_frame.pack(fill="x", padx=24)
        styled_btn(btn_frame, "+ Add Student", self.add_student_dialog).pack(side="left")
        styled_btn(btn_frame, "✏ Edit", self._edit_student, "#475569").pack(side="left", padx=6)
        styled_btn(btn_frame, "🗑 Delete", self._delete_student, DANGER).pack(side="left")

        cf = card_frame(self.main, padx=12, pady=12)
        cf.pack(fill="both", expand=True, padx=24, pady=8)
        cols = ("Roll No", "Name", "Class", "Section", "Parent", "Phone")
        self.student_tree, sb = make_treeview(cf, cols, heights=18)
        widths = [80, 180, 100, 70, 150, 110]
        for col, w in zip(cols, widths):
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=w, anchor="center")
        self.student_tree.column("Name", anchor="w")
        self.student_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._refresh_students()

    def _refresh_students(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        class_filter = self.filter_class.get()
        section_filter = self.filter_section.get()
        
        for s in load("students"):
            if s.get("status") != "active":
                continue
            if class_filter != "All" and s.get("class_name") != class_filter:
                continue
            if section_filter != "All" and s.get("section") != section_filter:
                continue
            name = f"{s['first_name']} {s['last_name']}"
            self.student_tree.insert("", "end", iid=s["id"], values=(
                s.get("roll_no", ""), name, s.get("class_name", ""), s.get("section", ""),
                s.get("parent_name", ""), s.get("phone", "")
            ))

    def _export_students_csv(self):
        students = load("students")
        if not students:
            messagebox.showinfo("Info", "No students to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                if students:
                    writer = csv.DictWriter(f, fieldnames=students[0].keys())
                    writer.writeheader()
                    writer.writerows(students)
            messagebox.showinfo("Exported", f"Saved to {path}")

    def add_student_dialog(self):
        win = self._dialog("Add New Student", 500, 550)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)
        fields = {}
        rows = [
            ("First Name*", "first_name"), ("Last Name*", "last_name"),
            ("Class", "class_name"), ("Section", "section"),
            ("Phone", "phone"), ("Parent Name", "parent_name"),
            ("Parent Phone", "parent_phone"),
        ]
        for i, (lbl_text, key) in enumerate(rows):
            label(f, lbl_text, fg=SUBTEXT, bg=CARD).grid(row=i, column=0, sticky="w", pady=4, padx=(0, 12))
            if key == "class_name":
                w = combo(f, CLASS_LEVELS)
            elif key == "section":
                w = combo(f, SECTIONS)
            else:
                w = entry(f, width=30)
            w.grid(row=i, column=1, sticky="ew", pady=4)
            fields[key] = w

        def save_student():
            fn = fields["first_name"].get().strip()
            ln = fields["last_name"].get().strip()
            if not fn or not ln:
                messagebox.showerror("Error", "First and Last name required!", parent=win)
                return
            students = load("students")
            sid = new_id()
            adm_no = f"ADM{date.today().year}{len(students)+1:04d}"
            cls = fields["class_name"].get()
            sec = fields["section"].get()
            
            existing_rolls = [int(s.get("roll_no", 0)) for s in students if s.get("class_name") == cls and s.get("section") == sec and s.get("roll_no", "").isdigit()]
            roll_no = str(max(existing_rolls) + 1) if existing_rolls else "1"
            
            student = {
                "id": sid, "admission_no": adm_no, "roll_no": roll_no,
                "first_name": fn, "last_name": ln,
                "class_name": cls, "section": sec,
                "phone": fields["phone"].get(), "parent_name": fields["parent_name"].get(),
                "parent_phone": fields["parent_phone"].get(),
                "admission_date": today(), "status": "active",
                "created_at": datetime.now().isoformat()
            }
            students.append(student)
            save("students", students)
            win.destroy()
            self._refresh_students()
            messagebox.showinfo("Success", f"Student added! Roll No: {roll_no}")

        styled_btn(f, "💾 Save Student", save_student).grid(row=len(rows), column=0, columnspan=2, pady=16)

    def _edit_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a student to edit.")
            return
        sid = sel[0]
        students = load("students")
        s = next((x for x in students if x["id"] == sid), None)
        if not s:
            return
        win = self._dialog("Edit Student", 500, 550)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)
        fields = {}
        rows = [
            ("First Name", "first_name"), ("Last Name", "last_name"),
            ("Roll No", "roll_no"), ("Class", "class_name"), ("Section", "section"),
            ("Phone", "phone"), ("Parent Name", "parent_name"), ("Parent Phone", "parent_phone"),
        ]
        for i, (lbl_text, key) in enumerate(rows):
            label(f, lbl_text, fg=SUBTEXT, bg=CARD).grid(row=i, column=0, sticky="w", pady=4, padx=(0, 12))
            if key == "class_name":
                w = combo(f, CLASS_LEVELS)
                w.set(s.get(key, ""))
            elif key == "section":
                w = combo(f, SECTIONS)
                w.set(s.get(key, ""))
            else:
                w = entry(f, width=30)
                w.insert(0, s.get(key, ""))
            w.grid(row=i, column=1, sticky="ew", pady=4)
            fields[key] = w

        def update():
            for k, w in fields.items():
                s[k] = w.get()
            save("students", students)
            win.destroy()
            self._refresh_students()
            messagebox.showinfo("Updated", "Student record updated.")

        styled_btn(f, "💾 Update", update).grid(row=len(rows), column=0, columnspan=2, pady=16)

    def _delete_student(self):
        sel = self.student_tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirm", "Delete this student?"):
            return
        sid = sel[0]
        students = [s for s in load("students") if s["id"] != sid]
        save("students", students)
        self._refresh_students()

    
    def show_teachers(self):
        self.clear_main()
        self.page_header("Teacher Management", "Manage teachers")

        toolbar = tk.Frame(self.main, bg=BG, pady=10)
        toolbar.pack(fill="x", padx=24)
        styled_btn(toolbar, "+ Add Teacher", self.add_teacher_dialog).pack(side="left")
        styled_btn(toolbar, "✏ Edit", self._edit_teacher, "#475569").pack(side="left", padx=6)
        styled_btn(toolbar, "🗑 Delete", self._delete_teacher, DANGER).pack(side="left")

        cf = card_frame(self.main, padx=12, pady=12)
        cf.pack(fill="both", expand=True, padx=24, pady=8)
        cols = ("Name", "Subject", "Email", "Phone")
        self.teacher_tree, sb = make_treeview(cf, cols, heights=18)
        widths = [160, 120, 180, 110]
        for col, w in zip(cols, widths):
            self.teacher_tree.heading(col, text=col)
            self.teacher_tree.column(col, width=w)
        self.teacher_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._refresh_teachers()

    def _refresh_teachers(self):
        for item in self.teacher_tree.get_children():
            self.teacher_tree.delete(item)
        for t in load("teachers"):
            if t.get("status") != "active":
                continue
            self.teacher_tree.insert("", "end", iid=t["id"], values=(
                f"{t['first_name']} {t['last_name']}", t.get("subject", ""),
                t.get("email", ""), t.get("phone", "")
            ))

    def add_teacher_dialog(self):
        win = self._dialog("Add Teacher", 450, 400)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)
        fields = {}
        rows = [
            ("First Name*", "first_name"), ("Last Name*", "last_name"),
            ("Email", "email"), ("Phone", "phone"), ("Subject", "subject"),
        ]
        for i, (lbl_t, key) in enumerate(rows):
            label(f, lbl_t, fg=SUBTEXT, bg=CARD).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 12))
            w = entry(f, width=28)
            w.grid(row=i, column=1, sticky="ew", pady=5)
            fields[key] = w

        def save_teacher():
            fn = fields["first_name"].get().strip()
            ln = fields["last_name"].get().strip()
            if not fn or not ln:
                messagebox.showerror("Error", "Name required!", parent=win)
                return
            teachers = load("teachers")
            tid = new_id()
            teachers.append({
                "id": tid, "employee_id": f"EMP{len(teachers)+1:04d}",
                "first_name": fn, "last_name": ln,
                "email": fields["email"].get(), "phone": fields["phone"].get(),
                "subject": fields["subject"].get(),
                "join_date": today(), "status": "active"
            })
            save("teachers", teachers)
            win.destroy()
            self._refresh_teachers()
            messagebox.showinfo("Success", "Teacher added.")

        styled_btn(f, "💾 Save Teacher", save_teacher).grid(row=len(rows), column=0, columnspan=2, pady=16)

    def _edit_teacher(self):
        sel = self.teacher_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a teacher.")
            return
        tid = sel[0]
        teachers = load("teachers")
        t = next((x for x in teachers if x["id"] == tid), None)
        if not t:
            return
        win = self._dialog("Edit Teacher", 450, 400)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)
        fields = {}
        rows = [("First Name", "first_name"), ("Last Name", "last_name"), ("Email", "email"),
                ("Phone", "phone"), ("Subject", "subject")]
        for i, (lbl_t, key) in enumerate(rows):
            label(f, lbl_t, fg=SUBTEXT, bg=CARD).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 12))
            w = entry(f, width=28)
            w.insert(0, str(t.get(key, "")))
            w.grid(row=i, column=1, sticky="ew", pady=5)
            fields[key] = w

        def update():
            for k, w in fields.items():
                t[k] = w.get()
            save("teachers", teachers)
            win.destroy()
            self._refresh_teachers()
            messagebox.showinfo("Updated", "Teacher record updated.")

        styled_btn(f, "💾 Update", update).grid(row=len(rows), column=0, columnspan=2, pady=16)

    def _delete_teacher(self):
        sel = self.teacher_tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirm", "Delete teacher?"):
            return
        tid = sel[0]
        teachers = [t for t in load("teachers") if t["id"] != tid]
        save("teachers", teachers)
        self._refresh_teachers()

    
    def show_attendance(self):
        self.clear_main()
        self.page_header("Attendance System", "Mark attendance")

        ctrl = tk.Frame(self.main, bg=BG, pady=10)
        ctrl.pack(fill="x", padx=24)

        label(ctrl, "Class:", bg=BG).pack(side="left")
        self.att_class = combo(ctrl, CLASS_LEVELS, width=10)
        self.att_class.pack(side="left", padx=6)
        
        label(ctrl, "Section:", bg=BG).pack(side="left", padx=(10,0))
        self.att_section = combo(ctrl, SECTIONS, width=6)
        self.att_section.pack(side="left", padx=6)

        label(ctrl, "Date:", bg=BG).pack(side="left", padx=(10,0))
        self.att_date = entry(ctrl, width=12)
        self.att_date.insert(0, today())
        self.att_date.pack(side="left", padx=6)

        styled_btn(ctrl, "📋 Load Students", self._load_attendance).pack(side="left", padx=8)
        styled_btn(ctrl, "💾 Save Attendance", self._save_attendance, ACCENT2).pack(side="left")

        cf = card_frame(self.main, padx=12, pady=12)
        cf.pack(fill="both", expand=True, padx=24, pady=8)
        cols = ("Roll No", "Name", "Status")
        self.att_tree, sb = make_treeview(cf, cols, heights=18)
        for col, w in zip(cols, [80, 200, 100]):
            self.att_tree.heading(col, text=col)
            self.att_tree.column(col, width=w, anchor="center")
        self.att_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _load_attendance(self):
        cls = self.att_class.get()
        sec = self.att_section.get()
        dt = self.att_date.get()
        if not cls:
            messagebox.showwarning("Select", "Select a class first.")
            return
        students = [s for s in load("students") if s.get("class_name") == cls and s.get("section") == sec and s.get("status") == "active"]
        existing = {a["student_id"]: a for a in load("attendance") if a.get("date") == dt}
        for item in self.att_tree.get_children():
            self.att_tree.delete(item)
        for s in students:
            sid = s["id"]
            status = existing.get(sid, {}).get("status", "Present")
            name = f"{s['first_name']} {s['last_name']}"
            self.att_tree.insert("", "end", iid=sid, values=(s.get("roll_no", ""), name, status))

        def toggle_status(event):
            sel = self.att_tree.selection()
            if sel:
                vals = list(self.att_tree.item(sel[0])["values"])
                cycle = ["Present", "Absent", "Late"]
                curr = vals[2]
                vals[2] = cycle[(cycle.index(curr) + 1) % len(cycle)] if curr in cycle else "Present"
                self.att_tree.item(sel[0], values=vals)
        
        self.att_tree.bind("<Double-1>", toggle_status)

    def _save_attendance(self):
        dt = self.att_date.get()
        attendance = []
        for item in self.att_tree.get_children():
            vals = self.att_tree.item(item)["values"]
            attendance.append({
                "id": new_id(), "student_id": item,
                "date": dt, "status": vals[2]
            })
        save("attendance", attendance)
        messagebox.showinfo("Saved", f"Attendance saved for {dt}!")

    
    def show_classes(self):
        self.clear_main()
        self.page_header("Classes", "Manage classes and sections")

        toolbar = tk.Frame(self.main, bg=BG, pady=10)
        toolbar.pack(fill="x", padx=24)
        styled_btn(toolbar, "+ Add Class", self._add_class).pack(side="left")

        cf = card_frame(self.main, padx=12, pady=12)
        cf.pack(fill="both", expand=True, padx=24, pady=8)
        cols = ("Class", "Section")
        self.class_tree, sb = make_treeview(cf, cols, heights=18)
        for col, w in zip(cols, [150, 100]):
            self.class_tree.heading(col, text=col)
            self.class_tree.column(col, width=w, anchor="center")
        self.class_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._refresh_classes()

    def _refresh_classes(self):
        for item in self.class_tree.get_children():
            self.class_tree.delete(item)
        for c in load("classes"):
            self.class_tree.insert("", "end", iid=c["id"], values=(
                c.get("class_name", ""), c.get("section", "")))

    def _add_class(self):
        win = self._dialog("Add Class", 350, 250)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)
        
        label(f, "Class:", fg=SUBTEXT, bg=CARD).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 12))
        cls_cb = combo(f, CLASS_LEVELS, width=20)
        cls_cb.grid(row=0, column=1, sticky="ew", pady=5)
        
        label(f, "Section:", fg=SUBTEXT, bg=CARD).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 12))
        sec_cb = combo(f, SECTIONS, width=20)
        sec_cb.grid(row=1, column=1, sticky="ew", pady=5)

        def save_class():
            classes = load("classes")
            cid = new_id()
            classes.append({"id": cid, "class_name": cls_cb.get(), "section": sec_cb.get()})
            save("classes", classes)
            win.destroy()
            self._refresh_classes()
            messagebox.showinfo("Success", "Class added.")

        styled_btn(f, "💾 Save", save_class).grid(row=2, column=0, columnspan=2, pady=16)


    def show_subjects(self):
        self.clear_main()
        self.page_header("Subjects", "Add subjects with Theory and Practical marks")

        toolbar = tk.Frame(self.main, bg=BG, pady=10)
        toolbar.pack(fill="x", padx=24)
        styled_btn(toolbar, "+ Add Subject", self._add_subject).pack(side="left")
        styled_btn(toolbar, "🗑 Delete", self._del_subject, DANGER).pack(side="left", padx=6)

        cf = card_frame(self.main, padx=12, pady=12)
        cf.pack(fill="both", expand=True, padx=24, pady=8)
        cols = ("Subject", "Class", "Theory Marks", "Practical Marks")
        self.subj_tree, sb = make_treeview(cf, cols, heights=18)
        widths = [160, 100, 100, 100]
        for col, w in zip(cols, widths):
            self.subj_tree.heading(col, text=col)
            self.subj_tree.column(col, width=w, anchor="center")
        self.subj_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._refresh_subjects()

    def _refresh_subjects(self):
        for item in self.subj_tree.get_children():
            self.subj_tree.delete(item)
        for s in load("subjects"):
            self.subj_tree.insert("", "end", iid=s["id"], values=(
                s.get("name", ""), s.get("class_name", ""),
                s.get("theory_marks", 0), s.get("practical_marks", 0)))

    def _add_subject(self):
        win = self._dialog("Add Subject", 400, 350)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)
        
        rows = [
            ("Subject Name*", "name"), ("Class", "class_name"),
            ("Theory Marks", "theory_marks"), ("Practical Marks", "practical_marks")
        ]
        fields = {}
        for i, (lbl_t, key) in enumerate(rows):
            label(f, lbl_t, fg=SUBTEXT, bg=CARD).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 12))
            if key == "class_name":
                w = combo(f, CLASS_LEVELS)
            else:
                w = entry(f, width=28)
                if "marks" in key:
                    w.insert(0, "100" if "theory" in key else "50")
            w.grid(row=i, column=1, sticky="ew", pady=5)
            fields[key] = w

        def save_subj():
            if not fields["name"].get().strip():
                messagebox.showerror("Error", "Subject name required!", parent=win)
                return
            subjects = load("subjects")
            sid = new_id()
            subjects.append({
                "id": sid,
                "name": fields["name"].get(),
                "class_name": fields["class_name"].get(),
                "theory_marks": int(fields["theory_marks"].get() or 0),
                "practical_marks": int(fields["practical_marks"].get() or 0),
            })
            save("subjects", subjects)
            win.destroy()
            self._refresh_subjects()
            messagebox.showinfo("Success", "Subject added.")

        styled_btn(f, "💾 Save", save_subj).grid(row=len(rows), column=0, columnspan=2, pady=16)

    def _del_subject(self):
        sel = self.subj_tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirm", "Delete subject?"):
            return
        sid = sel[0]
        save("subjects", [s for s in load("subjects") if s["id"] != sid])
        self._refresh_subjects()


    def show_exams(self):
        self.clear_main()
        self.page_header("Exams & Results", "Create exams, enter marks, generate PDF report cards")

        toolbar = tk.Frame(self.main, bg=BG, pady=10)
        toolbar.pack(fill="x", padx=24)
        styled_btn(toolbar, "+ Create Exam", self._add_exam).pack(side="left")
        styled_btn(toolbar, "✏ Enter Marks", self._enter_marks, ACCENT2).pack(side="left", padx=6)
        
        if PDF_AVAILABLE:
            styled_btn(toolbar, "📄 Generate Class PDF Report", self._generate_class_pdf, WARNING).pack(side="left", padx=6)
        else:
            label(toolbar, "⚠️ PDF support not available. Install reportlab", fg=DANGER, bg=BG).pack(side="left", padx=10)

        cf = card_frame(self.main, padx=12, pady=12)
        cf.pack(fill="both", expand=True, padx=24, pady=8)
        cols = ("Exam Name", "Class", "Start Date", "End Date")
        self.exam_tree, sb = make_treeview(cf, cols, heights=18)
        for col, w in zip(cols, [200, 100, 100, 100]):
            self.exam_tree.heading(col, text=col)
            self.exam_tree.column(col, width=w, anchor="center")
        self.exam_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._refresh_exams()

    def _refresh_exams(self):
        for item in self.exam_tree.get_children():
            self.exam_tree.delete(item)
        for e in load("exams"):
            self.exam_tree.insert("", "end", iid=e["id"], values=(
                e.get("name", ""), e.get("class_name", ""),
                e.get("start_date", ""), e.get("end_date", "")))

    def _add_exam(self):
        win = self._dialog("Create Exam", 400, 300)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)
        fields = {}
        rows = [("Exam Name*", "name"), ("Class", "class_name"), ("Start Date", "start_date"), ("End Date", "end_date")]
        for i, (lbl_t, key) in enumerate(rows):
            label(f, lbl_t, fg=SUBTEXT, bg=CARD).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 12))
            if key == "class_name":
                w = combo(f, CLASS_LEVELS)
            else:
                w = entry(f, width=28)
                if key in ("start_date", "end_date"):
                    w.insert(0, today())
            w.grid(row=i, column=1, sticky="ew", pady=5)
            fields[key] = w

        def save_exam():
            if not fields["name"].get().strip():
                messagebox.showerror("Error", "Exam name required!", parent=win)
                return
            exams = load("exams")
            eid = new_id()
            exams.append({"id": eid, **{k: v.get() for k, v in fields.items()}})
            save("exams", exams)
            win.destroy()
            self._refresh_exams()
            messagebox.showinfo("Success", "Exam created.")

        styled_btn(f, "💾 Save Exam", save_exam).grid(row=len(rows), column=0, columnspan=2, pady=16)

    def _enter_marks(self):
        sel = self.exam_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an exam first.")
            return
        eid = sel[0]
        exams = load("exams")
        exam = next((e for e in exams if e["id"] == eid), None)
        if not exam:
            return

        subjects = [s for s in load("subjects") if s.get("class_name") == exam.get("class_name")]
        if not subjects:
            messagebox.showwarning("No Subjects", f"No subjects found for class {exam.get('class_name')}.\n\nPlease add subjects first.")
            return

        students = [s for s in load("students") if s.get("class_name") == exam.get("class_name") and s.get("status") == "active"]
        if not students:
            messagebox.showwarning("No Students", f"No students found in class {exam.get('class_name')}.")
            return

        # Load existing marks
        marks_data = {}
        for m in load("marks"):
            if m.get("exam_id") == eid:
                key = (m["student_id"], m["subject_id"])
                marks_data[key] = {"theory": m.get("theory", 0), "practical": m.get("practical", 0), "total": m.get("total", 0)}

        win = self._dialog(f"Enter Marks - {exam['name']}", 900, 600)
        f = tk.Frame(win, bg=CARD, padx=16, pady=16)
        f.pack(fill="both", expand=True)

        cols = ["Roll No", "Student Name"] + [f"{sub['name']}" for sub in subjects]
        tree, sb = make_treeview(f, cols, heights=15)
        tree.heading("Roll No", text="Roll No")
        tree.column("Roll No", width=70, anchor="center")
        tree.heading("Student Name", text="Student Name")
        tree.column("Student Name", width=160, anchor="w")
        for sub in subjects:
            tree.heading(f"{sub['name']}", text=f"{sub['name']}")
            tree.column(f"{sub['name']}", width=100, anchor="center")

        def refresh_tree():
            for child in tree.get_children():
                tree.delete(child)
            for s in students:
                vals = [s.get("roll_no", ""), f"{s['first_name']} {s['last_name']}"]
                for sub in subjects:
                    m = marks_data.get((s["id"], sub["id"]), {})
                    vals.append(f"{m.get('theory', '-')}/{m.get('practical', '-')}")
                tree.insert("", "end", iid=s["id"], values=vals)

        refresh_tree()
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        label(f, "🔴 DOUBLE-CLICK on any student row to enter marks", font=FONT_H3, fg=WARNING, bg=CARD).pack(pady=10)

        def on_double_click(event):
            selected = tree.selection()
            if not selected:
                return
            sid = selected[0]
            student = next((s for s in students if s["id"] == sid), None)
            if not student:
                return

            mwin = self._dialog(f"Enter Marks for {student['first_name']} {student['last_name']} (Roll {student.get('roll_no','')})", 550, 500)
            mf = tk.Frame(mwin, bg=CARD, padx=20, pady=16)
            mf.pack(fill="both", expand=True)

            canvas = tk.Canvas(mf, bg=CARD, highlightthickness=0)
            scrollbar = tk.Scrollbar(mf, orient="vertical", command=canvas.yview)
            scrollable = tk.Frame(canvas, bg=CARD)
            scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            entries = {}
            row = 0
            for sub in subjects:
                tk.Label(scrollable, text=sub["name"], font=FONT_H3, bg=CARD, fg=ACCENT).grid(row=row, column=0, columnspan=4, sticky="w", pady=(10, 2))
                row += 1
                tk.Label(scrollable, text=f"Theory (max {sub.get('theory_marks', 0)}):", fg=SUBTEXT, bg=CARD).grid(row=row, column=0, sticky="e", pady=3, padx=(0, 5))
                th_ent = entry(scrollable, width=10)
                th_ent.grid(row=row, column=1, sticky="w", pady=3)
                tk.Label(scrollable, text=f"Practical (max {sub.get('practical_marks', 0)}):", fg=SUBTEXT, bg=CARD).grid(row=row, column=2, sticky="e", pady=3, padx=(10, 5))
                pr_ent = entry(scrollable, width=10)
                pr_ent.grid(row=row, column=3, sticky="w", pady=3)
                
                existing = marks_data.get((sid, sub["id"]), {})
                th_ent.insert(0, str(existing.get("theory", "")))
                pr_ent.insert(0, str(existing.get("practical", "")))
                entries[sub["id"]] = (th_ent, pr_ent, sub)
                row += 1

            def save_marks():
                all_marks = [m for m in load("marks") if not (m.get("exam_id") == eid and m.get("student_id") == sid)]
                for sub_id, (th_ent, pr_ent, sub) in entries.items():
                    th_str = th_ent.get().strip()
                    pr_str = pr_ent.get().strip()
                    theory = float(th_str) if th_str else 0
                    practical = float(pr_str) if pr_str else 0
                    
                    theory_max = sub.get("theory_marks", 0)
                    practical_max = sub.get("practical_marks", 0)
                    
                    if theory > theory_max:
                        messagebox.showerror("Error", f"Theory marks for {sub['name']} cannot exceed {theory_max}", parent=mwin)
                        return
                    if practical > practical_max:
                        messagebox.showerror("Error", f"Practical marks for {sub['name']} cannot exceed {practical_max}", parent=mwin)
                        return
                    
                    total = theory + practical
                    full_total = theory_max + practical_max
                    percentage = (total / full_total * 100) if full_total > 0 else 0
                    
                    all_marks.append({
                        "id": new_id(), "exam_id": eid, "student_id": sid, "subject_id": sub_id,
                        "theory": theory, "practical": practical, "total": total,
                        "percentage": percentage
                    })
                    marks_data[(sid, sub_id)] = {"theory": theory, "practical": practical, "total": total}
                
                save("marks", all_marks)
                refresh_tree()
                mwin.destroy()
                messagebox.showinfo("Saved", f"Marks saved for {student['first_name']} {student['last_name']}")

            styled_btn(scrollable, "💾 Save Marks", save_marks, ACCENT2).grid(row=row, column=0, columnspan=4, pady=16)

        tree.bind("<Double-1>", on_double_click)

    def _generate_class_pdf(self):
        """Generate PDF report for all students in selected exam with rankings"""
        if not PDF_AVAILABLE:
            messagebox.showerror("Error", "PDF support not available. Please install reportlab:\npip install reportlab")
            return
            
        sel = self.exam_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an exam first.")
            return
        eid = sel[0]
        exams = load("exams")
        exam = next((e for e in exams if e["id"] == eid), None)
        if not exam:
            return

     
        all_students = [s for s in load("students") if s.get("class_name") == exam.get("class_name") and s.get("status") == "active"]
        if not all_students:
            messagebox.showwarning("No Students", f"No students found in class {exam.get('class_name')}.")
            return

        subjects = {s["id"]: s for s in load("subjects") if s.get("class_name") == exam.get("class_name")}
        if not subjects:
            messagebox.showwarning("No Subjects", f"No subjects found for class {exam.get('class_name')}.")
            return

      
        results = []
        for student in all_students:
            marks_list = [m for m in load("marks") if m.get("exam_id") == eid and m.get("student_id") == student["id"]]
            
            total_obtained = 0
            total_max = 0
            subject_results = []
            
            for sub_id, sub in subjects.items():
                mark = next((m for m in marks_list if m["subject_id"] == sub_id), None)
                if mark:
                    theory = mark.get("theory", 0)
                    practical = mark.get("practical", 0)
                    total = theory + practical
                    max_total = sub.get("theory_marks", 0) + sub.get("practical_marks", 0)
                    total_obtained += total
                    total_max += max_total
                    percentage = (total / max_total * 100) if max_total > 0 else 0
                    grade = self._calculate_grade(percentage)
                    subject_results.append({
                        "name": sub["name"],
                        "theory": f"{theory}/{sub.get('theory_marks', 0)}",
                        "practical": f"{practical}/{sub.get('practical_marks', 0)}",
                        "total": f"{total}/{max_total}",
                        "percentage": percentage,
                        "grade": grade
                    })
                else:
                    subject_results.append({
                        "name": sub["name"],
                        "theory": "-",
                        "practical": "-",
                        "total": "-/-",
                        "percentage": 0,
                        "grade": "N/A"
                    })
            
            overall_percentage = (total_obtained / total_max * 100) if total_max > 0 else 0
            overall_grade = self._calculate_grade(overall_percentage)
            
            results.append({
                "student": student,
                "subjects": subject_results,
                "total_obtained": total_obtained,
                "total_max": total_max,
                "percentage": overall_percentage,
                "grade": overall_grade
            })
        

        results.sort(key=lambda x: x["percentage"], reverse=True)
        
        # Add rank
        for i, r in enumerate(results):
            r["rank"] = i + 1
        
       
        default_name = f"Report_{exam['name']}_{exam['class_name']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=default_name, filetypes=[("PDF files", "*.pdf")])
        if not filepath:
            return
        
        # Generate PDF
        self._create_pdf_report(filepath, exam, results)
        messagebox.showinfo("Success", f"PDF Report generated successfully!\nSaved to: {filepath}")

    def _calculate_grade(self, percentage):
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B+"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C+"
        elif percentage >= 40:
            return "C"
        else:
            return "F"

    def _create_pdf_report(self, filepath, exam, results):
        """Create multi-page PDF report with rankings"""
        doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
       
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, textColor=colors.HexColor('#0f172a'))
        header_style = ParagraphStyle('Header', parent=styles['Heading2'], fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor('#3b82f6'))
        normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9)
        grade_style = ParagraphStyle('Grade', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)
        
        for idx, result in enumerate(results):
            student = result["student"]
            
           
            story.append(Paragraph("SCHOOL MANAGEMENT SYSTEM", title_style))
            story.append(Paragraph("PROGRESS REPORT CARD", header_style))
            story.append(Spacer(1, 0.2*inch))
            
            info_data = [
                ["Student Name:", f"{student['first_name']} {student['last_name']}", "Roll No:", student.get("roll_no", "")],
                ["Class:", f"{student.get('class_name', '')} - {student.get('section', '')}", "Exam:", exam.get("name", "")],
                ["Rank:", f"{result['rank']} / {len(results)}", "Overall Grade:", result['grade']]
            ]
            
            info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f172a')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.15*inch))
            
         
            marks_data = [["Subject", "Theory", "Practical", "Total", "Grade"]]
            for sub in result["subjects"]:
                marks_data.append([
                    sub["name"], sub["theory"], sub["practical"], sub["total"], sub["grade"]
                ])
            
            marks_table = Table(marks_data, colWidths=[2.2*inch, 1*inch, 1*inch, 1.2*inch, 1*inch])
            marks_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#0f172a')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(marks_table)
            story.append(Spacer(1, 0.15*inch))
            
    
            percentage = result["percentage"]
            grade = result["grade"]
            grade_color = '#10b981' if grade not in ('F', 'N/A') else '#ef4444'
            
            summary_data = [
                ["Total Marks:", f"{result['total_obtained']} / {result['total_max']}"],
                ["Percentage:", f"{percentage:.2f}%"],
                ["Grade:", grade]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f172a')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bae6fd')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ]))
            story.append(summary_table)
            
  
            if idx < len(results) - 1:
                story.append(PageBreak())
        
        doc.build(story)


    def show_fees(self):
        self.clear_main()
        self.page_header("Fee Management", "Collect fees")

        toolbar = tk.Frame(self.main, bg=BG, pady=10)
        toolbar.pack(fill="x", padx=24)
        styled_btn(toolbar, "+ Collect Fee", self._collect_fee).pack(side="left")

        cf = card_frame(self.main, padx=12, pady=12)
        cf.pack(fill="both", expand=True, padx=24, pady=8)
        cols = ("Receipt No", "Student", "Amount", "Date", "Status")
        self.fee_tree, sb = make_treeview(cf, cols, heights=16)
        for col, w in zip(cols, [100, 180, 90, 100, 80]):
            self.fee_tree.heading(col, text=col)
            self.fee_tree.column(col, width=w, anchor="center")
        self.fee_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._refresh_fees()

    def _refresh_fees(self):
        for item in self.fee_tree.get_children():
            self.fee_tree.delete(item)
        students = {s["id"]: f"{s['first_name']} {s['last_name']}" for s in load("students")}
        for f in load("fees"):
            self.fee_tree.insert("", "end", iid=f["id"], values=(
                f.get("receipt_no", ""), students.get(f.get("student_id", ""), "Unknown"),
                f"Rs {f.get('amount', 0):,.0f}", f.get("date", ""), f.get("status", "")))

    def _collect_fee(self):
        win = self._dialog("Collect Fee", 400, 350)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)
        
        students = [s for s in load("students") if s.get("status") == "active"]
        snames = [f"{s['first_name']} {s['last_name']}" for s in students]
        
        label(f, "Student*", fg=SUBTEXT, bg=CARD).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 12))
        student_var = tk.StringVar()
        sc = combo(f, snames, width=25, textvariable=student_var)
        sc.grid(row=0, column=1, sticky="ew", pady=5)
        
        label(f, "Amount (Rs)*", fg=SUBTEXT, bg=CARD).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 12))
        amt_e = entry(f, width=25)
        amt_e.grid(row=1, column=1, sticky="ew", pady=5)

        def save_fee():
            idx = snames.index(student_var.get()) if student_var.get() in snames else -1
            if idx < 0:
                messagebox.showerror("Error", "Select student!", parent=win)
                return
            amt = amt_e.get().strip()
            if not amt:
                messagebox.showerror("Error", "Amount required!", parent=win)
                return
            fees = load("fees")
            fid = new_id()
            fees.append({
                "id": fid, "student_id": students[idx]["id"],
                "amount": float(amt), "date": today(),
                "status": "paid", "receipt_no": f"RCP{len(fees)+1:04d}"
            })
            save("fees", fees)
            win.destroy()
            self._refresh_fees()
            messagebox.showinfo("Success", "Fee collected!")

        styled_btn(f, "💰 Collect Fee", save_fee, ACCENT2).grid(row=2, column=0, columnspan=2, pady=16)


    def show_notices(self):
        self.clear_main()
        self.page_header("Notices", "School notices")

        toolbar = tk.Frame(self.main, bg=BG, pady=10)
        toolbar.pack(fill="x", padx=24)
        styled_btn(toolbar, "+ Post Notice", self._add_notice).pack(side="left")
        styled_btn(toolbar, "🗑 Delete", self._del_notice, DANGER).pack(side="left", padx=6)

        cf = card_frame(self.main, padx=12, pady=12)
        cf.pack(fill="both", expand=True, padx=24, pady=8)
        cols = ("Title", "Date")
        self.notice_tree, sb = make_treeview(cf, cols, heights=8)
        for col, w in zip(cols, [400, 100]):
            self.notice_tree.heading(col, text=col)
            self.notice_tree.column(col, width=w)
        self.notice_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._refresh_notices()

    def _refresh_notices(self):
        for item in self.notice_tree.get_children():
            self.notice_tree.delete(item)
        for n in load("notices"):
            self.notice_tree.insert("", "end", iid=n["id"], values=(n.get("title", ""), n.get("date", "")))

    def _add_notice(self):
        win = self._dialog("Post Notice", 400, 350)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        
        label(f, "Title*", fg=SUBTEXT, bg=CARD).pack(anchor="w")
        title_e = entry(f, width=40)
        title_e.pack(fill="x", pady=(4, 10))
        
        label(f, "Content*", fg=SUBTEXT, bg=CARD).pack(anchor="w")
        content_t = tk.Text(f, bg=INPUT_BG, fg=TEXT, font=FONT_BODY, height=6, relief="flat", insertbackground=TEXT)
        content_t.pack(fill="both", expand=True, pady=4)

        def save_notice():
            if not title_e.get().strip():
                messagebox.showerror("Error", "Title required!", parent=win)
                return
            notices = load("notices")
            nid = new_id()
            notices.append({
                "id": nid, "title": title_e.get().strip(), "content": content_t.get("1.0", tk.END).strip(),
                "date": today()
            })
            save("notices", notices)
            win.destroy()
            self._refresh_notices()
            messagebox.showinfo("Success", "Notice posted.")

        styled_btn(f, "📢 Post Notice", save_notice, ACCENT2).pack(pady=8)

    def _del_notice(self):
        sel = self.notice_tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirm", "Delete notice?"):
            return
        nid = sel[0]
        save("notices", [n for n in load("notices") if n["id"] != nid])
        self._refresh_notices()


    def show_library(self):
        self.clear_main()
        self.page_header("Library", "Book management")

        toolbar = tk.Frame(self.main, bg=BG, pady=10)
        toolbar.pack(fill="x", padx=24)
        styled_btn(toolbar, "+ Add Book", self._add_book).pack(side="left")

        cf = card_frame(self.main, padx=12, pady=12)
        cf.pack(fill="both", expand=True, padx=24, pady=8)
        cols = ("Title", "Author", "Category")
        self.lib_tree, sb = make_treeview(cf, cols, heights=18)
        for col, w in zip(cols, [220, 150, 120]):
            self.lib_tree.heading(col, text=col)
            self.lib_tree.column(col, width=w, anchor="center")
        self.lib_tree.column("Title", anchor="w")
        self.lib_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._refresh_library()

    def _refresh_library(self):
        for item in self.lib_tree.get_children():
            self.lib_tree.delete(item)
        for b in load("library"):
            self.lib_tree.insert("", "end", iid=b["id"], values=(
                b.get("title", ""), b.get("author", ""), b.get("category", "")))

    def _add_book(self):
        win = self._dialog("Add Book", 400, 350)
        f = tk.Frame(win, bg=CARD, padx=24, pady=16)
        f.pack(fill="both", expand=True)
        f.columnconfigure(1, weight=1)
        
        rows = [("Title*", "title"), ("Author", "author"), ("Category", "category")]
        fields = {}
        for i, (lbl_t, key) in enumerate(rows):
            label(f, lbl_t, fg=SUBTEXT, bg=CARD).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 12))
            if key == "category":
                w = combo(f, ["Textbook", "Fiction", "Non-fiction", "Reference"])
            else:
                w = entry(f, width=28)
            w.grid(row=i, column=1, sticky="ew", pady=5)
            fields[key] = w

        def save_book():
            if not fields["title"].get().strip():
                messagebox.showerror("Error", "Title required!", parent=win)
                return
            books = load("library")
            bid = new_id()
            books.append({
                "id": bid, "title": fields["title"].get(), "author": fields["author"].get(),
                "category": fields["category"].get(),
            })
            save("library", books)
            win.destroy()
            self._refresh_library()
            messagebox.showinfo("Success", "Book added.")

        styled_btn(f, "💾 Save Book", save_book).grid(row=len(rows), column=0, columnspan=2, pady=16)


    def promote_students(self):
        students = load("students")
        active_classes = sorted(set(s.get("class_name") for s in students if s.get("status") == "active"))
        if not active_classes:
            messagebox.showinfo("Info", "No active students.")
            return

        win = self._dialog("Promote Students", 400, 220)
        f = tk.Frame(win, bg=CARD, padx=20, pady=20)
        f.pack(fill="both", expand=True)

        label(f, "From Class:", fg=SUBTEXT, bg=CARD).pack(anchor="w")
        from_class = combo(f, active_classes, width=20)
        from_class.pack(fill="x", pady=(4, 12))

        label(f, "To Class:", fg=SUBTEXT, bg=CARD).pack(anchor="w")
        to_class = combo(f, CLASS_LEVELS, width=20)
        to_class.pack(fill="x", pady=(4, 12))

        def do_promote():
            curr = from_class.get()
            target = to_class.get()
            if not curr or not target:
                messagebox.showerror("Error", "Select both classes.")
                return
            if curr == target:
                messagebox.showerror("Error", "Promotion class must be different.")
                return
            if not messagebox.askyesno("Confirm", f"Promote all students from {curr} to {target}?"):
                return
            updated = 0
            for s in students:
                if s.get("class_name") == curr and s.get("status") == "active":
                    s["class_name"] = target
                    updated += 1
            save("students", students)
            win.destroy()
            self._refresh_students()
            messagebox.showinfo("Promotion", f"{updated} student(s) promoted.")

        styled_btn(f, "🔄 Promote Now", do_promote, ACCENT2).pack(pady=10)


    def _dialog(self, title, w, h):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry(f"{w}x{h}")
        win.configure(bg=CARD)
        win.transient(self)
        win.update_idletasks()
        win.grab_set()
        x = self.winfo_x() + (self.winfo_width() - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        win.geometry(f"+{x}+{y}")
        return win


from reportlab.platypus import PageBreak


if __name__ == "__main__":
    if not any(f.exists() for f in FILES.values()):
        save("students", [])
        save("teachers", [])
        save("classes", [])
        save("subjects", [])
        save("attendance", [])
        save("exams", [])
        save("marks", [])
        save("fees", [])
        save("notices", [])
        save("library", [])
    app = SchoolApp()
    app.mainloop()
