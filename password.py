import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import os
import json

def generate_key():
    return Fernet.generate_key()

def load_key():
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    else:
        key = generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
        return key

def encrypt_message(message, key):
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message

key = load_key()

def save_password():
    service = service_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if not service or not username or not password:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    encrypted_password = encrypt_message(password, key)
    new_data = {service: {"username": username, "password": encrypted_password.decode()}}

    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            try:
                existing_data = json.load(file)
            except (json.JSONDecodeError, TypeError):
                existing_data = {}
        existing_data.update(new_data)
    else:
        existing_data = new_data

    with open("passwords.json", "w") as file:
        try:
            json.dump(existing_data, file, indent=4)
        except TypeError as e:
            messagebox.showerror("Serialization Error", f"Error serializing data: {e}")

    service_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    messagebox.showinfo("Success", "Password saved successfully!")

def view_passwords():
    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

        result = ""
        if data:
            for service, info in data.items():
                username = info.get("username", "N/A")
                password = info.get("password", "")
                decrypted_password = decrypt_message(password.encode(), key)
                result += f"Service: {service}\nUsername: {username}\nPassword: {decrypted_password}\n\n"
        else:
            result = "No passwords stored yet."

        messagebox.showinfo("Stored Passwords", result)
    else:
        messagebox.showinfo("No Data", "No passwords stored yet.")


root = tk.Tk()
root.title("Password Manager")

tk.Label(root, text="Service").grid(row=0, column=0, padx=10, pady=10)
tk.Label(root, text="Username").grid(row=1, column=0, padx=10, pady=10)
tk.Label(root, text="Password").grid(row=2, column=0, padx=10, pady=10)

service_entry = tk.Entry(root, width=50)
service_entry.grid(row=0, column=1, padx=10, pady=10)

username_entry = tk.Entry(root, width=50)
username_entry.grid(row=1, column=1, padx=10, pady=10)

password_entry = tk.Entry(root, width=50, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Button(root, text="Save Password", command=save_password).grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(root, text="View Passwords", command=view_passwords).grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
