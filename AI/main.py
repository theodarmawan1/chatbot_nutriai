import tkinter as tk
from tkinter import messagebox, scrolledtext
import time
import os
import json
from generate_response import generate_meal_plan, welcome_message
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import threading

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartMealPlanner Chat")
        self.root.geometry("700x600")

        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', font=("Consolas", 12))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=5, fill=tk.X)

        self.input_field = tk.Entry(self.input_frame, font=("Consolas", 12))
        self.input_field.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        self.input_field.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=10)

        self.menu_bar = tk.Menu(self.root)
        self.history_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.history_menu.add_command(label="New Chat", command=self.start_new_chat)
        self.load_history_menu()
        self.menu_bar.add_cascade(label="History", menu=self.history_menu)
        self.root.config(menu=self.menu_bar)

        self.counter = 1
        self.chat_id = self.get_new_chat_id()
        self.chat_history = []
        self.display_bot_message(welcome_message)

    def get_new_chat_id(self):
        chat_id = f"chat-{self.counter}-{time.strftime('%Y%m%d%H%M%S')}"
        self.counter += 1
        return chat_id

    def start_new_chat(self):
        self.chat_id = self.get_new_chat_id()
        self.chat_display.config(state='normal')
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state='disabled')
        self.chat_history = []
        self.display_bot_message(welcome_message)

    def load_history_menu(self):
        self.history_menu.add_separator()
        if not os.path.exists("history"):
            os.makedirs("history")
        for fname in sorted(os.listdir("history")):
            if fname.endswith(".json"):
                chat_id = fname.replace(".json", "")
                self.history_menu.add_command(label=chat_id, command=lambda cid=chat_id: self.load_chat(cid))

    def load_chat(self, chat_id):
        path = os.path.join("history", f"{chat_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.chat_history = json.load(f)
            self.chat_id = chat_id
            self.chat_display.config(state='normal')
            self.chat_display.delete('1.0', tk.END)
            for entry in self.chat_history:
                self.chat_display.insert(tk.END, f"{entry['sender']} ({entry['time']}):\n{entry['message']}\n\n")
            self.chat_display.config(state='disabled')

    def save_message(self, sender, message):
        entry = {
            "sender": sender,
            "time": time.strftime("%H:%M"),
            "message": message
        }
        self.chat_history.append(entry)
        if not os.path.exists("history"):
            os.makedirs("history")
        with open(os.path.join("history", f"{self.chat_id}.json"), "w") as f:
            json.dump(self.chat_history, f, indent=2)

    def send_message(self, event=None):
        user_message = self.input_field.get().strip()
        if user_message == "":
            return
        self.display_user_message(user_message)
        self.save_message("You", user_message)
        self.input_field.delete(0, tk.END)
        threading.Thread(target=self.get_bot_response, args=(user_message,)).start()

    def display_user_message(self, message):
        self.chat_display.config(state='normal')
        timestamp = time.strftime("%H:%M")
        self.chat_display.insert(tk.END, f"You ({timestamp}):\n{message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def display_bot_message(self, message):
        self.chat_display.config(state='normal')
        timestamp = time.strftime("%H:%M")
        self.chat_display.insert(tk.END, f"Bot ({timestamp}):\n{message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)
        self.save_message("Bot", message)

    def get_bot_response(self, user_input):
        response = generate_meal_plan(user_input)
        if isinstance(response, tuple):
            message, chart_file = response
            self.display_bot_message(message)
            self.ask_show_chart(chart_file)
        else:
            self.display_bot_message(response)

    def ask_show_chart(self, filename):
        answer = messagebox.askyesno("View Chart", "Do you want to view the nutrition chart?")
        if answer:
            try:
                img = mpimg.imread(filename)
                plt.imshow(img)
                plt.axis('off')
                plt.title("Meal Plan Nutrition Chart")
                plt.show()
            except Exception as e:
                messagebox.showerror("Error", f"Unable to display chart.\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
