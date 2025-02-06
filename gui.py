# gui.py
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import os
import pandas as pd
import textwrap

from openai_client import OpenAIClient
from summarizer import get_python_files, Summarizer

class ModelFrame(ctk.CTkFrame):
    def __init__(self, master, openai_client, **kwargs):
        super().__init__(master, **kwargs)
        self.openai_client = openai_client
        self.configure(fg_color="transparent")
        
        # Bold label for MODEL
        self.model_label = ctk.CTkLabel(self, text="MODEL:", font=("Helvetica", 14, "bold"))
        self.model_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.model_var = tk.StringVar(value=self.openai_client.model)
        self.model_dropdown = ctk.CTkOptionMenu(self, variable=self.model_var, 
                                                 values=["text-davinci-003", "gpt-3.5-turbo"],
                                                 font=("Helvetica", 12))
        self.model_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.connect_button = ctk.CTkButton(self, text="Connect", command=self.connect_api,
                                            font=("Helvetica", 12))
        self.connect_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        self.status_label = ctk.CTkLabel(self, text="Not Connected", text_color="red",
                                         font=("Helvetica", 12))
        self.status_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
    def connect_api(self):
        model = self.model_var.get()
        self.openai_client.set_model(model)
        try:
            self.openai_client.connect()
            self.status_label.configure(text="Connected", text_color="green")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.status_label.configure(text="Not Connected", text_color="red")

class DirectoryFrame(ctk.CTkFrame):
    def __init__(self, master, directory_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.directory_callback = directory_callback
        self.configure(fg_color="transparent")
        
        # Bold label for DIRECTORY
        self.dir_label = ctk.CTkLabel(self, text="DIRECTORY:", font=("Helvetica", 14, "bold"))
        self.dir_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.directory_var = tk.StringVar(value="CHOSEN DIRECTORY: --- PLEASE CHOOSE A DIRECTORY ---")
        self.directory_entry = ctk.CTkEntry(self, textvariable=self.directory_var, width=500,
                                            font=("Helvetica", 12))
        self.directory_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.browse_button = ctk.CTkButton(self, text="Browse", command=self.browse_directory,
                                           font=("Helvetica", 12))
        self.browse_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
    def browse_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.directory_var.set(f"CHOSEN DIRECTORY: {dir_path}")
            self.directory_entry.configure(text_color="green")
            self.directory_callback(dir_path)
        else:
            self.directory_var.set("CHOSEN DIRECTORY: --- PLEASE CHOOSE A DIRECTORY ---")
            self.directory_entry.configure(text_color="red")

class ContentsFrame(ctk.CTkFrame):
    def __init__(self, master, openai_client, **kwargs):
        super().__init__(master, **kwargs)
        self.openai_client = openai_client
        self.summarizer = Summarizer(self.openai_client)
        self.current_directory = None
        
        # Bold label for CONTENTS section
        self.contents_label = ctk.CTkLabel(self, text="CONTENTS:", font=("Helvetica", 14, "bold"))
        self.contents_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        # Info frame for file count (at top of contents)
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="x", padx=5, pady=5)
        self.file_count_label = ctk.CTkLabel(self.info_frame, text="Files in Directory: 0",
                                             font=("Helvetica", 12))
        self.file_count_label.pack(side="left", padx=5)
        
        # Table frame for file list and summaries
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Set up a custom style for the Treeview to increase font size.
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Helvetica", 12))
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 12, "bold"))
        self.tree = ttk.Treeview(self.table_frame, columns=("File", "Summary"),
                                 show="headings", style="Custom.Treeview")
        self.tree.heading("File", text="File")
        self.tree.heading("Summary", text="Summary")
        self.tree.column("File", width=200)
        self.tree.column("Summary", width=500)
        self.tree.pack(fill="both", expand=True)
        
        # Bottom frame for buttons and summary prompt
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Left: Vertical stack of action buttons
        self.button_frame = ctk.CTkFrame(self.bottom_frame)
        self.button_frame.grid(row=0, column=0, sticky="n", padx=5)
        
        self.summarize_all_button = ctk.CTkButton(self.button_frame, text="Summarize All",
                                                  command=self.summarize_all, font=("Helvetica", 12))
        self.summarize_all_button.pack(fill="x", pady=(0, 5))
        
        self.summarize_selected_button = ctk.CTkButton(self.button_frame, text="Summarize Selected",
                                                       command=self.summarize_selected, font=("Helvetica", 12))
        self.summarize_selected_button.pack(fill="x", pady=(0, 5))
        
        self.edit_button = ctk.CTkButton(self.button_frame, text="Edit",
                                         command=self.edit_summary, font=("Helvetica", 12))
        self.edit_button.pack(fill="x", pady=(0, 5))
        
        # Right: Summary prompt label and text box (spanning the height of the left stack)
        self.prompt_frame = ctk.CTkFrame(self.bottom_frame)
        self.prompt_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        self.bottom_frame.columnconfigure(1, weight=1)
        
        self.prompt_label = ctk.CTkLabel(self.prompt_frame, text="Summary Prompt:",
                                         font=("Helvetica", 12, "bold"))
        self.prompt_label.pack(anchor="w", pady=(0, 5))
        
        # Default prompt text
        self.default_prompt = ("Please provide a concise summary of the following Python code:\n\n"
                               "{code}\n\nSummary:")
        self.prompt_textbox = ctk.CTkTextbox(self.prompt_frame, font=("Helvetica", 12))
        self.prompt_textbox.pack(fill="both", expand=True)
        self.prompt_textbox.insert("0.0", self.default_prompt)
        # (Optional: adjust the fg_color or placeholder behavior to indicate default text.)
        
        # Save button at the bottom right of the overall contents area
        self.save_button = ctk.CTkButton(self, text="Save",
                                         command=self.save_summaries, font=("Helvetica", 12))
        self.save_button.pack(anchor="e", padx=5, pady=5)
        
    def populate_table(self, directory):
        self.current_directory = directory
        files = get_python_files(directory)
        self.tree.delete(*self.tree.get_children())
        for file_path in files:
            file_name = os.path.basename(file_path)
            # Initially, set the summary cell to "none"
            self.tree.insert("", "end", iid=file_path, values=(file_name, "none"))
        self.file_count_label.configure(text=f"Files in Directory: {len(files)}")
        
    def wrap_text(self, text, width=60):
        """Wrap text to a specified character width for multi-line display."""
        return "\n".join(textwrap.wrap(text, width=width))
    
    def summarize_all(self):
        for file_path in self.tree.get_children():
            self.tree.set(file_path, column="Summary", value="Generating...")
            threading.Thread(target=self.summarize_file_thread, args=(file_path,), daemon=True).start()
            
    def summarize_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a file to summarize.")
            return
        file_path = selected[0]
        self.tree.set(file_path, column="Summary", value="Generating...")
        threading.Thread(target=self.summarize_file_thread, args=(file_path,), daemon=True).start()
        
    def summarize_file_thread(self, file_path):
        # Here you could modify the prompt using the custom text from prompt_textbox if desired.
        summary = self.summarizer.summarize_file(file_path)
        wrapped_summary = self.wrap_text(summary, width=60)
        self.tree.after(0, lambda: self.tree.set(file_path, column="Summary", value=wrapped_summary))
        
    def edit_summary(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a file to edit.")
            return
        file_path = selected[0]
        current_summary = self.tree.set(file_path, "Summary")
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Edit Summary")
        edit_text = ctk.CTkTextbox(edit_win, width=600, height=200, font=("Helvetica", 12))
        edit_text.pack(padx=10, pady=10)
        edit_text.insert("0.0", current_summary)
        def save_edit():
            new_summary = edit_text.get("0.0", "end").strip()
            self.tree.set(file_path, "Summary", value=new_summary)
            edit_win.destroy()
        save_button = ctk.CTkButton(edit_win, text="Save", command=save_edit, font=("Helvetica", 12))
        save_button.pack(pady=5)
        
    def save_summaries(self):
        items = self.tree.get_children()
        data = []
        for item in items:
            file_name = self.tree.set(item, "File")
            summary = self.tree.set(item, "Summary")
            data.append({"File": file_name, "Summary": summary})
        df = pd.DataFrame(data)
        save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV Files", "*.csv")])
        if save_path:
            df.to_csv(save_path, index=False)
            messagebox.showinfo("Saved", f"Summaries saved to {save_path}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Python File Summarizer")
        self.geometry("1000x800")
        
        self.openai_client = OpenAIClient()
        
        self.model_frame = ModelFrame(self, self.openai_client)
        self.model_frame.pack(fill="x", padx=10, pady=5)
        
        self.directory_frame = DirectoryFrame(self, self.directory_selected)
        self.directory_frame.pack(fill="x", padx=10, pady=5)
        
        self.contents_frame = ContentsFrame(self, self.openai_client)
        self.contents_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
    def directory_selected(self, directory):
        self.contents_frame.populate_table(directory)

if __name__ == "__main__":
    app = App()
    app.mainloop()
