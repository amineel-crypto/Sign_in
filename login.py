import customtkinter as ctk
import hashlib

# --- Fonction pour hasher le mot de passe ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Utilisateur admin prédéfini ---
ADMIN_USER = "admin"
ADMIN_PASS_HASH = hash_password("password123")  # Mot de passe par défaut

# --- Fenêtre de Login ---
class LoginApp(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("Login - Healthcare Dashboard")
        self.geometry("400x300")
        self.resizable(False, False)

        # Titre
        title = ctk.CTkLabel(self, text="🩺 Connexion Administrateur", font=("Helvetica", 18, "bold"))
        title.pack(pady=20)

        # Champ utilisateur
        self.username = ctk.CTkEntry(self, placeholder_text="Nom d'utilisateur")
        self.username.pack(pady=10, padx=20, fill="x")

        # Champ mot de passe
        self.password = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*")
        self.password.pack(pady=10, padx=20, fill="x")

        # Bouton de connexion
        self.login_button = ctk.CTkButton(self, text="Se connecter", command=self.check_login, fg_color="#4CAF50")
        self.login_button.pack(pady=10)

        # Message d'erreur
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=5)

    def check_login(self):
        user = self.username.get()
        pwd = self.password.get()

        if user == ADMIN_USER and hash_password(pwd) == ADMIN_PASS_HASH:
            self.destroy()
            self.on_success()  # Ouvrir le dashboard
        else:
            self.error_label.configure(text="Identifiants incorrects")

# --- Lancer l'application dashboard ---
def open_dashboard():
    import visualiation # Supposons que votre dashboard est dans 'healthcare_dashboard.py'

if __name__ == "__main__":
    app = LoginApp(open_dashboard)
    app.mainloop()