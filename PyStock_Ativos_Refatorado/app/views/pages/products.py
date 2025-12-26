import customtkinter as ctk
from tkinter import ttk, messagebox

from app.controllers import CatalogController

class ProductsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", pady=(0, 10))

        self.search = ctk.CTkEntry(top, placeholder_text="Buscar produto/modelo...")
        self.search.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())

        ctk.CTkButton(top, text="Novo", command=self.new_product).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Editar", command=self.edit_product).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Excluir", fg_color="#b91c1c", hover_color="#991b1b", command=self.delete_product).pack(side="left", padx=6, pady=10)

        self.table = ttk.Treeview(self, columns=("id","produto","categoria","fornecedor","custo","min","stock"), show="headings", height=18)
        for col, txt, w in [
            ("produto","Produto/Modelo",430), ("categoria","Categoria",140), ("fornecedor","Fornecedor",160),
            ("custo","Custo",110), ("min","Mín",70), ("stock","Em estoque",90),
        ]:
            self.table.heading(col, text=txt)
            self.table.column(col, width=w, anchor="w")
        self.table.column("custo", anchor="e")
        self.table.column("min", anchor="center")
        self.table.column("stock", anchor="center")
        self.table.heading("id", text="ID")
        self.table.column("id", width=0, stretch=False)
        self.table.pack(fill="both", expand=True)

        self.table.tag_configure("low", background="#fee2e2")

    def _selected_id(self):
        sel = self.table.selection()
        if not sel:
            return None
        vals = self.table.item(sel[0], "values")
        return int(vals[0])

    def refresh(self):
        for i in self.table.get_children():
            self.table.delete(i)
        rows = CatalogController.list_products(self.search.get())
        for p in rows:
            is_low = int(p["stock"]) < int(p["min_stock"])
            tag = ("low",) if is_low else ()
            self.table.insert("", "end", values=(
                p["id"], p["name"], p["category"], p["supplier"],
                f'{p["cost_price"]:.2f}', p["min_stock"], p["stock"]
            ), tags=tag)

    def new_product(self):
        ProductForm(self, title="Novo Produto/Modelo", on_save=lambda data: (CatalogController.create_product(**data), self.refresh()))

    def edit_product(self):
        pid = self._selected_id()
        if not pid:
            messagebox.showwarning("Produtos", "Selecione um produto.")
            return
        current = next((x for x in CatalogController.list_products("") if x["id"] == pid), None)
        if not current:
            messagebox.showerror("Produtos", "Produto não encontrado.")
            return
        ProductForm(self, title="Editar Produto/Modelo", initial=current, on_save=lambda data: (CatalogController.update_product(pid, **data), self.refresh()))

    def delete_product(self):
        pid = self._selected_id()
        if not pid:
            messagebox.showwarning("Produtos", "Selecione um produto.")
            return
        if not messagebox.askyesno("Produtos", "Excluir produto/modelo?"):
            return
        try:
            CatalogController.delete_product(pid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Produtos", str(e))

class ProductForm(ctk.CTkToplevel):
    def __init__(self, master, title: str, on_save, initial=None):
        super().__init__(master)
        self.title(title)
        self.geometry("720x460")
        self.resizable(False, False)
        self.on_save = on_save
        self.initial = initial or {}
        self.grab_set()

        cats = CatalogController.list_categories()
        sups = CatalogController.list_suppliers()

        self.var_name = ctk.StringVar(value=self.initial.get("name",""))
        self.var_desc = ctk.StringVar(value=self.initial.get("description",""))
        self.var_cost = ctk.StringVar(value=str(self.initial.get("cost_price",0)))
        self.var_min = ctk.StringVar(value=str(self.initial.get("min_stock",0)))

        self.cat_values = ["(Sem)"] + [f'{c["id"]} - {c["name"]}' for c in cats]
        self.sup_values = ["(Sem)"] + [f'{s["id"]} - {s["name"]}' for s in sups]

        def find_choice(values, key_id):
            if not key_id:
                return "(Sem)"
            for v in values:
                if v.startswith(f"{key_id} -"):
                    return v
            return "(Sem)"

        self.var_cat = ctk.StringVar(value=find_choice(self.cat_values, self.initial.get("category_id")))
        self.var_sup = ctk.StringVar(value=find_choice(self.sup_values, self.initial.get("supplier_id")))

        frm = ctk.CTkFrame(self, corner_radius=14)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        def row(label, widget, r):
            ctk.CTkLabel(frm, text=label).grid(row=r, column=0, sticky="w", padx=12, pady=10)
            widget.grid(row=r, column=1, sticky="ew", padx=12, pady=10)
            frm.grid_columnconfigure(1, weight=1)

        row("Nome *", ctk.CTkEntry(frm, textvariable=self.var_name), 0)
        row("Descrição", ctk.CTkEntry(frm, textvariable=self.var_desc), 1)
        row("Categoria", ctk.CTkOptionMenu(frm, variable=self.var_cat, values=self.cat_values), 2)
        row("Fornecedor", ctk.CTkOptionMenu(frm, variable=self.var_sup, values=self.sup_values), 3)
        row("Custo (uso interno)", ctk.CTkEntry(frm, textvariable=self.var_cost), 4)
        row("Estoque mínimo (unid.)", ctk.CTkEntry(frm, textvariable=self.var_min), 5)

        actions = ctk.CTkFrame(frm, fg_color="transparent")
        actions.grid(row=6, column=0, columnspan=2, sticky="e", padx=12, pady=12)
        ctk.CTkButton(actions, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", command=self.destroy).pack(side="right", padx=8)
        ctk.CTkButton(actions, text="Salvar", command=self._save).pack(side="right")

    def _parse_id(self, value: str):
        v = (value or "").strip()
        if v == "(Sem)" or not v:
            return None
        try:
            return int(v.split("-")[0].strip())
        except Exception:
            return None

    def _save(self):
        try:
            name = self.var_name.get().strip()
            if not name:
                raise ValueError("Nome é obrigatório.")
            data = {
                "name": name,
                "description": self.var_desc.get().strip(),
                "category_id": self._parse_id(self.var_cat.get()),
                "supplier_id": self._parse_id(self.var_sup.get()),
                "cost_price": float((self.var_cost.get() or "0").replace(",", ".")),
                "min_stock": int(self.var_min.get() or 0),
            }
            if data["min_stock"] < 0:
                raise ValueError("Estoque mínimo não pode ser negativo.")
            if data["cost_price"] < 0:
                raise ValueError("Custo não pode ser negativo.")
            self.on_save(data)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Produto", str(e))
