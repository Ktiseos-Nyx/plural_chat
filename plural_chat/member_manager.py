
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class MemberManager(ttk.Frame):
    def __init__(self, parent_frame, main_app):
        super().__init__(parent_frame)
        self.main_app = main_app
        self.members = self.main_app.members

        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Member List ---
        list_frame = ttk.LabelFrame(main_frame, text="Members", padding=5)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.member_listbox = tk.Listbox(list_frame)
        self.member_listbox.pack(fill=tk.BOTH, expand=True)
        self.member_listbox.bind("<<ListboxSelect>>", self.on_member_select)

        # --- Form ---
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Name
        ttk.Label(form_frame, text="Name:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.pack(anchor=tk.W, pady=(0, 10))

        # Avatar
        ttk.Label(form_frame, text="Avatar Path:").pack(anchor=tk.W)
        self.avatar_entry = ttk.Entry(form_frame, width=30)
        self.avatar_entry.pack(anchor=tk.W, pady=(0, 20))

        # --- Buttons ---
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X)

        add_button = ttk.Button(button_frame, text="Add", command=self.add_member)
        add_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        update_button = ttk.Button(button_frame, text="Update", command=self.update_member)
        update_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        remove_button = ttk.Button(form_frame, text="Remove Selected", command=self.remove_member)
        remove_button.pack(fill=tk.X, pady=(10, 0))

        self.populate_list()

    def populate_list(self):
        self.member_listbox.delete(0, tk.END)
        for member in self.members:
            self.member_listbox.insert(tk.END, member['name'])

    def on_member_select(self, event=None):
        selection_indices = self.member_listbox.curselection()
        if not selection_indices:
            return

        selected_index = selection_indices[0]
        member = self.members[selected_index]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, member['name'])
        self.avatar_entry.delete(0, tk.END)
        self.avatar_entry.insert(0, member['avatar'])

    def add_member(self):
        name = self.name_entry.get()
        avatar = self.avatar_entry.get()

        if not name:
            messagebox.showerror("Error", "Name cannot be empty.", parent=self)
            return

        if any(m['name'] == name for m in self.members):
            messagebox.showerror("Error", "A member with this name already exists.", parent=self)
            return

        self.members.append({'name': name, 'avatar': avatar})
        self.populate_list()
        self.clear_form()

    def update_member(self):
        selection_indices = self.member_listbox.curselection()
        if not selection_indices:
            messagebox.showinfo("Info", "Select a member to update.", parent=self)
            return

        selected_index = selection_indices[0]
        name = self.name_entry.get()
        avatar = self.avatar_entry.get()

        if not name:
            messagebox.showerror("Error", "Name cannot be empty.", parent=self)
            return

        # Check for name conflict, excluding the current member
        for i, member in enumerate(self.members):
            if member['name'] == name and i != selected_index:
                messagebox.showerror("Error", "A member with this name already exists.", parent=self)
                return

        self.members[selected_index] = {'name': name, 'avatar': avatar}
        self.populate_list()
        self.member_listbox.selection_set(selected_index) # Keep selection

    def remove_member(self):
        selection_indices = self.member_listbox.curselection()
        if not selection_indices:
            messagebox.showinfo("Info", "Select a member to remove.", parent=self)
            return

        selected_index = selection_indices[0]
        member_name = self.members[selected_index]['name']
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove {member_name}?", parent=self):
            del self.members[selected_index]
            self.populate_list()
            self.clear_form()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.avatar_entry.delete(0, tk.END)
        self.member_listbox.selection_clear(0, tk.END)

    def on_save_and_close(self):
        # Save changes back to the main app's list and file
        self.main_app.members = self.members
        self.main_app.save_members()
        self.main_app.load_members() # Reload in main window

