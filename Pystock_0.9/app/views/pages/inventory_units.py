import customtkinter as ctk
from tkinter import ttk

from app.controllers import AssetController, LocationController

class InventoryUnitsPage(ctk.CTkFrame):
    """Lista individual de equipamentos (somente visualização)."""

    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Equipamentos", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))

        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", pady=(0, 10))

        self.search = ctk.CTkEntry(top, placeholder_text="Buscar por patrimônio, serial ou QR...")
        self.search.pack(side="left", fill="x", expand=True, padx=12, pady=12)
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())

        self.var_status = ctk.StringVar(value="ALL")
        self.cbo_status = ctk.CTkOptionMenu(
            top,
            variable=self.var_status,
            values=["ALL", "IN_STOCK", "OUT", "MAINTENANCE", "DISPOSED"],
            command=lambda _v: self.refresh()
        )
        self.cbo_status.pack(side="left", padx=(0, 12), pady=12)


        self.locations = LocationController.list_locations(active_only=True)
        loc_names = ["ALL"] + [l["name"] for l in self.locations]
        self.var_location = ctk.StringVar(value="ALL")
        self.cbo_location = ctk.CTkOptionMenu(
            top,
            variable=self.var_location,
            values=loc_names,
            command=lambda _v: self.refresh()
        )
        self.cbo_location.pack(side="left", padx=(0, 12), pady=12)


        cols = ("asset_tag", "product", "category", "location", "status", "serial_number", "notes")
        table_frame = ctk.CTkFrame(self, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ysb = ttk.Scrollbar(table_frame, orient="vertical")
        ysb.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.configure(yscrollcommand=ysb.set)
        ysb.configure(command=self.tree.yview)

        self.tree.pack(side="left", fill="both", expand=True)

        heads = {
            "asset_tag": "Patrimônio",
            "product": "Produto/Modelo",
            "category": "Categoria",
            "location": "Unidade",
            "status": "Status",
            "serial_number": "Serial",
            "notes": "Observações",
        }
        widths = {"asset_tag": 140, "product": 250, "category": 160, "location": 160, "status": 110, "serial_number": 170, "notes": 260}
        for c in cols:
            self.tree.heading(c, text=heads[c])
            self.tree.column(c, width=widths.get(c, 120), anchor="w")

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        location_id = None
        loc_name = (self.var_location.get() or "").strip()
        if loc_name and loc_name != "ALL":
            for l in self.locations:
                if l["name"] == loc_name:
                    location_id = int(l["id"])
                    break

        rows = AssetController.list_assets(search=self.search.get().strip(), status=self.var_status.get(), location_id=location_id)
        for r in rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    r["asset_tag"],
                    r.get("product") or "",
                    r.get("category") or "",
                    r.get("location") or "",
                    r["status"],
                    r.get("serial_number") or "",
                    r.get("notes") or ""
                )
            )
