import customtkinter as ctk
from tkinter import ttk, messagebox
from app.controllers import CatalogController

class SuppliersPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(top, text="Novo", command=self.new).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(top, text="Editar", command=self.edit).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Excluir", fg_color="#b91c1c", hover_color="#991b1b", command=self.delete).pack(side="left", padx=6, pady=10)

        self.table = ttk.Treeview(self, columns=("id","name","cnpj","phone","email"), show="headings", height=18)
        for col, txt, w in [("id","ID",70),("name","Nome",240),("cnpj","CNPJ",120),("phone","Telefone",120),("email","Email",240)]:
            self.table.heading(col, text=txt)
            self.table.column(col, width=w, anchor="w")
        self.table.column("id", anchor="center")
        self.table.pack(fill="both", expand=True)

    def _selected_id(self):
        sel = self.table.selection()
        if not sel:
            return None
        return int(self.table.item(sel[0], "values")[0])

    def refresh(self):
        for i in self.table.get_children():
            self.table.delete(i)
        for s in CatalogController.list_suppliers():
            self.table.insert("", "end", values=(s["id"], s["name"], s.get("cnpj","") or "", s.get("phone","") or "", s.get("email","") or ""))

    def new(self):
        SupplierForm(self, "Novo Fornecedor", on_save=lambda d: (CatalogController.create_supplier(**d), self.refresh()))

    def edit(self):
        sid = self._selected_id()
        if not sid:
            messagebox.showwarning("Fornecedores", "Selecione um fornecedor.")
            return
        current = next((x for x in CatalogController.list_suppliers() if x["id"] == sid), None)
        if not current:
            messagebox.showerror("Fornecedores", "Fornecedor não encontrado.")
            return
        SupplierForm(self, "Editar Fornecedor", initial=current, on_save=lambda d: (CatalogController.update_supplier(sid, **d), self.refresh()))

    def delete(self):
        sid = self._selected_id()
        if not sid:
            messagebox.showwarning("Fornecedores", "Selecione um fornecedor.")
            return
        if not messagebox.askyesno("Fornecedores", "Excluir fornecedor?"):
            return
        try:
            CatalogController.delete_supplier(sid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Fornecedores", str(e))

class SupplierForm(ctk.CTkToplevel):
    def __init__(self, master, title, on_save, initial=None):
        super().__init__(master)
        self.title(title)
        self.geometry("640x420")
        self.resizable(False, False)
        self.grab_set()
        self.on_save = on_save
        self.initial = initial or {}

        self.var_name = ctk.StringVar(value=self.initial.get("name",""))
        self.var_cnpj = ctk.StringVar(value=self.initial.get("cnpj","") or "")
        self.var_phone = ctk.StringVar(value=self.initial.get("phone","") or "")
        self.var_email = ctk.StringVar(value=self.initial.get("email","") or "")

        frm = ctk.CTkFrame(self, corner_radius=14)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        def row(label, widget, r):
            ctk.CTkLabel(frm, text=label).grid(row=r, column=0, sticky="w", padx=12, pady=10)
            widget.grid(row=r, column=1, sticky="ew", padx=12, pady=10)
            frm.grid_columnconfigure(1, weight=1)

        row("Nome *", ctk.CTkEntry(frm, textvariable=self.var_name), 0)
        row("CNPJ", ctk.CTkEntry(frm, textvariable=self.var_cnpj), 1)
        row("Telefone", ctk.CTkEntry(frm, textvariable=self.var_phone), 2)
        row("Email", ctk.CTkEntry(frm, textvariable=self.var_email), 3)

        actions = ctk.CTkFrame(frm, fg_color="transparent")
        actions.grid(row=4, column=0, columnspan=2, sticky="e", padx=12, pady=12)
        ctk.CTkButton(actions, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", command=self.destroy).pack(side="right", padx=8)
        ctk.CTkButton(actions, text="Salvar", command=self._save).pack(side="right")

    def _save(self):
        try:
            name = self.var_name.get().strip()
            if not name:
                raise ValueError("Nome é obrigatório.")
            data = {"name": name, "cnpj": self.var_cnpj.get().strip(), "phone": self.var_phone.get().strip(), "email": self.var_email.get().strip()}
            self.on_save(data)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Fornecedor", str(e))
