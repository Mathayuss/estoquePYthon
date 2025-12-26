import customtkinter as ctk
from tkinter import ttk

from app.controllers import CatalogController

class InventorySummaryPage(ctk.CTkFrame):
    """Resumo por Modelo/Produto (quantidades e alertas)."""

    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Resumo por Modelo", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))

        cols = ("category", "product", "in_stock", "out", "maintenance", "disposed", "total", "min_qty", "low")
        table_frame = ctk.CTkFrame(self, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ysb = ttk.Scrollbar(table_frame, orient="vertical")
        ysb.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.configure(yscrollcommand=ysb.set)
        ysb.configure(command=self.tree.yview)

        self.tree.pack(side="left", fill="both", expand=True)

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
            "category": 170,
            "product": 320,
            "in_stock": 90,
            "out": 90,
            "maintenance": 90,
            "disposed": 80,
            "total": 70,
            "min_qty": 70,
            "low": 70,
        }
        for c in cols:
            self.tree.heading(c, text=heads[c])
            self.tree.column(c, width=widths.get(c, 100), anchor="w")

        self.tree.tag_configure("low", background="#fee2e2")

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        rows = CatalogController.list_product_stock_summary()
        for r in rows:
            low = "SIM" if r["low"] else ""
            tags = ("low",) if r["low"] else ()
            self.tree.insert(
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
