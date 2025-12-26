import customtkinter as ctk
from app.controllers import AuthController
from app.views.login_view import LoginView
from app.views.main_view import MainView

class AppShell(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PyStock Ativos — Controle de Estoque (QR)")
        self.geometry("1240x760")
        self.minsize(1120, 680)

        self.current_user = None

        self._container = ctk.CTkFrame(self)
        self._container.pack(fill="both", expand=True)

        self.show_login()

    def show_login(self):
        for w in self._container.winfo_children():
            w.destroy()
        view = LoginView(self._container, on_login=self._handle_login)
        view.pack(fill="both", expand=True)

    def _handle_login(self, username: str, password: str):
        user = AuthController.login(username, password)
        self.current_user = user
        self.show_main()

    def show_main(self):
        for w in self._container.winfo_children():
            w.destroy()
        view = MainView(self._container, user=self.current_user, on_logout=self._handle_logout)
        view.pack(fill="both", expand=True)

    def _handle_logout(self):
        self.current_user = None
        self.show_login()
