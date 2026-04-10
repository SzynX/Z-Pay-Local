import json
import os
import time
import hashlib
from datetime import datetime

# A globális főkönyv fájlneve, amely a közös hálózatot szimulálja
LEDGER_FILE = "global_ledger.json"


class Ledger:
    """
    A Ledger osztály felelős a tranzakciók integritásáért és tárolásáért.
    Visszafelé kompatibilis a v1.5 és v1.6-os adatszerkezetekkel.
    """

    def __init__(self):
        """Inicializálja a főkönyvet. Ha a fájl nem létezik, létrehoz egy üres listát."""
        if not os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, "w") as f:
                json.dump([], f)

    def get_all_transactions(self):
        """Beolvassa az összes rögzített tranzakciót a fájlból."""
        try:
            if not os.path.exists(LEDGER_FILE):
                return []
            with open(LEDGER_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return []

    def get_balance(self, address):
        """
        Kiszámolja egy adott 0x... cím aktuális egyenlegét.
        Kezeli a régi (sender_addr) és az új (sender) kulcsneveket is a hiba elkerülése végett.
        """
        balance = 1000.0  # Kezdő egyenleg (Genesis bonus)
        transactions = self.get_all_transactions()

        for tx in transactions:
            # Kompatibilitási réteg: ha nincs 'sender', keresse 'sender_addr'-ként
            s = tx.get('sender') or tx.get('sender_addr')
            r = tx.get('receiver') or tx.get('receiver_addr')
            amt = tx.get('amount', 0)

            if s == address:
                balance -= amt
            if r == address:
                balance += amt

        return balance

    def get_history(self, address):
        """
        Lekéri az összes olyan tranzakciót, amelyben az adott cím érintett.
        Egységesíti a régi és új kulcsneveket a GUI számára.
        """
        all_tx = self.get_all_transactions()
        history = []

        for tx in all_tx:
            # Kulcsok kinyerése bármelyik formátumból
            s = tx.get('sender') or tx.get('sender_addr')
            r = tx.get('receiver') or tx.get('receiver_addr')

            if s == address or r == address:
                # Dinamikusan hozzáadjuk/javítjuk a kulcsokat a memóriában a GUI-hoz
                tx['sender'] = s
                tx['receiver'] = r
                history.append(tx)

        # Rendezés timestamp szerint csökkenő sorrendbe
        return sorted(history, key=lambda x: x.get('timestamp', 0), reverse=True)

    def add_transaction(self, sender_pub, sender_addr, receiver_addr, amount, signature):
        """
        Új tranzakció validálása és véglegesítése a 2.0-ás szabvány szerint.
        """
        from engine import CryptoEngine  # Körkörös hivatkozás megelőzése

        # 1. Alapvető validációk
        if amount <= 0:
            return False, "Hiba: Az összegnek pozitívnak kell lennie!"

        if sender_addr == receiver_addr:
            return False, "Hiba: Önmagának nem küldhet pénzt!"

        # 2. Digitális aláírás ellenőrzése (Zero Knowledge Proof)
        msg = f"{sender_addr}-{receiver_addr}-{amount}"
        if not CryptoEngine.verify_signature(sender_pub, msg, signature):
            return False, "Hiba: Érvénytelen aláírás! A tranzakció elutasítva."

        # 3. Egyenleg ellenőrzése
        if self.get_balance(sender_addr) < amount:
            return False, "Hiba: Nincs elegendő fedezet a tárcán!"

        # 4. Egyedi Tranzakció ID (Hash) generálása
        raw_id_str = f"{msg}{time.time()}{signature[:20]}"
        tx_hash = hashlib.sha256(raw_id_str.encode()).hexdigest()
        tx_id = f"0x{tx_hash[:16]}"

        # 5. Tranzakció rögzítése (v2.0-ás formátum)
        tx_data = {
            "tx_id": tx_id,
            "sender": sender_addr,
            "receiver": receiver_addr,
            "amount": amount,
            "timestamp": time.time(),
            "date": datetime.now().strftime("%Y.%m.%d %H:%M:%S"),
            "status": "Confirmed"
        }

        try:
            data = self.get_all_transactions()
            data.append(tx_data)

            with open(LEDGER_FILE, "w") as f:
                json.dump(data, f, indent=4)

            return True, f"Sikeres! Tranzakció hash: {tx_id}"
        except Exception as e:
            return False, f"Rendszerhiba a mentés során: {str(e)}"