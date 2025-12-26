import customtkinter as ctk
from tkinter import ttk, messagebox

from app.controllers import AssetController, CatalogController
from app.qr_utils import generate_asset_qr_png
from app.paths import get_labels_dir

class AssetRegisterPage(ctk.CTkFrame):
    """Cadastro/CRUD de Ativos (Unidades) - somente Admin."""

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkFrame(self, corner_radius=12)
        title.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(title, text="Cadastro de Ativos (Unidades)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=12, pady=(12, 2))
        ctk.CTkLabel(
            title,
            text="Patrimônio: deixe em branco para gerar automaticamente (único).",
            text_color="#6b7280"
        ).pack(anchor="w", padx=12, pady=(0, 12))

        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", pady=(0, 10))

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

        ctk.CTkButton(top, text="Novo", command=self.new_asset).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Editar", command=self.edit_asset).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Criar em lote", command=self.bulk_create).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Gerar QR (PNG)", command=self.gen_qr).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Excluir", fg_color="#b91c1c", hover_color="#991b1b", command=self.delete_asset).pack(side="left", padx=6, pady=10)

        cols = ("id", "asset_tag", "product", "category", "status", "serial_number", "qr_code")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.heading("id", text="ID")
        self.tree.heading("asset_tag", text="Patrimônio")
        self.tree.heading("product", text="Produto/Modelo")
        self.tree.heading("category", text="Categoria")
        self.tree.heading("status", text="Status")
        self.tree.heading("serial_number", text="Serial")
        self.tree.heading("qr_code", text="QR (UUID)")

        self.tree.column("id", width=60, anchor="w")
        self.tree.column("asset_tag", width=120, anchor="w")
        self.tree.column("product", width=220, anchor="w")
        self.tree.column("category", width=140, anchor="w")
        self.tree.column("status", width=120, anchor="w")
        self.tree.column("serial_number", width=160, anchor="w")
        self.tree.column("qr_code", width=240, anchor="w")

        self._rows = []
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        self._rows = AssetController.list_assets(
            search=self.search.get().strip(),
            status=self.var_status.get()
        )

        for r in self._rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    r["id"],
                    r["asset_tag"],
                    r["product"],
                    r["category"],
                    r["status"],
                    r.get("serial_number") or "",
                    r["qr_code"],
                )
            )

    def _selected(self) -> dict | None:
        cur = self.tree.selection()
        if not cur:
            return None
        values = self.tree.item(cur[0], "values")
        if not values:
            return None
        asset_id = int(values[0])
        for r in self._rows:
            if int(r["id"]) == asset_id:
                return r
        return None

    # ------------------ Actions ------------------

    def new_asset(self):
        AssetForm(self, title="Novo Ativo", on_save=lambda: self.refresh(), mode="new")

    def bulk_create(self):
        AssetForm(self, title="Criar Ativos em Lote", on_save=lambda: self.refresh(), mode="bulk")

    def edit_asset(self):
        a = self._selected()
        if not a:
            messagebox.showwarning("Editar", "Selecione um ativo.")
            return
        AssetForm(self, title="Editar Ativo", on_save=lambda: self.refresh(), mode="edit", asset=a)

    def delete_asset(self):
        a = self._selected()
        if not a:
            messagebox.showwarning("Excluir", "Selecione um ativo.")
            return
        if not messagebox.askyesno("Excluir", f"Excluir o ativo {a['asset_tag']}?"):
            return
        try:
            AssetController.delete_asset(int(a["id"]))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Excluir", str(e))

    def gen_qr(self):
        a = self._selected()
        if not a:
            messagebox.showwarning("QR", "Selecione um ativo.")
            return
        try:
            out_dir = get_labels_dir()
            path = generate_asset_qr_png(a["qr_code"], a["asset_tag"], str(out_dir))
            messagebox.showinfo("QR gerado", f"Arquivo gerado em:\n{path}")
        except Exception as e:
            messagebox.showerror("QR", str(e))


class AssetForm(ctk.CTkToplevel):
    def __init__(self, master, title: str, on_save, mode: str, asset: dict | None = None):
        super().__init__(master)
        self.title(title)
        self.geometry("680x320")
        self.resizable(False, False)
        self.on_save = on_save
        self.mode = mode
        self.asset = asset or {}

        self.products = CatalogController.list_products()
        if not self.products:
            messagebox.showerror("Cadastro", "Cadastre primeiro um Produto/Modelo.")
            self.destroy()
            return

        # layout
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        # Product
        ctk.CTkLabel(frm, text="Produto/Modelo").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 4))
        self.var_product = ctk.StringVar(value=self._default_product_name())
        self.cbo_product = ctk.CTkOptionMenu(frm, variable=self.var_product, values=[p["name"] for p in self.products])
        self.cbo_product.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Patrimony
        ctk.CTkLabel(frm, text="Patrimônio (deixe em branco para automático)").grid(row=0, column=1, sticky="w", padx=10, pady=(10, 4))
        self.ent_tag = ctk.CTkEntry(frm, placeholder_text="AUTO")
        self.ent_tag.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))

        # Serial
        ctk.CTkLabel(frm, text="Serial (opcional)").grid(row=2, column=0, sticky="w", padx=10, pady=(0, 4))
        self.ent_serial = ctk.CTkEntry(frm, placeholder_text="Ex.: SN123456")
        self.ent_serial.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Notes
        ctk.CTkLabel(frm, text="Observações (opcional)").grid(row=2, column=1, sticky="w", padx=10, pady=(0, 4))
        self.ent_notes = ctk.CTkEntry(frm, placeholder_text="Ex.: carregador incluso, etiqueta nova...")
        self.ent_notes.grid(row=3, column=1, sticky="ew", padx=10, pady=(0, 10))

        # Quantity (bulk)
        self.ent_qty = None
        if self.mode == "bulk":
            ctk.CTkLabel(frm, text="Quantidade").grid(row=4, column=0, sticky="w", padx=10, pady=(0, 4))
            self.ent_qty = ctk.CTkEntry(frm, placeholder_text="Ex.: 10")
            self.ent_qty.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 10))
            ctk.CTkLabel(frm, text="Obs.: o Serial não é aplicado em lote.").grid(row=5, column=1, sticky="w", padx=10, pady=(0, 10))

        # Status (edit only)
        self.var_status = ctk.StringVar(value=self.asset.get("status", "IN_STOCK"))
        if self.mode == "edit":
            ctk.CTkLabel(frm, text="Status").grid(row=4, column=0, sticky="w", padx=10, pady=(0, 4))
            self.cbo_status = ctk.CTkOptionMenu(frm, variable=self.var_status, values=["IN_STOCK", "OUT", "MAINTENANCE", "DISPOSED"])
            self.cbo_status.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Buttons
        btns = ctk.CTkFrame(frm, corner_radius=0, fg_color="transparent")
        btns.grid(row=6, column=0, columnspan=2, sticky="e", padx=10, pady=10)

        ctk.CTkButton(btns, text="Cancelar", fg_color="#111827", hover_color="#0b1220", command=self.destroy).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Salvar", command=self._save).pack(side="right", padx=6)

        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)

        self._prefill()

        # focus
        self.after(150, lambda: self.ent_tag.focus_set())

    def _default_product_name(self) -> str:
        if self.asset.get("product"):
            return self.asset["product"]
        return self.products[0]["name"]

    def _get_product_id(self) -> int:
        name = (self.var_product.get() or "").strip()
        for p in self.products:
            if p["name"] == name:
                return int(p["id"])
        return int(self.products[0]["id"])

    def _prefill(self):
        if self.mode == "edit":
            self.ent_tag.insert(0, self.asset.get("asset_tag", ""))
            self.ent_serial.insert(0, self.asset.get("serial_number") or "")
            self.ent_notes.insert(0, self.asset.get("notes") or "")
        else:
            # new/bulk
            self.ent_tag.delete(0, "end")

    def _save(self):
        try:
            pid = self._get_product_id()
            tag = (self.ent_tag.get() or "").strip() or None
            serial = (self.ent_serial.get() or "").strip() or None
            notes = (self.ent_notes.get() or "").strip() or None

            if self.mode == "new":
                created = AssetController.create_asset(pid, tag, serial, notes)
                self.on_save()
                messagebox.showinfo("Cadastro", f"Criado: {created['asset_tag']}")
                self.destroy()
                return

            if self.mode == "bulk":
                qty = int((self.ent_qty.get() or "0").strip())
                if qty <= 0:
                    raise ValueError("Informe uma quantidade válida.")
                if tag:
                    raise ValueError("Para criação em lote, deixe o patrimônio em branco (automático).")
                created = AssetController.create_assets_bulk(pid, qty, notes=notes)
                self.on_save()
                if created:
                    messagebox.showinfo("Cadastro", f"Criados {len(created)} ativos. Ex.: {created[0]['asset_tag']} ... {created[-1]['asset_tag']}")
                else:
                    messagebox.showinfo("Cadastro", "Nenhum ativo criado.")
                self.destroy()
                return

            if self.mode == "edit":
                if not self.asset.get("id"):
                    raise ValueError("Ativo inválido.")
                status = self.var_status.get()
                AssetController.update_asset(
                    asset_id=int(self.asset["id"]),
                    product_id=pid,
                    asset_tag=tag or "",
                    serial=serial,
                    notes=notes,
                    status=status
                )
                self.on_save()
                messagebox.showinfo("Cadastro", "Alterações salvas.")
                self.destroy()
                return

        except Exception as e:
            messagebox.showerror("Cadastro", str(e))
