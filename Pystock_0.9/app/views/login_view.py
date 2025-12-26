import customtkinter as ctk
from tkinter import messagebox

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login):
        super().__init__(master)
        self.on_login = on_login

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=16)
        card.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="PyStock Ativos", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, pady=(20, 6))
        ctk.CTkLabel(card, text="Acesso ao sistema", text_color="#6b7280").grid(row=1, column=0, pady=(0, 18))

        self.username = ctk.CTkEntry(card, width=320, placeholder_text="Usuário")
        self.username.grid(row=2, column=0, pady=8, padx=24)

        self.password = ctk.CTkEntry(card, width=320, placeholder_text="Senha", show="*")
        self.password.grid(row=3, column=0, pady=8, padx=24)

        btn = ctk.CTkButton(card, text="Entrar", width=320, command=self._login)
        btn.grid(row=4, column=0, pady=(16, 10), padx=24)

        hint = "Primeiro acesso: admin / admin123"
        ctk.CTkLabel(card, text=hint, text_color="#6b7280").grid(row=5, column=0, pady=(6, 20))

        self.username.focus_set()
        self.username.bind("<Return>", lambda _e: self._login())
        self.password.bind("<Return>", lambda _e: self._login())

    def _login(self):
        try:
            self.on_login(self.username.get(), self.password.get())
        except Exception as e:
            messagebox.showerror("Login", str(e))
