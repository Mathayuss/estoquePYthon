import customtkinter as ctk
from tkinter import ttk
from app.controllers import CatalogController

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.card_total = self._card("Total de Ativos", "0", 0)
        self.card_in = self._card("Ativos em Estoque", "0", 1)
        self.card_value = self._card("Valor do Estoque (R$ - custo)", "0,00", 2)

        ctk.CTkLabel(self, text="Modelos abaixo do estoque mínimo", font=ctk.CTkFont(size=14, weight="bold"))            .grid(row=1, column=0, columnspan=3, sticky="w", pady=(18, 10))

        self.table = ttk.Treeview(self, columns=("produto", "estoque", "minimo"), show="headings", height=10)
        self.table.heading("produto", text="Produto/Modelo")
        self.table.heading("estoque", text="Em estoque")
        self.table.heading("minimo", text="Mínimo")

        self.table.column("produto", width=560, anchor="w")
        self.table.column("estoque", width=130, anchor="center")
        self.table.column("minimo", width=130, anchor="center")
        self.table.grid(row=2, column=0, columnspan=3, sticky="nsew")

    def _card(self, title, value, col):
        frame = ctk.CTkFrame(self, corner_radius=14)
        frame.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(frame, text=title, text_color="#6b7280").pack(anchor="w", padx=14, pady=(12, 2))
        lbl = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=26, weight="bold"))
        lbl.pack(anchor="w", padx=14, pady=(0, 12))
        return lbl

    def refresh(self):
        m = CatalogController.get_dashboard_metrics()
        self.card_total.configure(text=str(m["total_assets"]))
        self.card_in.configure(text=str(m["assets_in_stock"]))
        self.card_value.configure(text=f"{m['total_value']:.2f}".replace(".", ","))

        for i in self.table.get_children():
            self.table.delete(i)
        for p in m["low_products"]:
            self.table.insert("", "end", values=(p["name"], p["stock"], p["min_stock"]))
