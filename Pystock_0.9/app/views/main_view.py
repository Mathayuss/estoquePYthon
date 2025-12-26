import customtkinter as ctk
from tkinter import messagebox

from app.views.pages.dashboard import DashboardPage
from app.views.pages.movement import MovementPage
from app.views.pages.inventory import InventoryPage
from app.views.pages.reports import ReportsPage
from app.views.pages.admin_page import AdminPage


class MainView(ctk.CTkFrame):
    def __init__(self, master, user: dict, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=235, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")

        self.sidebar.grid_rowconfigure(99, weight=1)

        ctk.CTkLabel(self.sidebar, text="PyStock Ativos", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(16, 6), sticky="w"
        )
        ctk.CTkLabel(self.sidebar, text=f"Usuário: {user['username']} ({user['role']})", text_color="#6b7280").grid(
            row=1, column=0, padx=16, pady=(0, 12), sticky="w"
        )

        self.btns = {}
        self.pages = {}

        # Menu curto (Modelo 1)
        self._add_nav("dashboard", "Dashboard", row=2)
        self._add_nav("movement", "Movimentação", row=3)
        self._add_nav("inventory", "Inventário (Ativos)", row=4)
        self._add_nav("reports", "Relatórios", row=5)

        if user["role"] == "admin":
            self._add_nav("admin", "Administração", row=6)

        ctk.CTkButton(
            self.sidebar,
            text="Sair",
            fg_color="#111827",
            hover_color="#0b1220",
            command=self._logout
        ).grid(row=99, column=0, padx=16, pady=16, sticky="ew")

        # Pages
        self.pages["dashboard"] = DashboardPage(self.content)
        self.pages["movement"] = MovementPage(self.content, current_user=self.user)
        self.pages["inventory"] = InventoryPage(self.content, current_user=self.user)
        self.pages["reports"] = ReportsPage(self.content)

        if user["role"] == "admin":
            self.pages["admin"] = AdminPage(self.content, current_user=self.user)

        self.show_page("dashboard")

    def _add_nav(self, key, text, row: int):
        btn = ctk.CTkButton(self.sidebar, text=text, anchor="w", command=lambda k=key: self.show_page(k))
        btn.grid(row=row, column=0, padx=16, pady=6, sticky="ew")
        self.btns[key] = btn

    def show_page(self, key):
        for p in self.pages.values():
            p.pack_forget()

        page = self.pages[key]
        page.pack(fill="both", expand=True, padx=16, pady=16)

        if hasattr(page, "refresh"):
            page.refresh()

        if hasattr(page, "focus_default"):
            page.focus_default()

    def _logout(self):
        if messagebox.askyesno("Sair", "Deseja sair do sistema?"):
            self.on_logout()
