import tkinter as tk
from tkinter import ttk
import re

from models.contracts_model import ContractsModel
from models.utils.afs_parser import CONTRACT_FIELDS

BTN_COLOR = "#0F20B4"
DND_BG_COLOR = "#f0f0f0"

class ContractsPageTwo(tk.Frame):
    def __init__(self, root, controller, model: ContractsModel, bg, finalize_handler, reset_ui_handler):
        super().__init__(root)
        self.root = root
        self.bg_color = bg
        self.configure(bg=bg)
        self.model = model
        self.controller = controller

        # parsed/known values
        self.data = dict(self.model.afs_data or {})

        # keep references to vars so they don't get GC'd
        self.vars: dict[str, tk.StringVar] = {}
        self.vars_by_key = {} 
        # self.entries_by_key = {}

        self.spinner_path = self.model.resource_path("assets/spinner.gif")
        self.contract_fields = CONTRACT_FIELDS  # list of display labels
        if not "Fee Amount" in self.contract_fields: self.contract_fields.insert(3, "Fee Amount")
        if not "Interest Rate" in self.contract_fields: self.contract_fields.insert(3, "Interest Rate")
        if not "Frequency" in self.contract_fields: self.contract_fields.insert(3, "Frequency")

        # ---------- fields ----------
        self.fields = tk.Frame(self, bg=bg)
        self.fields.grid_columnconfigure(0, weight=1)
        self.fields.grid_columnconfigure(1, weight=2)

        row = 0
        for label in self.contract_fields:
            # normalize label -> key used in dict
            src_key = label.replace(":", "").strip()
            key_norm = src_key.lower()
            initial = self.data.get(src_key, "")
            sv = tk.StringVar(value=initial)

            # live update back into self.model.afs_data
            def make_callback(key, var):           
                return lambda *args: self.model.afs_data.__setitem__(key, var.get())
            sv.trace_add("write", make_callback(src_key, sv))

            block = LabeledEntry(self.fields, label=label, textvariable=sv, width=40)
            block.grid(row=row, column=0, sticky="ew", padx=6, pady=4)
            row += 1

            self.vars[label] = sv
            self.vars_by_key[key_norm] = sv
            # self.entries_by_key[key_norm] = block.entry

        self._setup_fee_bindings()
        # self._setup_money_field_formatters()

        self.fields.pack(pady=20, fill="x")

        # ---------- buttons ----------
        self.contract_button_frame = tk.Frame(self, bg=bg)
        self.contract_button_frame.pack()

        self.generate_button = tk.Button(
            self.contract_button_frame,
            text="Generate Contracts",
            font=("Segoe UI", 14),
            command=lambda: self._on_generate(finalize_handler),
            bg="#8752CE",
            fg="white",
            height=1
        )
        self.generate_button.grid(row=0, column=0, sticky="ew", padx=6, pady=4)

        self.clear_files_btn = tk.Button(
            self.contract_button_frame,
            text="Cancel",
            font=("Segoe UI", 14),
            command=lambda: [self.model.clean_uploads(), reset_ui_handler()],
            bg="#545151",
            fg="white",
            width=10,
            height=1
        )
        self.clear_files_btn.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

    def _on_generate(self, finalize_handler):
        """Pull current values from the form back into model.afs_data, then call finalize."""
        # push values back (strip the ":" for keys)
        for label, sv in self.vars.items():
            key = label.replace(":", "").strip()
            self.model.afs_data[key] = sv.get()
        finalize_handler()

    def _setup_fee_bindings(self):
        # Accept multiple label/key variants
        PCT_KEYS = ["fee", "percent fee", "fee %"]
        AMT_KEYS = ["fee amount", "total fee"]
        LOC_KEYS = ["line of credit", "loc amount", "of the line of credit amount of"]
        IFA_KEYS = ["initial funding"]

        def _find_var(candidates):
            for cand in candidates:
                v = self.vars_by_key.get(cand.lower())
                if v:
                    return v
            # fallback: substring search over known keys
            for k, v in self.vars_by_key.items():
                if any(cand in k for cand in candidates):
                    return v
            return None

        pct_var = _find_var(PCT_KEYS)
        amt_var = _find_var(AMT_KEYS)
        loc_var = _find_var(LOC_KEYS)
        ifa_var = _find_var(IFA_KEYS)

        if not (pct_var and amt_var and loc_var and ifa_var):
            return
        
        self._sync_guard = False

        def format_initial_funding(*_):
            if self._sync_guard:
                return
            self._sync_guard = True
            try:
                ifa = self._money_to_float(ifa_var.get())
                if ifa is not None:
                    ifa_var.set(self._fmt_money(ifa))
            finally:
                self._sync_guard = False

        def recompute_from_percent(*_):
            if self._sync_guard:
                return
            self._sync_guard = True
            try:
                loc = self._money_to_float(loc_var.get())
                pct = self._percent_to_float(pct_var.get())
                if loc is not None and pct is not None:
                    fee_amount = loc * (pct / 100.0)
                    amt_var.set(self._fmt_money(fee_amount))
                    # ensure percent displays with %
                    loc_var.set(self._fmt_money(loc))
                    pct_var.set(self._fmt_percent(pct))
            finally:
                self._sync_guard = False

        def recompute_from_amount(*_):
            if self._sync_guard:
                return
            self._sync_guard = True
            try:
                loc = self._money_to_float(loc_var.get())
                amt = self._money_to_float(amt_var.get())
                if loc not in (None, 0) and amt is not None:
                    pct = (amt / loc) * 100.0
                    pct_var.set(self._fmt_percent(pct))
                    amt_var.set(self._fmt_money(amt))
            finally:
                self._sync_guard = False

        def recompute_when_loc_changes(*_):
            # If LOC changes, prefer recomputing amount from the existing percent
            recompute_from_percent()

        # Initial normalization/compute once on load
        recompute_from_percent()

        # Wire traces for live updates
        pct_var.trace_add("write", recompute_from_percent)
        amt_var.trace_add("write", recompute_from_amount)
        loc_var.trace_add("write", recompute_when_loc_changes)
        ifa_var.trace_add("write", format_initial_funding)

    def _money_to_float(self, s: str | None) -> float | None:
        if not s:
            return None
        # drop anything that isn't digit or dot/comma, then normalize commas
        cleaned = re.sub(r"[^0-9.,-]", "", s)
        # if both comma and dot appear, assume comma = thousands
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(",", "")
        else:
            # if only comma appears, treat it as decimal
            cleaned = cleaned.replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
        
    def _percent_to_float(self, s: str) -> float | None:
        if s is None:
            return None
        s = s.strip()
        if not s:
            return None
        s = s.replace('%', '').strip()
        try:
            return float(s) if s else None
        except ValueError:
            return None
    
    def _fmt_money(self, x: float | None) -> str:
        if x is None:
            return ""
        return f"{x:,.2f}"

    def _fmt_percent(self, x: float | None) -> str:
        if x is None:
            return ""
        return f"{x:.1f}%"
    

class LabeledEntry(ttk.Frame):
    def __init__(self, parent, label, textvariable=None, width=32, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = ttk.Label(self, text=label)
        self.label.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.entry = ttk.Entry(self, textvariable=textvariable, width=width)
        self.entry.grid(row=0, column=1, sticky="ew")
        self.grid_columnconfigure(1, weight=1)

