import customtkinter as ctk

from app.views.pages.reasons import ReasonsPage
from app.views.pages.users import UsersPage

class AdminPage(ctk.CTkFrame):
    def __init__(self, master, current_user: dict):
        super().__init__(master)
        self.current_user = current_user

        header = ctk.CTkFrame(self, corner_radius=12)
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="Administração", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=12, pady=12)

        self.tab = ctk.StringVar(value="Motivos de Saída")
        self.seg = ctk.CTkSegmentedButton(
            header,
            values=["Motivos de Saída", "Usuários"],
            variable=self.tab,
            command=lambda _v: self._show_tab()
        )
        self.seg.pack(side="right", padx=12, pady=12)

        self.container = ctk.CTkFrame(self, corner_radius=12)
        self.container.pack(fill="both", expand=True)

        self.pages = {
            "Motivos de Saída": ReasonsPage(self.container),
            "Usuários": UsersPage(self.container),
        }

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
