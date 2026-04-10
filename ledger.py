import json
import os
import time
import hashlib
from datetime import datetime

# A globális főkönyv fájlneve, amely a közös hálózatot szimulálja
LEDGER_FILE = "global_ledger.json"


class Ledger:
    """
    A Ledger osztály felelős a tranzakciók hitelesítéséért és tárolásáért.
    Ez szimulálja a decentralizált hálózatot egy közös JSON fájlon keresztül.
    """

    def __init__(self):
        """Inicializálja a főkönyvet, ha még nem létezik."""
        if not os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, "w") as f:
                json.dump([], f)

    def get_all_transactions(self):
        """Beolvassa az összes tranzakciót a globális adatbázisból."""
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
        Minden új cím automatikusan 1000.0 ZCOIN-nal indul a gyakorláshoz.
        """
        balance = 1000.0  # Kezdő egyenleg (Genesis bonus)
        transactions = self.get_all_transactions()

        for tx in transactions:
            if tx['sender_addr'] == address:
                balance -= tx['amount']
            if tx['receiver_addr'] == address:
                balance += tx['amount']

        return balance

    def get_history(self, address):
        """
        Lekéri egy adott címhez tartozó összes tranzakciót.
        A listát a legfrissebbtől a legrégebbi felé rendezi.
        """
        all_tx = self.get_all_transactions()
        history = [tx for tx in all_tx if tx['sender_addr'] == address or tx['receiver_addr'] == address]

        # Rendezés timestamp szerint csökkenő sorrendbe
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)

    def add_transaction(self, sender_pub, sender_addr, receiver_addr, amount, signature):
        """
        Validál és rögzít egy új tranzakciót a hálózaton.
        """
        from engine import CryptoEngine  # Körkörös import elkerülése

        # 1. Alapvető ellenőrzések
        if amount <= 0:
            return False, "Hiba: Az összegnek pozitívnak kell lennie!"

        if sender_addr == receiver_addr:
            return False, "Hiba: Önmagának nem utalhat!"

        # 2. Aláírás ellenőrzése (Zero Knowledge bizonyíték)
        # Az aláírandó üzenetnek pontosan egyeznie kell a küldő által aláírttal
        msg = f"{sender_addr}-{receiver_addr}-{amount}"
        if not CryptoEngine.verify_signature(sender_pub, msg, signature):
            return False, "Hiba: Érvénytelen digitális aláírás!"

        # 3. Fedezet ellenőrzése
        if self.get_balance(sender_addr) < amount:
            return False, "Hiba: Nincs elegendő fedezet a tranzakcióhoz!"

        # 4. Egyedi Transaction ID (TXID) generálása (Hash)
        # A hash alapja az üzenet, az időbélyeg és az aláírás egy része
        raw_id_str = f"{msg}{time.time()}{signature[:10]}"
        tx_hash = hashlib.sha256(raw_id_str.encode()).hexdigest()
        tx_id = f"0x{tx_hash[:16]}"  # Rövidített hash a szebb megjelenítéshez

        # 5. Tranzakciós objektum összeállítása
        tx = {
            "tx_id": tx_id,
            "sender_addr": sender_addr,
            "receiver_addr": receiver_addr,
            "amount": amount,
            "timestamp": time.time(),
            "date": datetime.now().strftime("%H:%M:%S | %Y.%m.%d"),
            "status": "Confirmed"
        }

        # 6. Írás a fájlba (Atomic-like művelet szimulálása)
        try:
            all_tx = self.get_all_transactions()
            all_tx.append(tx)

            with open(LEDGER_FILE, "w") as f:
                json.dump(all_tx, f, indent=4)

            return True, f"Sikeres tranzakció! ID: {tx_id}"
        except Exception as e:
            return False, f"Rendszerhiba a mentés során: {str(e)}"