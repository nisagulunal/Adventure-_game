import json
import os
import random
import time

# Karakter sınıfı (oyuncu)
class Character:
    def __init__(self, name, health=100, gold=0, xp=0, level=1):
        self.name = name
        self.health = health
        self.gold = gold
        self.inventory = []
        self.xp = xp
        self.level = level

    # XP kazanımı ve seviye atlama
    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 100:
            self.level += 1
            self.health += 20
            print(f"\n⭐ Seviye atladın! Yeni seviye: {self.level} | Sağlık: {self.health}")

    # Oyuncunun durumunu göster
    def show_status(self):
        print(f"\n{self.name}'in Durumu:")
        print(f"  Seviye: {self.level}  XP: {self.xp}/{self.level*100}")
        print(f"  Sağlık: {self.health}")
        print(f"  Altın: {self.gold}")
        print(f"  Envanter: {', '.join(self.inventory) if self.inventory else 'Boş'}")

# Düşman sınıfı
class Enemy:
    def __init__(self, name, health, attack_power, special=None):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.special = special

# Kalıtım örneği - Boss düşman sınıfı
class Boss(Enemy):
    def __init__(self):
        super().__init__("Ejderha", 150, 25)

# Ana oyun sınıfı
class Game:
    def __init__(self):
        self.player = None
        self.directions = ["kuzey", "güney", "doğu", "batı", "köy", "kule"]
        self.initial_challenges = ["CADI", "KURT", "MAĞAARA", "BATAKLIK", "DEV", "TUZAK", "HAYALET", "BOSS"]
        random.shuffle(self.initial_challenges)
        self.direction_challenges = dict(zip(self.directions[2:], self.initial_challenges[:4]))
        self.completed_challenges = []
        self.castle_unlocked = False
        self.village_direction = "köy"
        self.castle_direction = "kule"
        self.all_challenges = self.initial_challenges[:]

    # Oyunu başlat
    def start(self):
        print("🎮 Prensesi Kurtarma Macerasına Hoş Geldin!")
        print("🎮 İpucu:Köyden anahtar satın alıp kuleyi açabilirsin.")
        choice = input("1- Yeni Oyun\n2- Kaydı Yükle\nSeçiminiz: ")

        if choice == "2" and os.path.exists("save.json"):
            self.load_game()
        else:
            global name
            name = input("Kahramanının adı: ")
            self.player = Character(name)

            # Tuple örneği - Oyuncuya başlangıçta 3 eşya verilir
            basic_items = ("Mızrak", "Zırh", "İksir")
            self.player.inventory.extend(list(basic_items))

        while self.player.health > 0:
            if self.castle_unlocked:
                print("\n🎉 Oyunu başarıyla tamamladın! Prensesi kurtardın!")
                break

            self.player.show_status()
            print("\nYönler: Kuzey, Güney, Doğu, Batı, Köy, Kule")
            direction = input("Hangi yöne gitmek istersin?: ").lower()

            if direction not in self.directions:
                print("Geçerli bir yön değil.")
                continue

            if direction == self.village_direction:
                self.handle_challenge("KÖY")
            elif direction == self.castle_direction:
                self.handle_challenge("KULE")
            else:
                challenge = self.direction_challenges.get(direction, random.choice(self.initial_challenges))
                self.handle_challenge(challenge)
                self.completed_challenges.append(challenge)

            self.save_game()

        if self.player.health <= 0:
            print("\n☠️ Oyunu kaybettin...")

    # Oyunu kaydet
    def save_game(self):
        save_data = {
            "name": self.player.name,
            "health": self.player.health,
            "gold": self.player.gold,
            "xp": self.player.xp,
            "level": self.player.level,
            "inventory": self.player.inventory,
            "completed_challenges": self.completed_challenges,
            "direction_challenges": self.direction_challenges,
            "castle_unlocked": self.castle_unlocked
        }
        with open("save.json", "w") as f:
            json.dump(save_data, f)

    # Kayıtlı oyunu yükle
    def load_game(self):
        with open("save.json") as f:
            data = json.load(f)
            self.player = Character(data["name"], data["health"], data["gold"], data["xp"], data["level"])
            self.player.inventory = data["inventory"]
            self.completed_challenges = data["completed_challenges"]
            self.direction_challenges = data["direction_challenges"]
            self.castle_unlocked = data.get("castle_unlocked", False)
            print("✔️ Kayıt yüklendi!")

    # Bölüm işleyici
    def handle_challenge(self, challenge):
        print("\n--- Yeni bir bölgeye girdin! ---")
        time.sleep(1)

        if challenge == "CADI":
            print("🧙‍♀️ Cadı bir bilmece sordu.")
            self.ask_riddle()
        elif challenge == "KURT":
            print("🐺 Kurt saldırıyor!")
            self.fight_enemy(Enemy("Kurt", 50, 15))
        elif challenge == "KÖY":
            print("🏘️ Köydesin. Anahtar 50 altın.")
            if self.player.gold >= 50:
                buy = input("Anahtar alınsın mı? (evet/hayır): ")
                if buy == "evet":
                    self.player.gold -= 50
                    self.player.inventory.append("Anahtar")
            else:
                print("Altının yetmiyor.")
        elif challenge == "KULE":
            print("🏰 Kuleye ulaştın.")
            if "Anahtar" in self.player.inventory:
                print("🔓 Prensesi kurtardın!")
                self.castle_unlocked = True
            else:
                print("Anahtar yok, geri dönmelisin.")
        elif challenge == "MAĞAARA":
            print("🌫️ Gizli mağarada gizemli bir hazine buldun. 50 XP kazandın!")
            self.player.gain_xp(50)
        elif challenge == "BATAKLIK":
            print("☠️ Zehirli bataklıktasın. Her tur sağlık kaybı olabilir.")
            lost = random.randint(10, 30)
            print(f"Zehir etkisiyle {lost} sağlık kaybettin.")
            self.player.health -= lost
            self.player.gain_xp(30)
        elif challenge == "DEV":
            print("👹 Dev karşında! Çok güçlü!")
            self.fight_enemy(Enemy("Dev", 70, 10))
        elif challenge == "TUZAK":
            print("🪤 Tuzaklara yakalandın!")
            damage = random.randint(10, 25)
            self.player.health -= damage
            print(f"{damage} sağlık kaybettin!")
        elif challenge == "HAYALET":
            print("👻 Hayalet seni korkutuyor. Cesurca dayanırsan ödül var.")
            action = input("Korkmadan bekle (b) ya da kaç (k): ")
            if action == "b":
                print("Hayalet kayboldu. 20 XP kazandın!")
                self.player.gain_xp(20)
            else:
                print("Kaçtın ama 10 sağlık kaybettin!")
                self.player.health -= 10
        elif challenge == "BOSS":
            print("🐉 Ejderha ile karşılaştın! Son savaş!")
            self.fight_enemy(Boss())

    # Bilmece sistemi
    def ask_riddle(self):
        riddles = [
            {"soru": "Uçmaz, kaçmaz ama her yere gider. Nedir?", "cevap": "yol"},
            {"soru": "Ne kadar çok alırsan o kadar büyür. Nedir?", "cevap": "delik"},
            {"soru": "Gündüz gölge yapar, gece kaybolur. Nedir?", "cevap": "güneş"}
        ]
        riddle = random.choice(riddles)
        cevap = input(f"Bilmece: {riddle['soru']}\nCevabın: ").lower()
        if cevap == riddle["cevap"]:
            print("✅ Doğru cevap! 30 altın ve 30 XP kazandın.")
            self.player.gold += 30
            self.player.gain_xp(30)
        else:
            print("❌ Yanlış. 10 can kaybettin.")
            self.player.health -= 10

    # Düşmanla savaş sistemi
    def fight_enemy(self, enemy):
        while enemy.health > 0 and self.player.health > 0:
            print(f"\n{enemy.name} Canı: {enemy.health}")
            move = input("Saldır / Savun / Kaç: ").lower()

            if move == "saldır":
                damage = random.randint(10, 20)
                enemy.health -= damage
                print(f"💥 {enemy.name}'a {damage} hasar verdin.")
            elif move == "savun":
                blocked = enemy.attack_power // 2
                self.player.health -= blocked
                print(f"🛡️ Savundun ama {blocked} hasar aldın.")
            elif move == "kaç":
                if random.random() < 0.5:
                    print("🏃 Kaçtın! 30 altın ve 40 XP kazandın.")
                    self.player.gold += 30
                    self.player.gain_xp(40)
                    return
                else:
                    print("Kaçamadın!")

            if enemy.health > 0:
                self.player.health -= enemy.attack_power
                print(f"{enemy.name} saldırdı, {enemy.attack_power} hasar aldın!")

        if self.player.health > 0:
            print(f"🎉 {enemy.name}'i yendin! 30 altın ve 40 XP kazandın.")
            self.player.gold += 30
            self.player.gain_xp(40)
        else:
            print("☠️ Maalesef yenildin...")

# Oyunu başlat
if __name__ == "__main__":
    game = Game()
    game.start()
