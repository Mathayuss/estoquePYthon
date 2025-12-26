import customtkinter as ctk
from tkinter import ttk

from app.controllers import AssetController, CatalogController

class AssetsPage(ctk.CTkFrame):
    """Visão de Ativos (Unidades): resumo por produto e lista individual (somente leitura)."""

    def __init__(self, master):
        super().__init__(master)

        header = ctk.CTkFrame(self, corner_radius=12)
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(header, text="Ativos (Visão Geral)", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=12, pady=12)

        self.mode = ctk.StringVar(value="Por Produto")
        self.seg = ctk.CTkSegmentedButton(
            header,
            values=["Por Produto", "Individual"],
            variable=self.mode,
            command=lambda _v: self._switch_mode(),
        )
        self.seg.pack(side="right", padx=12, pady=12)

        self.frm_product = ctk.CTkFrame(self, corner_radius=12)
        self.frm_individual = ctk.CTkFrame(self, corner_radius=12)

        self._build_product_view()
        self._build_individual_view()

        self._switch_mode()
        self.refresh()

    # ------------------ Views ------------------

    def _build_product_view(self):
        self.frm_product.pack(fill="both", expand=True)

        cols = ("category", "product", "in_stock", "out", "maintenance", "disposed", "total", "min_qty", "low")
        self.tree_prod = ttk.Treeview(self.frm_product, columns=cols, show="headings", height=18)
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)

        heads = {
            "category": "Categoria",
            "product": "Produto/Modelo",
            "in_stock": "Em estoque",
            "out": "Em uso (fora)",
            "maintenance": "Manutenção",
            "disposed": "Baixado",
            "total": "Total",
            "min_qty": "Mínimo",
            "low": "Alerta",
        }
        widths = {
            "category": 150,
            "product": 260,
            "in_stock": 90,
            "out": 90,
            "maintenance": 90,
            "disposed": 80,
            "total": 70,
            "min_qty": 70,
            "low": 70,
        }
        for c in cols:
            self.tree_prod.heading(c, text=heads[c])
            self.tree_prod.column(c, width=widths.get(c, 100), anchor="w")

        self.tree_prod.tag_configure("low", background="#fee2e2")

    def _build_individual_view(self):
        top = ctk.CTkFrame(self.frm_individual, corner_radius=12)
        top.pack(fill="x", padx=10, pady=(10, 0))

        self.search = ctk.CTkEntry(top, placeholder_text="Buscar por patrimônio, serial ou QR...")
        self.search.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())

        self.var_status = ctk.StringVar(value="ALL")
        self.cbo_status = ctk.CTkOptionMenu(
            top,
            variable=self.var_status,
            values=["ALL", "IN_STOCK", "OUT", "MAINTENANCE", "DISPOSED"],
            command=lambda _v: self.refresh()
        )
        self.cbo_status.pack(side="left", padx=6, pady=10)

        cols = ("asset_tag", "product", "category", "status", "serial_number", "notes")
        self.tree_ind = ttk.Treeview(self.frm_individual, columns=cols, show="headings", height=18)
        self.tree_ind.pack(fill="both", expand=True, padx=10, pady=10)

        heads = {
            "asset_tag": "Patrimônio",
            "product": "Produto/Modelo",
            "category": "Categoria",
            "status": "Status",
            "serial_number": "Serial",
            "notes": "Observações",
        }
        widths = {"asset_tag": 120, "product": 220, "category": 140, "status": 110, "serial_number": 160, "notes": 260}
        for c in cols:
            self.tree_ind.heading(c, text=heads[c])
            self.tree_ind.column(c, width=widths.get(c, 120), anchor="w")

    def _switch_mode(self):
        # remove both then add selected
        self.frm_product.pack_forget()
        self.frm_individual.pack_forget()

        if self.mode.get() == "Por Produto":
            self.frm_product.pack(fill="both", expand=True)
        else:
            self.frm_individual.pack(fill="both", expand=True)

    # ------------------ Data ------------------

    def refresh(self):
        mode = self.mode.get()

        if mode == "Por Produto":
            self._refresh_product()
        else:
            self._refresh_individual()

    def _refresh_product(self):
        for i in self.tree_prod.get_children():
            self.tree_prod.delete(i)

        rows = CatalogController.list_product_stock_summary()
        for r in rows:
            low = "SIM" if r["low"] else ""
            tags = ("low",) if r["low"] else ()
            self.tree_prod.insert(
                "",
                "end",
                values=(
                    r["category"],
                    r["product"],
                    r["in_stock"],
                    r["out"],
                    r["maintenance"],
                    r["disposed"],
                    r["total"],
                    r["min_qty"],
                    low
                ),
                tags=tags
            )

    def _refresh_individual(self):
        for i in self.tree_ind.get_children():
            self.tree_ind.delete(i)

        rows = AssetController.list_assets(search=self.search.get().strip(), status=self.var_status.get())
        for r in rows:
            self.tree_ind.insert(
                "",
                "end",
                values=(r["asset_tag"], r["product"], r["category"], r["status"], r.get("serial_number") or "", r.get("notes") or "")
            )
