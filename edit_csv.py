import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import csv
import os
import sys


# Determine base directory for resource files (works for PyInstaller and dev)
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILES = [
    "bonehenge_dscr.csv",
    "bonehenge_qna.csv",
    "right_resp.csv",
    "wrong_resp.csv"
]

class CSVEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV Editor")
        self.geometry("700x400")
        self.filename = None
        self.rows = []
        self.headers = []
        self.create_widgets()

    def create_widgets(self):
        # File selection
        self.file_var = tk.StringVar(value=CSV_FILES[0])
        file_menu = ttk.OptionMenu(self, self.file_var, CSV_FILES[0], *CSV_FILES, command=self.load_csv)
        file_menu.pack(fill='x')

        # Table
        style = ttk.Style(self)
        style.configure("Treeview", rowheight=22)
        style.map("Treeview", background=[('selected', '#cce6ff')])
        style.configure("Treeview.Heading", font=(None, 10, 'bold'))
        style.configure("Treeview", font=(None, 10))
        style.configure("Treeview", borderwidth=0)
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        # Add striped row tags
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff")
        style.map("Treeview", background=[('selected', '#cce6ff')])
        self.tree = ttk.Treeview(self, show='headings')
        self.tree.tag_configure('oddrow', background='#f0f0ff')
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.pack(expand=True, fill='both')

        # In-place double-click editing removed for stability

        # Buttons (create only once, after table)
        if not hasattr(self, '_buttons_created'):
            self.btn_frame = ttk.Frame(self)
            self.btn_frame.pack(fill='x')
            self.add_btn = ttk.Button(self.btn_frame, text="Add Row", command=self.add_row)
            self.add_btn.pack(side='left')
            self.edit_btn = ttk.Button(self.btn_frame, text="Edit Row", command=self.edit_row)
            self.edit_btn.pack(side='left')
            self.delete_btn = ttk.Button(self.btn_frame, text="Delete Row", command=self.delete_row)
            self.delete_btn.pack(side='left')
            self.save_btn = ttk.Button(self.btn_frame, text="Save", command=self.save_csv)
            self.save_btn.pack(side='right')
            self._buttons_created = True


    def load_csv(self, filename):
        # Get absolute path for the selected file
        abs_path = os.path.join(BASE_DIR, filename)
        self.filename = abs_path
        self.rows = []
        if os.path.exists(abs_path):
            with open(abs_path, newline='', encoding='utf-8') as f:
                reader = list(csv.reader(f))
                # Remove blank/empty rows
                reader = [row for row in reader if any(cell.strip() for cell in row)]
                if reader:
                    self.headers = [f"Column {i+1}" for i in range(len(reader[0]))]
                    self.rows = reader
                else:
                    self.headers = ["Column 1"]
        else:
            self.headers = ["Column 1"]
        self.refresh_table()

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(range(len(self.headers)))
        for i, h in enumerate(self.headers):
            self.tree.heading(i, text=h)
            self.tree.column(i, width=100)
        for idx, row in enumerate(self.rows):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert('', 'end', values=row, tags=(tag,))

    def add_row(self):
        # Add a blank row and immediately open the first cell for editing
        row = ["" for _ in range(len(self.headers))]
        self.rows.append(row)
        self.refresh_table()
        # Open the first cell for editing after the UI updates
        self.after(50, self.edit_new_row_and_save)

    def edit_new_row_and_save(self):
        children = self.tree.get_children()
        if not children:
            return
        last_row_id = children[-1]
        bbox = self.tree.bbox(last_row_id, '#1')
        if bbox:
            x, y, width, height = bbox
            entry = tk.Entry(self.tree)
            entry.place(x=x, y=y, width=width, height=height)
            entry.focus()

            def save_edit(event=None):
                new_value = entry.get().replace(',', '').replace('\n', ' ').replace('\r', ' ').strip()
                self.rows[-1][0] = new_value
                self.refresh_table()
                entry.destroy()

            entry.bind('<Return>', save_edit)
            entry.bind('<FocusOut>', lambda e: entry.destroy())

    def edit_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Edit Row", "Select a row to edit.")
            return
        idx = self.tree.index(selected[0])
        current = self.rows[idx]
        values = simpledialog.askstring("Edit Row", f"Edit values separated by commas:", initialvalue=",".join(current))
        if values is not None:
            # Remove commas and newlines from each cell
            row = [cell.replace(',', '').replace('\n', ' ').replace('\r', ' ').strip() for cell in values.split(',')]
            while len(row) < len(self.headers):
                row.append("")
            self.rows[idx] = row
            self.refresh_table()

    def delete_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete Row", "Select a row to delete.")
            return
        idx = self.tree.index(selected[0])
        del self.rows[idx]
        self.refresh_table()

    def save_csv(self):
        # Remove blank/empty rows before saving
        clean_rows = [row for row in self.rows if any(cell.strip() for cell in row)]
        with open(self.filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(clean_rows)
        messagebox.showinfo("Save", "File saved.")

if __name__ == "__main__":
    app = CSVEditor()
    app.mainloop()