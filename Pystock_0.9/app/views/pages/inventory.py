import customtkinter as ctk

from app.views.pages.inventory_summary import InventorySummaryPage
from app.views.pages.inventory_units import InventoryUnitsPage
from app.views.pages.inventory_locations import InventoryLocationsPage
from app.views.pages.asset_register import AssetRegisterPage
from app.views.pages.products import ProductsPage
from app.views.pages.categories import CategoriesPage
from app.views.pages.suppliers import SuppliersPage

class InventoryPage(ctk.CTkFrame):
    def __init__(self, master, current_user: dict):
        super().__init__(master)
        self.current_user = current_user

        header = ctk.CTkFrame(self, corner_radius=12)
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="Inventário (Ativos)", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=12, pady=12)

        # Tabs variam conforme perfil
        base_tabs = ["Resumo por Modelo", "Equipamentos", "Unidades (Locais)"]
        admin_tabs = ["Cadastro", "Modelos", "Categorias", "Fornecedores"]
        tabs = base_tabs + (admin_tabs if current_user.get("role") == "admin" else [])

        self.tab = ctk.StringVar(value=tabs[0])
        self.seg = ctk.CTkSegmentedButton(header, values=tabs, variable=self.tab, command=lambda _v: self._show_tab())
        self.seg.pack(side="right", padx=12, pady=12)

        self.container = ctk.CTkFrame(self, corner_radius=12)
        self.container.pack(fill="both", expand=True)

        self.pages = {
            "Resumo por Modelo": InventorySummaryPage(self.container),
            "Equipamentos": InventoryUnitsPage(self.container),
            "Unidades (Locais)": InventoryLocationsPage(self.container, current_user=current_user),
        }

        if current_user.get("role") == "admin":
            self.pages["Cadastro"] = AssetRegisterPage(self.container)
            self.pages["Modelos"] = ProductsPage(self.container)
            self.pages["Categorias"] = CategoriesPage(self.container)
            self.pages["Fornecedores"] = SuppliersPage(self.container)

        self._show_tab()

    def _show_tab(self):
        for p in self.pages.values():
            p.pack_forget()

        page = self.pages[self.tab.get()]
        page.pack(fill="both", expand=True, padx=16, pady=16)

        if hasattr(page, "refresh"):
            page.refresh()

    def refresh(self):
        self._show_tab()
