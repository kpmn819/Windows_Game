import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import csv
import os

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

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text="Add Row", command=self.add_row).pack(side='left')
        ttk.Button(btn_frame, text="Edit Row", command=self.edit_row).pack(side='left')
        ttk.Button(btn_frame, text="Delete Row", command=self.delete_row).pack(side='left')
        ttk.Button(btn_frame, text="Save", command=self.save_csv).pack(side='right')

        self.load_csv(self.file_var.get())

    def load_csv(self, filename):
        self.filename = filename
        self.rows = []
        if os.path.exists(filename):
            with open(filename, newline='', encoding='utf-8') as f:
                reader = list(csv.reader(f))
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
        values = simpledialog.askstring("Add Row", f"Enter values separated by commas ({len(self.headers)} columns):")
        if values is not None:
            # Remove commas and newlines from each cell
            row = [cell.replace(',', '').replace('\n', ' ').replace('\r', ' ').strip() for cell in values.split(',')]
            while len(row) < len(self.headers):
                row.append("")
            self.rows.append(row)
            self.refresh_table()

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
        with open(self.filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(self.rows)
        messagebox.showinfo("Save", "File saved.")

if __name__ == "__main__":
    app = CSVEditor()
    app.mainloop()