import customtkinter as ctk
from tkinter import ttk, messagebox
from app.controllers import CatalogController

class CategoriesPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", pady=(0, 10))

        self.name = ctk.CTkEntry(top, placeholder_text="Nova categoria (ex: TI, Redes, PDV...)")
        self.name.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkButton(top, text="Adicionar", command=self.add).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Excluir", fg_color="#b91c1c", hover_color="#991b1b", command=self.delete).pack(side="left", padx=6, pady=10)

        self.table = ttk.Treeview(self, columns=("id","name"), show="headings", height=18)
        self.table.heading("id", text="ID")
        self.table.heading("name", text="Categoria")
        self.table.column("id", width=70, anchor="center")
        self.table.column("name", width=560, anchor="w")
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        for i in self.table.get_children():
            self.table.delete(i)
        for c in CatalogController.list_categories():
            self.table.insert("", "end", values=(c["id"], c["name"]))

    def add(self):
        try:
            CatalogController.create_category(self.name.get())
            self.name.delete(0, "end")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Categorias", str(e))

    def delete(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("Categorias", "Selecione uma categoria.")
            return
        cid = int(self.table.item(sel[0], "values")[0])
        if not messagebox.askyesno("Categorias", "Excluir categoria?"):
            return
        try:
            CatalogController.delete_category(cid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Categorias", str(e))
