import tkinter as tk
from tkinter import ttk
from tkinter import font

from models.contracts_model import ContractsModel
from views.contracts_view import COMBOBOX_VALUES

BTN_COLOR = "#0F20B4"
DND_BG_COLOR = "#f0f0f0"
CONTRACT_FIELDS_COLS = {
    'Merchant Name': 0, 'Tele No': 0, 'Fee': 2, 'Frequency': 2, 'Interest Rate': 2, 'EIN': 0, 
    "Merchant Address": 0, "City": 0, "State": 0, "Zip": 0, "Bank": 1, "Routing": 1, "Account": 1, 
    "Initial Funding": 2, "Line of Credit": 2, 'Fee Amount': 2, "Print Name": 0, "Date": 2
}
BUSINESS_INFO = [
    'Merchant Name', 'Tele No', 'EIN', "Merchant Address", "City", "State", "Zip", "Print Name"
]
BANK_INFO = [
    "Bank", "Routing", "Account"
]
CONTRACT_INFO = [
    'Fee', 'Frequency', 'Interest Rate', 'Fee Amount', "Line of Credit", "Initial Funding", "Date"
]
SCREEN_ONE_VARS = [
    "Fee", "Frequency", "Interest Rate"
]

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

        # keep references to vars and entries so they don't get GC'd
        self.vars: dict[str, tk.StringVar] = {}
        self.blocks: dict[str, LabeledEntry] = {}

        self.spinner_path = self.model.resource_path("assets/spinner.gif")
        self.contract_fields = CONTRACT_FIELDS_COLS.keys()  # list of display labels
       
        # ---------- fields ----------
        self.fields = tk.Frame(self, bg=bg)
        self.fields.grid_columnconfigure(0, weight=1)
        self.fields.grid_columnconfigure(1, weight=2)

        bus_row = tk.IntVar(self, 0)
        bank_row = tk.IntVar(self, 0)
        con_row = tk.IntVar(self, 0)
        curr_row = None
        for label in self.contract_fields:
            # normalize label -> key used in dict
            src_key = label.replace(":", "").strip()
            initial = self.data.get(src_key, "")
            sv = tk.StringVar(value=initial)
            values = COMBOBOX_VALUES.get(label, None)
            block = LabeledEntry(self.fields, label=label, textvariable=sv, values=values)
            column = CONTRACT_FIELDS_COLS[label]
            if label in BUSINESS_INFO:
                curr_row = bus_row
            elif label in BANK_INFO:
                curr_row = bank_row
            else:
                curr_row = con_row
            block.grid(row=curr_row.get(), column=column, sticky="ew", padx=6, pady=4)
            curr_row.set(curr_row.get() + 1)            

            self.vars[src_key] = sv
            self.blocks[src_key] = block

        self.format_all = self._setup_bindings()
        self.format_all()

        self.fields.pack(pady=20, fill="x")

        # ---------- buttons ----------
        self.contract_button_frame = tk.Frame(self, bg=bg)
        self.contract_button_frame.pack(side='bottom')

        self.generate_button = tk.Button(
            self.contract_button_frame,
            text="Generate Contracts",
            font=("Segoe UI", 14),
            command=lambda: [self.format_all(), self._on_generate(finalize_handler)],
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

    #def setup bindings
    def _setup_bindings(self) -> callable:
        #define format funcs
        def _fmt(key_var: tk.StringVar | None):
            if not key_var:
                return
            key_var.set(self.model._capitalize_all(key_var.get()))

        #unique format funcs: ein, phone, fee, state
        def format_ein(*_):
            ein_var = self.vars.get("EIN")
            if not ein_var:
                return
            ein = self.model._fmt_ein(ein_var.get())
            if ein is not None:
                ein_var.set(ein)

        def format_phone_number(*_):
            phone_var = self.vars.get("Tele No")
            phone = self.model._fmt_phone(phone_var.get())
            if phone is not None:
                phone_var.set(phone)
        
        def format_fee(*_):
            pct_var = self.vars.get('Fee')
            if not pct_var:
                return
            p = self.model._percent_to_float(pct_var.get())
            pct_var.set(self.model._fmt_percent(p))
        
        def format_state(*_):
            state_var = self.vars.get("State")
            state = self.model._fmt_state(state_var.get())
            if state is not None:
                state_var.set(state)

        #money format: fee amount, LOC, initial funding
        def format_money(key_var: tk.StringVar | None):
            if not key_var:
                return
            f = self.model._money_to_float(key_var.get())
            key_var.set(self.model._fmt_money(f))

        #reg number format (delete anything but digits and dashes): routing, account, zip
        def format_number(key_var: tk.StringVar | None):
            if not key_var:
                return
            key_var.set(self.model._fmt_number(key_var.get()))

        #Fee, Fee amount, and LOC: add trace to update other two, bind on focusout to format
        self._sync_guard = False

        def recompute_from_percent(
                loc_var=self.vars.get('Line of Credit'),
                pct_var=self.vars.get('Fee'),
                amt_var=self.vars.get('Fee Amount')
        ):
            if not loc_var or not pct_var or not amt_var:
                return
            if self._sync_guard:
                return
            self._sync_guard = True
            try:
                loc = self.model._money_to_float(loc_var.get())
                pct = self.model._percent_to_float(pct_var.get())
                if loc is not None and pct is not None:
                    fee_amount = loc * (pct / 100.0)
                    amt_var.set(self.model._fmt_money(fee_amount)) # ensure percent displays with %
            finally:
                self._sync_guard = False

        def recompute_from_amount(
                loc_var=self.vars.get('Line of Credit'),
                pct_var=self.vars.get('Fee'),
                amt_var=self.vars.get('Fee Amount')
        ):
            if not loc_var or not pct_var or not amt_var:
                return
            if self._sync_guard:
                return
            self._sync_guard = True
            try:
                loc = self.model._money_to_float(loc_var.get())
                amt = self.model._money_to_float(amt_var.get())
                if loc not in (None, 0) and amt is not None:
                    pct = (amt / loc) * 100.0
                    pct_var.set(self.model._fmt_percent(pct))
            finally:
                self._sync_guard = False

        def recompute_when_loc_changes(*_):
            recompute_from_percent() # If LOC changes, prefer recomputing amount from the existing percent

        #create dict to map field names to funcs for bind on focus out
        BIND_MAPPING: dict[str, callable] = {
            'Merchant Name': lambda *_: _fmt(self.vars.get('Merchant Name')),
            'Tele No': format_phone_number,
            'Fee': format_fee,
            'Fee Amount': lambda *_: format_money(self.vars.get('Fee Amount')),
            'EIN': format_ein,
            'Merchant Address': lambda *_: _fmt(self.vars.get('Merchant Address')),
            'City': lambda *_: _fmt(self.vars.get('City')),
            'State': format_state,
            'Zip': lambda *_: format_number(self.vars.get('Zip')),
            'Bank': lambda *_: _fmt(self.vars.get('Bank')),
            'Routing Number': lambda *_: format_number(self.vars.get('Routing Number')),
            'Account Number': lambda *_: format_number(self.vars.get('Account Number')),
            'Line of Credit': lambda *_: format_money(self.vars.get('Line of Credit')),
            'Initial Funding': lambda *_: format_money(self.vars.get('Initial Funding')),
            'Print Name': lambda *_: _fmt(self.vars.get('Print Name')),
            'Date': lambda *_: format_number(self.vars.get('Date'))
        }
        #another dict to map fields to traces on write
        TRACE_MAPPING: dict[str, callable] = {
            'Fee': lambda *_: recompute_from_percent(),
            'Fee Amount': lambda *_: recompute_from_amount(),
            'Line of Credit': recompute_when_loc_changes
        }

        for field in self.contract_fields: #for each field in fields
            #get var and block from self.vars and self.blocks
            var = self.vars.get(field)
            block = self.blocks.get(field)
            #get bind func and trace func if exists from mappings
            bind_func = BIND_MAPPING.get(field)
            trace_func = TRACE_MAPPING.get(field)
            #bind format func on focusOut to block
            if bind_func: block.bind("<FocusOut>", bind_func)
            #add trace on write from mapping if exists
            if trace_func: var.trace_add("write", trace_func)
            #add trace on write to var for updating model
            # suffix = " Number" if field in ["Account Number", "Routing Number"] else ""
            model_field = field.replace(" Number", '') if field in ["Account Number", "Routing Number"] else field
            var.trace_add(
                'write',
                lambda *_: self.model.afs_data.__setitem__(model_field, var.get())
            )

        def format_all():
            for key in BIND_MAPPING.keys():
                BIND_MAPPING.get(key)()
            for key in TRACE_MAPPING.keys():
                TRACE_MAPPING.get(key)()

        return format_all


class LabeledEntry(ttk.Frame):
    def __init__(self, parent, label, textvariable=None, width=25, height=45, values=None, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self.label = ttk.Label(self, text=label)
        self.label.grid(row=0, column=0, sticky="w", padx=(0, 8))
        large_font = font.Font(family="Helvetica", size=14)
        self.entry = None
        if values is None:
            self.entry = ttk.Entry(
                self, 
                textvariable=textvariable, 
                width=width,
                font=large_font
            )
        else:
            self.entry = ttk.Combobox(
            self, 
            textvariable=textvariable, 
            width=width,
            values=values,
            state="readonly",
            font=large_font
        )
        self.entry.grid(row=1, column=0, sticky="ew")
        self.grid_columnconfigure(1, weight=1)

