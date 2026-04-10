import customtkinter as ctk
import json
import os
import pyperclip
from engine import CryptoEngine
from ledger import Ledger

# Alapvető vizuális beállítások
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ZPayApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ablak alapbeállításai
        self.title("Z-Pay Local v1.2 - Stable Edition")
        self.geometry("1000x650")

        # Backend példányosítás
        self.ledger = Ledger()
        self.current_user = None  # Feloldott kulcsok a memóriában

        # UI elemek referenciái a későbbi takarításhoz
        self.sidebar = None
        self.content_area = None
        self.auth_frame = None

        self.setup_initial_view()

    def setup_initial_view(self):
        """Kezdeti nézet felépítése (Login vagy Register)."""
        self.clear_all_widgets()

        # Rácsszerkezet alaphelyzetbe állítása (fontos a tiszta váltáshoz)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        if os.path.exists("wallet.json"):
            self.show_auth_screen("Bejelentkezés", "Oldja fel a tárcáját a jelszavával.", self.unlock_wallet)
        else:
            self.show_auth_screen("Új Tárca Létrehozása", "Adjon meg egy jelszót a tárca védelméhez.",
                                  self.create_wallet)

    def show_auth_screen(self, title, subtitle, action_func):
        """Közös felület a regisztrációhoz és belépéshez."""
        self.auth_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.auth_frame, text=title, font=("Arial", 32, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(self.auth_frame, text=subtitle, font=("Arial", 14), text_color="gray").pack(pady=(0, 30))

        self.pwd_input = ctk.CTkEntry(self.auth_frame, placeholder_text="Mester Jelszó", show="*", width=300, height=45)
        self.pwd_input.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.auth_frame, text="", text_color="#E74C3C")
        self.status_label.pack(pady=5)

        ctk.CTkButton(self.auth_frame, text="Indítás", command=action_func, width=300, height=45,
                      font=("Arial", 16, "bold")).pack(pady=20)

    # --- LOGIKA ---

    def create_wallet(self):
        pwd = self.pwd_input.get()
        if len(pwd) < 4:
            self.status_label.configure(text="A jelszónak legalább 4 karakternek kell lennie!")
            return

        priv, pub = CryptoEngine.generate_keypair()
        enc_priv = CryptoEngine.encrypt_private_key(priv, pwd)

        with open("wallet.json", "w") as f:
            json.dump({"address": pub, "vault": enc_priv}, f)

        self.setup_initial_view()

    def unlock_wallet(self):
        pwd = self.pwd_input.get()
        try:
            with open("wallet.json", "r") as f:
                data = json.load(f)

            priv = CryptoEngine.decrypt_private_key(data['vault'], pwd)
            if priv:
                self.current_user = {"priv": priv, "pub": data['address']}
                self.auth_frame.destroy()
                self.build_main_interface()
            else:
                self.status_label.configure(text="Hibás jelszó! Próbálja újra.")
        except Exception:
            self.status_label.configure(text="Hiba a pénztárca fájl beolvasásakor.")

    # --- FŐ INTERFÉSZ ---

    def build_main_interface(self):
        # Ablak rácsának újraosztása a Sidebar-hoz
        self.grid_columnconfigure(0, weight=0)  # Sidebar fix
        self.grid_columnconfigure(1, weight=1)  # Tartalom nyúlik

        # OLDALSÁV (SIDEBAR)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self.sidebar, text="Z-PAY", font=("Arial", 28, "bold"), text_color="#3B8ED0").pack(pady=30)

        ctk.CTkButton(self.sidebar, text="Irányítópult", fg_color="transparent", anchor="w",
                      command=self.draw_dashboard).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.sidebar, text="Pénz küldése", fg_color="transparent", anchor="w",
                      command=self.draw_send).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.sidebar, text="Előzmények", fg_color="transparent", anchor="w",
                      command=self.draw_history).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(self.sidebar, text="Kijelentkezés", fg_color="#333", command=self.logout).pack(side="bottom",
                                                                                                     fill="x", padx=20,
                                                                                                     pady=20)

        # TARTALMI TERÜLET
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)

        self.draw_dashboard()

    def draw_dashboard(self):
        self.clear_content()
        balance = self.ledger.get_balance(self.current_user['pub'])

        card = ctk.CTkFrame(self.content_area, fg_color="#2B2B2B", corner_radius=15)
        card.pack(fill="x", pady=10)

        ctk.CTkLabel(card, text="Aktuális Egyenleg", font=("Arial", 16), text_color="gray").pack(pady=(25, 0))
        ctk.CTkLabel(card, text=f"{balance:,.2f} ZCOIN", font=("Arial", 48, "bold"), text_color="#3B8ED0").pack(
            pady=(5, 25))

        addr_box = ctk.CTkFrame(self.content_area, fg_color="#1E1E1E", height=60)
        addr_box.pack(fill="x", pady=20)

        full_addr = self.current_user['pub']
        ctk.CTkLabel(addr_box, text=f"Saját cím:  {full_addr[:35]}...", font=("Consolas", 13)).pack(side="left",
                                                                                                    padx=20, pady=15)

        def copy_action():
            pyperclip.copy(full_addr)
            copy_btn.configure(text="Másolva!", fg_color="#2ECC71")

            # BIZTONSÁGOS IDŐZÍTŐ: Ellenőrizzük, létezik-e még a gomb (logout után pl nem)
            def reset_button():
                if copy_btn.winfo_exists():
                    copy_btn.configure(text="Másolás", fg_color="#3B8ED0")

            self.after(2000, reset_button)

        copy_btn = ctk.CTkButton(addr_box, text="Másolás", width=100, command=copy_action)
        copy_btn.pack(side="right", padx=10)

    def draw_send(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="Tranzakció indítása", font=("Arial", 24, "bold")).pack(pady=(0, 30),
                                                                                                     anchor="w")

        target_input = ctk.CTkEntry(self.content_area, placeholder_text="Fogadó címe (0x...)", width=500, height=40)
        target_input.pack(pady=5, anchor="w")

        amount_input = ctk.CTkEntry(self.content_area, placeholder_text="0.00", width=200, height=40)
        amount_input.pack(pady=10, anchor="w")

        info_label = ctk.CTkLabel(self.content_area, text="")
        info_label.pack(anchor="w")

        def initiate_transfer():
            try:
                amt = float(amount_input.get())
                target = target_input.get()
                msg = f"{self.current_user['pub']}-{target}-{amt}"
                signature = CryptoEngine.sign_transaction(self.current_user['priv'], msg)

                success, response = self.ledger.add_transaction(self.current_user['pub'], target, amt, signature)
                info_label.configure(text=response, text_color="#2ECC71" if success else "#E74C3C")
            except ValueError:
                info_label.configure(text="Hiba: Érvénytelen összeg!", text_color="#E74C3C")

        ctk.CTkButton(self.content_area, text="Küldés megerősítése", command=initiate_transfer,
                      fg_color="#2ECC71").pack(pady=20, anchor="w")

    def draw_history(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="Tranzakciós napló", font=("Arial", 24, "bold")).pack(pady=(0, 20),
                                                                                                   anchor="w")

        scroll = ctk.CTkScrollableFrame(self.content_area, height=400)
        scroll.pack(fill="both", expand=True)

        history = self.ledger.get_history(self.current_user['pub'])
        for tx in history:
            is_in = tx['receiver'] == self.current_user['pub']
            color = "#2ECC71" if is_in else "#E74C3C"
            f = ctk.CTkFrame(scroll, fg_color="#252525", height=60)
            f.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(f, text=f"{tx['date_str']}", font=("Arial", 11), text_color="gray").pack(side="left", padx=15)
            ctk.CTkLabel(f, text=f"{'+' if is_in else '-'}{tx['amount']} ZCOIN", font=("Arial", 14, "bold"),
                         text_color=color).pack(side="right", padx=20)

    def logout(self):
        """Biztonságos kijelentkezés és felület-visszaállítás."""
        self.current_user = None
        self.setup_initial_view()

    def clear_content(self):
        """Csak a belső tartalmi területet törli."""
        if self.content_area and self.content_area.winfo_exists():
            for widget in self.content_area.winfo_children():
                widget.destroy()

    def clear_all_widgets(self):
        """Teljesen kitakarítja az ablakot az új nézethez."""
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = ZPayApp()
    app.mainloop()