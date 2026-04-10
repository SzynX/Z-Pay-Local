import customtkinter as ctk
import json
import os
import pyperclip
from engine import CryptoEngine
from ledger import Ledger

# Ethereum 2.0 Professzionális Színpaletta
C_BG = "#030303"  # Teljesen sötét háttér
C_SIDE = "#0a0a0c"  # Oldalsáv sötétszürke
C_CARD = "#141416"  # Kártyák és panelek színe
C_ACCENT = "#627eea"  # Klasszikus Ethereum kék/lila
C_TEXT = "#f0f0f0"  # Világos szöveg
C_GRAY = "#6e6e73"  # Tompított szürke szöveg
C_GREEN = "#2ecc71"  # Sikeres tranzakció
C_RED = "#e74c3c"  # Hiba / Kimenő forgalom

ctk.set_appearance_mode("dark")


class ZPayApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ablak beállítások
        self.title("Z-Pay 2.0 Pro - Decentralized Ledger Interface")

        # Teljes képernyős indítás
        try:
            self.state('zoomed')
        except:
            self.geometry("1280x800")

        self.configure(fg_color=C_BG)

        # Backend inicializálás
        self.ledger = Ledger()
        self.current_user = None  # {name, priv, pub, addr}
        self.vault_path = "vault.json"

        # UI komponensek referenciái
        self.sidebar = None
        self.status_bar = None
        self.content_area = None

        # Vault fájl ellenőrzése
        if not os.path.exists(self.vault_path):
            with open(self.vault_path, "w") as f:
                json.dump({"accounts": []}, f)

        self.show_account_selector()

    def clear_screen(self):
        """Teljesen kitakarítja az ablakot az új nézetváltáshoz."""
        for widget in self.winfo_children():
            widget.destroy()

    # --- 1. NÉZET: FIÓK VÁLASZTÓ ---

    def show_account_selector(self):
        self.clear_screen()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0)

        ctk.CTkLabel(container, text="Z-PAY 2.0", font=("Orbitron", 54, "bold"), text_color=C_ACCENT).pack(pady=5)
        ctk.CTkLabel(container, text="DECENTRALIZED LOCAL ECOSYSTEM", font=("Arial", 14, "bold"),
                     text_color=C_GRAY).pack(pady=(0, 40))

        # Fiókok listája
        list_frame = ctk.CTkScrollableFrame(container, width=550, height=350, fg_color=C_CARD, corner_radius=25,
                                            border_width=1, border_color="#222")
        list_frame.pack(pady=10)

        with open(self.vault_path, "r") as f:
            vault = json.load(f)

        if not vault["accounts"]:
            ctk.CTkLabel(list_frame, text="Még nincsenek mentett tárcák", font=("Arial", 14), text_color=C_GRAY).pack(
                pady=50)
        else:
            for acc in vault["accounts"]:
                acc_btn = ctk.CTkButton(
                    list_frame,
                    text=f" 👤  {acc['name']}\n      {acc['address']}",
                    font=("Arial", 14),
                    anchor="w",
                    fg_color="#1c1c1e",
                    hover_color=C_ACCENT,
                    height=85,
                    corner_radius=15,
                    command=lambda a=acc: self.show_login(a)
                )
                acc_btn.pack(fill="x", pady=8, padx=15)

        ctk.CTkButton(container, text="+ Új tárca létrehozása", font=("Arial", 16, "bold"), fg_color=C_ACCENT,
                      hover_color="#4f66c9", height=60, corner_radius=15, command=self.show_create_account).pack(
            pady=30, fill="x")

    def show_create_account(self):
        self.clear_screen()
        cont = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=30, border_width=1, border_color="#222")
        cont.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(cont, text="Secure Wallet Generation", font=("Arial", 26, "bold")).pack(pady=(35, 10), padx=70)
        ctk.CTkLabel(cont, text="Minden adat titkosítva kerül tárolásra a vault.json-ban.", font=("Arial", 12),
                     text_color=C_GRAY).pack(pady=(0, 25))

        name_in = ctk.CTkEntry(cont, placeholder_text="Fiók neve", width=380, height=50, fg_color=C_BG,
                               border_color="#333")
        name_in.pack(pady=10)

        pwd_in = ctk.CTkEntry(cont, placeholder_text="Mester jelszó", show="*", width=380, height=50, fg_color=C_BG,
                              border_color="#333")
        pwd_in.pack(pady=10)

        def save():
            name, pwd = name_in.get(), pwd_in.get()
            if not name or not pwd: return
            priv, addr, pub = CryptoEngine.generate_keypair()
            enc_priv = CryptoEngine.encrypt_private_key(priv, pwd)
            with open(self.vault_path, "r") as f: v = json.load(f)
            v["accounts"].append({"name": name, "address": addr, "pub": pub, "vault": enc_priv})
            with open(self.vault_path, "w") as f: json.dump(v, f, indent=4)
            self.show_account_selector()

        ctk.CTkButton(cont, text="Generálás és Titkosítás", fg_color=C_ACCENT, font=("Arial", 15, "bold"), height=55,
                      width=380, command=save).pack(pady=30)
        ctk.CTkButton(cont, text="Vissza", fg_color="transparent", text_color=C_GRAY,
                      command=self.show_account_selector).pack(pady=(0, 25))

    def show_login(self, acc):
        self.clear_screen()
        cont = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=30, border_width=1, border_color="#222")
        cont.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(cont, text=f"Unlock {acc['name']}", font=("Arial", 26, "bold"), text_color=C_ACCENT).pack(
            pady=(35, 5), padx=80)
        ctk.CTkLabel(cont, text=acc['address'], font=("Consolas", 12), text_color=C_GRAY).pack(pady=(0, 25))

        pwd_in = ctk.CTkEntry(cont, placeholder_text="Jelszó", show="*", width=380, height=50, fg_color=C_BG,
                              border_color="#333")
        pwd_in.pack(pady=10)

        def unlock():
            priv = CryptoEngine.decrypt_private_key(acc['vault'], pwd_in.get())
            if priv:
                self.current_user = {"name": acc['name'], "priv": priv, "pub": acc['pub'], "addr": acc['address']}
                self.build_main_dashboard()
            else:
                pwd_in.configure(border_color=C_RED)

        ctk.CTkButton(cont, text="Fiók Feloldása", fg_color=C_ACCENT, font=("Arial", 15, "bold"), height=55, width=380,
                      command=unlock).pack(pady=30)
        ctk.CTkButton(cont, text="Mégse", fg_color="transparent", text_color=C_GRAY,
                      command=self.show_account_selector).pack(pady=(0, 25))

    # --- 2. NÉZET: FŐ DASHBOARD ---

    def build_main_dashboard(self):
        self.clear_screen()
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Oldalsáv
        self.sidebar = ctk.CTkFrame(self, width=300, fg_color=C_SIDE, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="Z-PAY 2.0", font=("Orbitron", 32, "bold"), text_color=C_ACCENT).pack(pady=60)

        menu = [("🏠 Irányítópult", self.draw_dash), ("💸 Pénz küldése", self.draw_send),
                ("📜 Tranzakciók", self.draw_history)]
        for text, cmd in menu:
            ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", font=("Arial", 16), anchor="w",
                          hover_color="#1a1a1c", height=65, command=cmd).pack(fill="x", padx=25, pady=5)

        ctk.CTkButton(self.sidebar, text="🔒 Kijelentkezés", font=("Arial", 14, "bold"), fg_color="#1c1c1e",
                      text_color=C_RED,
                      command=self.show_account_selector).pack(side="bottom", pady=40, padx=40, fill="x")

        # Felső Állapotsáv
        self.status_bar = ctk.CTkFrame(self, height=70, fg_color=C_CARD, corner_radius=0, border_width=1,
                                       border_color="#222")
        self.status_bar.grid(row=0, column=1, sticky="new")

        ctk.CTkLabel(self.status_bar, text="🟢 Network: Z-Pay Mainnet (Local)", font=("Arial", 13)).pack(side="left",
                                                                                                        padx=40)
        ctk.CTkLabel(self.status_bar, text=f"Active Wallet: {self.current_user['addr']}", font=("Consolas", 13),
                     text_color=C_GRAY).pack(side="right", padx=40)

        # Tartalmi terület
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=80, pady=(120, 60))
        self.draw_dash()

    def draw_dash(self):
        self.clear_content()
        balance = self.ledger.get_balance(self.current_user['addr'])

        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"Welcome, {self.current_user['name']}!", font=("Arial", 36, "bold")).pack(
            side="left")

        card = ctk.CTkFrame(self.content_area, fg_color=C_ACCENT, corner_radius=35, height=280)
        card.pack(fill="x", pady=40)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="TOTAL BALANCE", font=("Arial", 18, "bold"), text_color="#d1d1d1").pack(pady=(60, 0))
        ctk.CTkLabel(card, text=f"{balance:,.2f} ZCOIN", font=("Arial", 78, "bold")).pack()

        info_card = ctk.CTkFrame(self.content_area, fg_color=C_CARD, corner_radius=20, border_width=1,
                                 border_color="#222")
        info_card.pack(fill="x")
        ctk.CTkLabel(info_card, text=f"Saját tárcacímed: {self.current_user['addr']}", font=("Consolas", 16)).pack(
            side="left", padx=30, pady=30)

        def copy():
            pyperclip.copy(self.current_user['addr'])
            copy_btn.configure(text="Siker!", fg_color=C_GREEN)
            self.after(2000, lambda: copy_btn.configure(text="Másolás",
                                                        fg_color="#2b2b2b") if copy_btn.winfo_exists() else None)

        copy_btn = ctk.CTkButton(info_card, text="Másolás", fg_color="#2b2b2b", width=140, height=45,
                                 font=("Arial", 14, "bold"), command=copy)
        copy_btn.pack(side="right", padx=30)

    def draw_send(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="Pénzeszközök küldése", font=("Arial", 32, "bold")).pack(anchor="w",
                                                                                                      pady=(0, 40))

        form_container = ctk.CTkFrame(self.content_area, fg_color=C_CARD, corner_radius=30, border_width=1,
                                      border_color="#222")
        form_container.pack(fill="x")

        inner = ctk.CTkFrame(form_container, fg_color="transparent")
        inner.pack(padx=60, pady=60, fill="x")

        ctk.CTkLabel(inner, text="Fogadó címe", font=("Arial", 14), text_color=C_GRAY).pack(anchor="w", padx=5)
        target_in = ctk.CTkEntry(inner, placeholder_text="0x...", width=800, height=55, fg_color=C_BG,
                                 border_color="#333")
        target_in.pack(pady=(5, 20))

        ctk.CTkLabel(inner, text="Összeg (ZCOIN)", font=("Arial", 14), text_color=C_GRAY).pack(anchor="w", padx=5)
        amt_in = ctk.CTkEntry(inner, placeholder_text="0.00", width=800, height=55, fg_color=C_BG, border_color="#333")
        amt_in.pack(pady=(5, 30))

        status_lbl = ctk.CTkLabel(inner, text="", font=("Arial", 14))
        status_lbl.pack(pady=10)

        def process():
            try:
                amt = float(amt_in.get())
                target = target_in.get()
                msg = f"{self.current_user['addr']}-{target}-{amt}"
                sig = CryptoEngine.sign_transaction(self.current_user['priv'], msg)
                success, res = self.ledger.add_transaction(self.current_user['pub'], self.current_user['addr'], target,
                                                           amt, sig)
                status_lbl.configure(text=res, text_color=C_GREEN if success else C_RED)
            except:
                status_lbl.configure(text="Hiba: Érvénytelen adatok!", text_color=C_RED)

        ctk.CTkButton(inner, text="Tranzakció Aláírása és Küldése", fg_color=C_ACCENT, font=("Arial", 18, "bold"),
                      height=65, width=400, command=process).pack(pady=20)

    def draw_history(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="Tranzakciós napló", font=("Arial", 32, "bold")).pack(anchor="w",
                                                                                                   pady=(0, 30))

        scroll = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent", height=600)
        scroll.pack(fill="both", expand=True)

        history = self.ledger.get_history(self.current_user['addr'])
        if not history:
            ctk.CTkLabel(scroll, text="Még nincsenek tranzakciók.", font=("Arial", 16), text_color=C_GRAY).pack(
                pady=100)
            return

        for tx in history:
            is_in = tx['receiver'] == self.current_user['addr']
            card = ctk.CTkFrame(scroll, fg_color=C_CARD, height=110, corner_radius=25, border_width=1,
                                border_color="#222")
            card.pack(fill="x", pady=8, padx=10)

            # Ikon és Dátum
            ctk.CTkLabel(card, text="📥" if is_in else "📤", font=("Arial", 30)).pack(side="left", padx=30)

            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.pack(side="left", pady=15)
            ctk.CTkLabel(info_f, text=tx['date'], font=("Arial", 12, "bold"), text_color=C_GRAY).pack(anchor="w")
            ctk.CTkLabel(info_f, text=f"Hash: {tx['tx_id']}", font=("Consolas", 14), text_color=C_ACCENT).pack(
                anchor="w")

            # Összeg
            amt_color = C_GREEN if is_in else C_RED
            amt_prefix = "+" if is_in else "-"
            ctk.CTkLabel(card, text=f"{amt_prefix}{tx['amount']} ZCOIN", font=("Arial", 24, "bold"),
                         text_color=amt_color).pack(side="right", padx=50)

    def clear_content(self):
        if self.content_area:
            for widget in self.content_area.winfo_children():
                widget.destroy()


if __name__ == "__main__":
    app = ZPayApp()
    app.mainloop()