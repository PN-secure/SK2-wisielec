import tkinter as tk
from tkinter import messagebox, ttk
import socket
import threading


class WisielecGUI:     
    def __init__(self, root):
        self.root = root
        self.root.title("Gra Wisielec - Multiplayer")
        self.root.geometry("800x650")
        self.root.resizable(False, False)
        
        self.socket = None
        self. connected = False
        self.game_started = False
        
        self.my_client_number = None
        self.target_word = None
        self. total_clients = 0
        self.used_letters = set()
        
        self.players = {}  # {numer_gracza: {"chances": int, "guessed": set(), "lost": bool, "tried": set(), "disconnected": bool}}
        
        self.game_frame = None
        
        self.lock = threading. Lock()
        
        self.create_connection_screen()
    
    def create_connection_screen(self):
        self.connection_frame = tk.Frame(self.root, bg="#2C3E50")
        self.connection_frame.pack(fill=tk. BOTH, expand=True)
        
        title_label = tk.Label(
            self. connection_frame, 
            text="Gra Wisielec - Multiplayer", 
            font=("Arial", 24, "bold"),
            bg="#2C3E50",
            fg="#ECF0F1"
        )
        title_label.pack(pady=50)
        
        input_frame = tk.Frame(self.connection_frame, bg="#2C3E50")
        input_frame.pack(pady=20)
        
        # IP
        tk.Label(
            input_frame, 
            text="Adres IP:", 
            font=("Arial", 14),
            bg="#2C3E50",
            fg="#ECF0F1"
        ).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.ip_entry = tk.Entry(input_frame, font=("Arial", 14), width=20)
        self.ip_entry.grid(row=0, column=1, padx=10, pady=10)
        self.ip_entry.insert(0, "127.0.0.1")
        
        # Port
        tk.Label(
            input_frame, 
            text="Port:", 
            font=("Arial", 14),
            bg="#2C3E50",
            fg="#ECF0F1"
        ).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        self. port_entry = tk.Entry(input_frame, font=("Arial", 14), width=20)
        self.port_entry. grid(row=1, column=1, padx=10, pady=10)
        self.port_entry.insert(0, "5555")
        
        connect_btn = tk.Button(
            self.connection_frame,
            text="Połącz",
            font=("Arial", 16, "bold"),
            bg="#27AE60",
            fg="white",
            activebackground="#229954",
            padx=30,
            pady=10,
            command=self.connect_to_server
        )
        connect_btn.pack(pady=30)
        
        # Status
        self.status_label = tk.Label(
            self. connection_frame,
            text="",
            font=("Arial", 12),
            bg="#2C3E50",
            fg="#E74C3C"
        )
        self.status_label. pack(pady=10)
    
    def connect_to_server(self):
        ip = self.ip_entry.get().strip()
        port_str = self.port_entry. get().strip()
        
        if not ip or not port_str:
            self.status_label.config(text="Wprowadź adres IP i port!")
            return
        
        try:
            port = int(port_str)
        except ValueError:  
            self.status_label.config(text="Port musi być liczbą!")
            return
        
        try:    
            self.socket = socket. socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            self.connected = True
            self. status_label.config(text="Połączono!  Oczekiwanie na start gry.. .", fg="#27AE60")
            
            listen_thread = threading.Thread(target=self.listen_to_server, daemon=True)
            listen_thread.start()
            
        except Exception as e:
            self.status_label.config(text=f"Błąd połączenia: {e}", fg="#E74C3C")
    
    def listen_to_server(self):
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.process_message(line. strip())
                    
            except Exception as e:  
                print(f"Błąd odbierania: {e}")
                break
        
        self.connected = False
    
    def process_message(self, message):
        if not message:  
            return
        
        parts = message.split()
        
        if parts[0] == "start" and len(parts) >= 4:
            self.my_client_number = int(parts[1])
            self.target_word = parts[2].upper()
            self.total_clients = int(parts[3])
            
            with self.lock:
                for i in range(1, self. total_clients + 1):
                    self.players[i] = {
                        "chances":  10,
                        "guessed": set(),
                        "lost": False,
                        "tried": set(),
                        "disconnected": False  
                    }
            
            self.root.after(0, self.create_game_screen)
        
        elif parts[0] == "wygralem" and len(parts) >= 2:
            winner = int(parts[1])
            self.root.after(0, lambda: self.show_winner(winner))
        
        elif parts[0] == "utracono" and len(parts) >= 2:
            disconnected_client = int(parts[1])
            with self.lock:
                if disconnected_client in self.players:
                    self.players[disconnected_client]["disconnected"] = True
            self.root.after(0, self.refresh_game_screen)
        
        elif len(parts) == 2:
            try:  
                client_num = int(parts[0])
                letter = parts[1].upper()
                
                self.root.after(0, lambda c=client_num, l=letter:  self.process_player_move(c, l))
            except ValueError:
                pass
    
    def create_game_screen(self):
        self.game_started = True
        
        self.connection_frame.destroy()
        
        self.game_frame = tk.Frame(self.root, bg="#34495E")
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        
        header = tk.Label(
            self.game_frame,
            text=f"Jesteś graczem #{self.my_client_number}",
            font=("Arial", 20, "bold"),
            bg="#34495E",
            fg="#ECF0F1"
        )
        header.pack(pady=20)
        
        self.players_container = tk.LabelFrame(
            self.game_frame,
            text="Postępy Graczy",
            font=("Arial", 14, "bold"),
            bg="#34495E",
            fg="#ECF0F1",
            relief=tk.RIDGE,
            bd=2
        )
        self.players_container.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        canvas = tk. Canvas(self.players_container, bg="#34495E", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.players_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk. Frame(canvas, bg="#34495E")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar. set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.update_players_display()
        
        instruction_frame = tk.Frame(self. game_frame, bg="#34495E")
        instruction_frame. pack(padx=20, pady=10)
        
        tk.Label(
            instruction_frame,
            text="⌨️ wpisz literę na klawiaturze",
            font=("Arial", 14, "bold"),
            bg="#354A5F",
            fg="#F39C12"
        ).pack()
        
        self.used_letters_frame = tk.LabelFrame(
            self.game_frame,
            text="miłej gry :3",
            font=("Arial", 12, "bold"),
            bg="#34495E",
            fg="#ECF0F1"
        )
        self.used_letters_frame.pack(padx=20, pady=5)
        
        self.used_letters_label = tk.Label(
            self.used_letters_frame,
            text="Brak",
            font=("Arial", 12),
            bg="#34495E",
            fg="#95A5A6",
            wraplength=700
        )
        self.used_letters_label.pack(padx=10, pady=5)

        self.root.bind('<KeyPress>', self.on_key_press)
        
        self.root.focus_set()
    
    def on_key_press(self, event):
        if not self.game_started:
            return
        
        char = event.char. upper()
        
        polish_letters = "AĄBCĆDEĘFGHIJKLŁMNŃOÓPQRSŚTUVWXYZŹŻ"
        
        if char in polish_letters:    
            self.select_letter(char)
    
    def update_players_display(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        with self.lock:
            players_copy = dict(self.players)
        
        for player_num in sorted(players_copy.keys()):
            player_info = players_copy[player_num]
            
            player_frame = tk.Frame(self. scrollable_frame, bg="#2C3E50", relief=tk.RAISED, bd=2)
            player_frame.pack(padx=10, pady=5, fill=tk.X)
            
            if player_num == self. my_client_number:
                player_text = f"Gracz #{player_num} (TY)"
                color = "#3498DB"
            else:  
                player_text = f"Gracz #{player_num}"
                color = "#95A5A6"
            
            tk.Label(
                player_frame,
                text=player_text,
                font=("Arial", 12, "bold"),
                bg="#2C3E50",
                fg=color
            ).pack(anchor="w", padx=10, pady=5)
            
            if player_info["disconnected"]:
                status_text = "🔌 Utracono połączenie"
                status_color = "#E67E22" 
            elif player_info["lost"]: 
                status_text = "❌ PRZEGRAŁ"
                status_color = "#E74C3C"
            else:
                status_text = f"❤️ Szanse: {player_info['chances']}"
                status_color = "#27AE60"
            
            tk.Label(
                player_frame,
                text=status_text,
                font=("Arial", 11),
                bg="#2C3E50",
                fg=status_color
            ).pack(anchor="w", padx=10)
            
            word_display = self.get_word_display(player_info["guessed"])
            tk.Label(
                player_frame,
                text=f"Hasło: {word_display}",
                font=("Arial", 14, "bold"),
                bg="#2C3E50",
                fg="#ECF0F1"
            ).pack(anchor="w", padx=10, pady=5)
            
            if player_info["tried"]:
                tried_letters = sorted(list(player_info["tried"]))
                tried_display = " ".join(tried_letters)
                tried_color = "#95A5A6"
            else:
                tried_display = "Brak"
                tried_color = "#7F8C8D"
            
            tried_frame = tk.Frame(player_frame, bg="#2C3E50")
            tried_frame.pack(anchor="w", padx=10, pady=2)
            
            tk.Label(
                tried_frame,
                text="Sprawdzone litery:  ",
                font=("Arial", 10),
                bg="#2C3E50",
                fg="#BDC3C7"
            ).pack(side=tk.LEFT)
            
            tk.Label(
                tried_frame,
                text=tried_display,
                font=("Arial", 10, "bold"),
                bg="#2C3E50",
                fg=tried_color
            ).pack(side=tk.LEFT)
    
    def get_word_display(self, guessed_letters):
        return " ".join([letter if letter in guessed_letters else "_" for letter in self.target_word])
    
    def update_used_letters_display(self):
        if self.used_letters:  
            sorted_letters = sorted(list(self.used_letters))
            self.used_letters_label.config(
                text=" ".join(sorted_letters),
                fg="#ECF0F1"
            )
        else:
            self.used_letters_label.config(
                text="Brak",
                fg="#95A5A6"
            )
    
    def select_letter(self, letter):
        if letter in self.used_letters:
            return
        
        with self.lock:
            if self.players[self.my_client_number]["lost"]:
                return
        
        self.used_letters.add(letter)
        self.update_used_letters_display()
        
        message = f"{self.my_client_number} {letter}\n"
        try:
            self.socket.sendall(message.encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wysłać:  {e}")
            return

        with self.lock:
            self.players[self.my_client_number]["tried"].add(letter)
            
            if letter in self. target_word:
                self.players[self.my_client_number]["chances"] += 1
                self.players[self.my_client_number]["guessed"].add(letter)
            else:
                self.players[self.my_client_number]["chances"] -= 1
            
            if self.players[self.my_client_number]["chances"] <= 0:
                self.players[self.my_client_number]["lost"] = True
                self.root.after(0, lambda: messagebox.showwarning("Koniec gry", "Przegrałeś!  Oglądasz dalsze postępy innych graczy."))
            
            if all(letter in self.players[self.my_client_number]["guessed"] for letter in self.target_word):
                win_message = f"wygralem {self.my_client_number}\n"
                try:
                    self.socket. sendall(win_message.encode('utf-8'))
                except:      
                    pass
                self.root.after(0, lambda: self.show_winner(self.my_client_number))
                return
        
        self. refresh_game_screen()
    
    def process_player_move(self, client_num, letter):
        if client_num not in self.players:
            return
        
        with self.lock:
            if client_num == self.my_client_number:
                return
            
            self.players[client_num]["tried"].add(letter)
            
            if letter in self.target_word:
                self.players[client_num]["chances"] += 1
                self.players[client_num]["guessed"].add(letter)
            else:
                self.players[client_num]["chances"] -= 1
            
            if self.players[client_num]["chances"] <= 0:
                self.players[client_num]["lost"] = True
        
        self. refresh_game_screen()
    
    def refresh_game_screen(self):
        if self.game_started:
            self.update_players_display()
    
    def show_winner(self, winner_num):
        if winner_num == self. my_client_number:
            message = "Gratulacje! Wygrałeś!"
            title = "Zwycięstwo!"
        else:
            message = f"Gracz #{winner_num} wygrał grę!"
            title = "Koniec gry"
        
        messagebox.showinfo(title, message)
        self.root.quit()
    
    def on_closing(self):
        self. connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WisielecGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":      
    main()