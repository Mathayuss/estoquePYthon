
import customtkinter as ctk
from tkinter import ttk, messagebox

from app.controllers import LocationController

class InventoryLocationsPage(ctk.CTkFrame):
    """Unidades (locais físicos) onde os equipamentos ficam distribuídos."""

    def __init__(self, master, current_user: dict):
        super().__init__(master)
        self.current_user = current_user

        ctk.CTkLabel(self, text="Unidades (Locais físicos)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))

        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", pady=(0, 10))

        self.search = ctk.CTkEntry(top, placeholder_text="Buscar unidade...")
        self.search.pack(side="left", fill="x", expand=True, padx=12, pady=12)
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())

        self.is_admin = (current_user.get("role") == "admin")

        if self.is_admin:
            ctk.CTkButton(top, text="Novo", command=self.new_location).pack(side="left", padx=(0, 8), pady=12)
            ctk.CTkButton(top, text="Editar", command=self.edit_location).pack(side="left", padx=(0, 8), pady=12)
            ctk.CTkButton(top, text="Excluir", fg_color="#b91c1c", hover_color="#991b1b", command=self.delete_location).pack(side="left", padx=(0, 12), pady=12)

        cols = ("id", "name", "is_active", "notes")
        table_frame = ctk.CTkFrame(self, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ysb = ttk.Scrollbar(table_frame, orient="vertical")
        ysb.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.configure(yscrollcommand=ysb.set)
        ysb.configure(command=self.tree.yview)

        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Unidade (Local)")
        self.tree.heading("is_active", text="Ativa")
        self.tree.heading("notes", text="Observações")

        self.tree.column("id", width=60, anchor="w")
        self.tree.column("name", width=260, anchor="w")
        self.tree.column("is_active", width=80, anchor="w")
        self.tree.column("notes", width=420, anchor="w")

        self._rows = []
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        rows = LocationController.list_locations(active_only=False)
        q = (self.search.get() or "").strip().lower()
        if q:
            rows = [r for r in rows if q in (r.get("name","").lower())]

        self._rows = rows
        for r in rows:
            self.tree.insert("", "end", values=(r["id"], r["name"], "SIM" if int(r["is_active"]) else "NÃO", r.get("notes") or ""))

    def _selected(self) -> dict | None:
        cur = self.tree.selection()
        if not cur:
            return None
        vals = self.tree.item(cur[0], "values")
        if not vals:
            return None
        rid = int(vals[0])
        for r in self._rows:
            if int(r["id"]) == rid:
                return r
        return None

    def new_location(self):
        LocationForm(self, title="Nova Unidade", on_save=self.refresh)

    def edit_location(self):
        r = self._selected()
        if not r:
            messagebox.showwarning("Editar", "Selecione uma unidade.")
            return
        LocationForm(self, title="Editar Unidade", on_save=self.refresh, location=r)

    def delete_location(self):
        r = self._selected()
        if not r:
            messagebox.showwarning("Excluir", "Selecione uma unidade.")
            return
        if not messagebox.askyesno("Excluir", f"Excluir a unidade '{r['name']}'?"):
            return
        try:
            LocationController.delete_location(int(r["id"]))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Excluir", str(e))


class LocationForm(ctk.CTkToplevel):
    def __init__(self, master, title: str, on_save, location: dict | None = None):
        super().__init__(master)
        self.title(title)
        self.geometry("560x220")
        self.resizable(False, False)
        self.on_save = on_save
        self.location = location or {}

        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frm, text="Nome").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 4))
        self.ent_name = ctk.CTkEntry(frm, placeholder_text="Ex.: Administração, Loja, TI, Matriz...")
        self.ent_name.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        ctk.CTkLabel(frm, text="Observações (opcional)").grid(row=2, column=0, sticky="w", padx=10, pady=(0, 4))
        self.ent_notes = ctk.CTkEntry(frm, placeholder_text="Ex.: 15º andar, Rack 01, Sala 03...")
        self.ent_notes.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        self.var_active = ctk.IntVar(value=int(self.location.get("is_active", 1)))
        ctk.CTkCheckBox(frm, text="Ativa", variable=self.var_active).grid(row=4, column=0, sticky="w", padx=10, pady=(0, 10))

        btns = ctk.CTkFrame(frm, fg_color="transparent")
        btns.grid(row=5, column=0, columnspan=2, sticky="e", padx=10, pady=10)
        ctk.CTkButton(btns, text="Cancelar", fg_color="#111827", hover_color="#0b1220", command=self.destroy).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Salvar", command=self._save).pack(side="right", padx=6)

        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)

        if self.location:
            self.ent_name.insert(0, self.location.get("name") or "")
            self.ent_notes.insert(0, self.location.get("notes") or "")

    def _save(self):
        try:
            name = (self.ent_name.get() or "").strip()
            notes = (self.ent_notes.get() or "").strip() or None
            active = int(self.var_active.get())

            if self.location and self.location.get("id"):
                LocationController.update_location(int(self.location["id"]), name, notes, active)
            else:
                LocationController.create_location(name, notes)

            self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Salvar", str(e))
