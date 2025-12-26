import customtkinter as ctk
from tkinter import ttk, messagebox
from app.controllers import AuthController

class UsersPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(top, text="Novo Usuário", command=self.new_user).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(top, text="Resetar Senha", command=self.reset_pwd).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Alterar Role", command=self.set_role).pack(side="left", padx=6, pady=10)

        self.table = ttk.Treeview(self, columns=("id","username","role","created"), show="headings", height=18)
        for col, txt, w in [("id","ID",70),("username","Usuário",220),("role","Role",120),("created","Criado em",180)]:
            self.table.heading(col, text=txt)
            self.table.column(col, width=w, anchor="w")
        self.table.column("id", anchor="center")
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        for i in self.table.get_children():
            self.table.delete(i)
        for u in AuthController.list_users():
            self.table.insert("", "end", values=(u["id"], u["username"], u["role"], u["created_at"].strftime("%Y-%m-%d %H:%M")))

    def _selected_id(self):
        sel = self.table.selection()
        if not sel:
            return None
        return int(self.table.item(sel[0], "values")[0])

    def new_user(self):
        UserForm(self, "Novo Usuário", on_save=lambda d: (AuthController.create_user(**d), self.refresh()))

    def reset_pwd(self):
        uid = self._selected_id()
        if not uid:
            messagebox.showwarning("Usuários", "Selecione um usuário.")
            return
        PasswordForm(self, "Resetar Senha", on_save=lambda pwd: (AuthController.reset_password(uid, pwd), self.refresh()))

    def set_role(self):
        uid = self._selected_id()
        if not uid:
            messagebox.showwarning("Usuários", "Selecione um usuário.")
            return
        RoleForm(self, "Alterar Role", on_save=lambda role: (AuthController.set_role(uid, role), self.refresh()))

class UserForm(ctk.CTkToplevel):
    def __init__(self, master, title, on_save):
        super().__init__(master)
        self.title(title)
        self.geometry("520x360")
        self.resizable(False, False)
        self.grab_set()
        self.on_save = on_save

        self.var_username = ctk.StringVar()
        self.var_password = ctk.StringVar()
        self.var_role = ctk.StringVar(value="operator")

        frm = ctk.CTkFrame(self, corner_radius=14)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frm, text="Usuário").pack(anchor="w", padx=12, pady=(12, 4))
        ctk.CTkEntry(frm, textvariable=self.var_username).pack(fill="x", padx=12)

        ctk.CTkLabel(frm, text="Senha").pack(anchor="w", padx=12, pady=(12, 4))
        ctk.CTkEntry(frm, textvariable=self.var_password, show="*").pack(fill="x", padx=12)

        ctk.CTkLabel(frm, text="Role").pack(anchor="w", padx=12, pady=(12, 4))
        ctk.CTkOptionMenu(frm, variable=self.var_role, values=["admin", "operator"]).pack(fill="x", padx=12)

        actions = ctk.CTkFrame(frm, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=14)
        ctk.CTkButton(actions, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", command=self.destroy).pack(side="right", padx=8)
        ctk.CTkButton(actions, text="Salvar", command=self._save).pack(side="right")

    def _save(self):
        try:
            data = {"username": self.var_username.get().strip(), "password": self.var_password.get(), "role": self.var_role.get().strip()}
            self.on_save(data)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Usuário", str(e))

class PasswordForm(ctk.CTkToplevel):
    def __init__(self, master, title, on_save):
        super().__init__(master)
        self.title(title)
        self.geometry("520x260")
        self.resizable(False, False)
        self.grab_set()
        self.on_save = on_save

        self.var_pwd = ctk.StringVar()

        frm = ctk.CTkFrame(self, corner_radius=14)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frm, text="Nova senha").pack(anchor="w", padx=12, pady=(12, 4))
        ctk.CTkEntry(frm, textvariable=self.var_pwd, show="*").pack(fill="x", padx=12)

        actions = ctk.CTkFrame(frm, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=14)
        ctk.CTkButton(actions, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", command=self.destroy).pack(side="right", padx=8)
        ctk.CTkButton(actions, text="Salvar", command=self._save).pack(side="right")

    def _save(self):
        try:
            self.on_save(self.var_pwd.get())
            self.destroy()
        except Exception as e:
            messagebox.showerror("Senha", str(e))

class RoleForm(ctk.CTkToplevel):
    def __init__(self, master, title, on_save):
        super().__init__(master)
        self.title(title)
        self.geometry("520x260")
        self.resizable(False, False)
        self.grab_set()
        self.on_save = on_save

        self.var_role = ctk.StringVar(value="operator")

        frm = ctk.CTkFrame(self, corner_radius=14)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frm, text="Role").pack(anchor="w", padx=12, pady=(12, 4))
        ctk.CTkOptionMenu(frm, variable=self.var_role, values=["admin", "operator"]).pack(fill="x", padx=12)

        actions = ctk.CTkFrame(frm, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=14)
        ctk.CTkButton(actions, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", command=self.destroy).pack(side="right", padx=8)
        ctk.CTkButton(actions, text="Salvar", command=self._save).pack(side="right")

    def _save(self):
        try:
            self.on_save(self.var_role.get().strip())
            self.destroy()
        except Exception as e:
            messagebox.showerror("Role", str(e))
