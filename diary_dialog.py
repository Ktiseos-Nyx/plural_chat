import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import os
import logging
from typing import List, Dict, Optional

try:
    from ttkbootstrap.tableview import Tableview
    HAS_TABLEVIEW = True
except ImportError:
    HAS_TABLEVIEW = False


class DiaryDialog:
    """Per-member diary dialog with modern UI"""
    
    def __init__(self, parent, system_db, members, app_db=None):
        self.parent = parent
        self.system_db = system_db
        self.members = members
        self.app_db = app_db
        self.current_entry_id = None
        self.logger = logging.getLogger('plural_chat.diary')
        
        self.create_window()
        self.setup_ui()
        self.load_entries()
    
    def create_window(self):
        """Create the diary window"""
        self.window = ttk.Toplevel(self.parent)
        self.window.title("📔 Member Diary")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Center on parent
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=2)
    
    def setup_ui(self):
        """Setup the main UI components"""
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        
        # Left panel - Entry list
        self.setup_entry_list(main_frame)
        
        # Right panel - Editor
        self.setup_editor(main_frame)
    
    def setup_entry_list(self, parent):
        """Setup the entry list on the left side"""
        left_frame = ttk.LabelFrame(parent, text="📝 Diary Entries", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Member selector
        member_frame = ttk.Frame(left_frame)
        member_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        member_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(member_frame, text="Member:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        self.member_var = tk.StringVar()
        self.member_combo = ttk.Combobox(member_frame, textvariable=self.member_var, 
                                       state="readonly", width=20)
        self.member_combo.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.member_combo['values'] = ['All Members'] + [m['name'] for m in self.members]
        self.member_combo.set('All Members')
        self.member_combo.bind('<<ComboboxSelected>>', self.on_member_changed)
        
        # Filter button
        ttk.Button(member_frame, text="🔍", width=3, 
                  command=self.show_search_dialog).grid(row=0, column=2)
        
        # Entry list
        if HAS_TABLEVIEW:
            self.setup_tableview(left_frame)
        else:
            self.setup_listbox(left_frame)
        
        # Entry list buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Button(button_frame, text="📄 New Entry", 
                  bootstyle="success", command=self.new_entry).pack(side=LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🗑️ Delete", 
                  bootstyle="danger-outline", command=self.delete_entry).pack(side=LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📤 Export", 
                  bootstyle="info-outline", command=self.export_diary).pack(side=LEFT)
    
    def setup_tableview(self, parent):
        """Setup the modern tableview for entries"""
        self.entry_table = Tableview(
            master=parent,
            coldata=[
                {"text": "Date", "width": 100},
                {"text": "Member", "width": 120},
                {"text": "Title", "width": 200},
                {"text": "Preview", "width": 250}
            ],
            rowdata=[],
            searchable=True,
            bootstyle="primary",
            paginated=True,
            pagesize=20,
            height=15
        )
        self.entry_table.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.entry_table.view.bind('<<TreeviewSelect>>', self.on_entry_selected)
    
    def setup_listbox(self, parent):
        """Fallback listbox if tableview isn't available"""
        list_frame = ttk.Frame(parent)
        list_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        self.entry_listbox = tk.Listbox(list_frame, font=("Consolas", 10))
        self.entry_listbox.grid(row=0, column=0, sticky="nsew")
        self.entry_listbox.bind('<<ListboxSelect>>', self.on_entry_selected)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.entry_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.entry_listbox.configure(yscrollcommand=scrollbar.set)
    
    def setup_editor(self, parent):
        """Setup the editor on the right side"""
        right_frame = ttk.LabelFrame(parent, text="✍️ Write Entry", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Entry info
        info_frame = ttk.Frame(right_frame)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        info_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Author:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.author_var = tk.StringVar()
        self.author_combo = ttk.Combobox(info_frame, textvariable=self.author_var, 
                                       state="readonly", width=20)
        self.author_combo.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.author_combo['values'] = [m['name'] for m in self.members]
        if self.members:
            self.author_combo.set(self.members[0]['name'])
        
        # Entry date/time (read-only display)
        self.date_label = ttk.Label(info_frame, text="", font=("Arial", 9), foreground="gray")
        self.date_label.grid(row=0, column=2, sticky="e")
        
        # Title
        title_frame = ttk.Frame(right_frame)
        title_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        title_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(title_frame, text="Title:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.title_entry = ttk.Entry(title_frame, font=("Arial", 12, "bold"))
        self.title_entry.grid(row=0, column=1, sticky="ew")
        
        # Content
        content_frame = ttk.Frame(right_frame)
        content_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Get font settings from parent app
        try:
            if self.app_db:
                font_family = self.app_db.get_setting('font_family', 'Consolas')
                font_size = int(self.app_db.get_setting('font_size', '11'))
            else:
                font_family = 'Consolas'
                font_size = 11
        except:
            font_family = 'Consolas'
            font_size = 11
        
        self.content_text = tk.Text(content_frame, wrap=tk.WORD, font=(font_family, font_size),
                                   undo=True, maxundo=20)
        self.content_text.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar for content
        content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", 
                                        command=self.content_text.yview)
        content_scrollbar.grid(row=0, column=1, sticky="ns")
        self.content_text.configure(yscrollcommand=content_scrollbar.set)
        
        # Word count
        self.word_count_label = ttk.Label(right_frame, text="Words: 0", 
                                        font=("Arial", 9), foreground="gray")
        self.word_count_label.grid(row=3, column=0, sticky="w", pady=(0, 5))
        
        # Bind text change to update word count
        self.content_text.bind('<KeyRelease>', self.update_word_count)
        
        # Editor buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=4, column=0, sticky="ew")
        
        ttk.Button(button_frame, text="💾 Save Entry", 
                  bootstyle="success", command=self.save_entry).pack(side=LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔄 Clear", 
                  bootstyle="warning-outline", command=self.clear_editor).pack(side=LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="❌ Close", 
                  bootstyle="secondary-outline", command=self.close_dialog).pack(side=RIGHT)
    
    def load_entries(self):
        """Load diary entries into the list"""
        member_name = self.member_var.get()
        
        if member_name == 'All Members':
            entries = self.system_db.get_diary_entries()
        else:
            member = next((m for m in self.members if m['name'] == member_name), None)
            if member:
                entries = self.system_db.get_diary_entries(member['id'])
            else:
                entries = []
        
        if HAS_TABLEVIEW:
            self.load_entries_tableview(entries)
        else:
            self.load_entries_listbox(entries)
    
    def load_entries_tableview(self, entries):
        """Load entries into the tableview"""
        rowdata = []
        for entry in entries:
            date_str = datetime.fromisoformat(entry['created_at']).strftime('%m/%d/%Y')
            preview = (entry['content'][:50] + '...') if len(entry['content']) > 50 else entry['content']
            preview = preview.replace('\n', ' ').replace('\r', ' ')
            
            rowdata.append([
                date_str,
                entry['member_name'],
                entry['title'] or '(No title)',
                preview
            ])
        
        self.entry_table.build_table_data(coldata=self.entry_table.get_columns(), rowdata=rowdata)
        self.entries_data = entries  # Store for selection
    
    def load_entries_listbox(self, entries):
        """Load entries into the fallback listbox"""
        self.entry_listbox.delete(0, tk.END)
        self.entries_data = entries
        
        for entry in entries:
            date_str = datetime.fromisoformat(entry['created_at']).strftime('%m/%d/%Y')
            title = entry['title'] or '(No title)'
            display_text = f"{date_str} - {entry['member_name']} - {title}"
            self.entry_listbox.insert(tk.END, display_text)
    
    def on_member_changed(self, event=None):
        """Handle member selection change"""
        self.load_entries()
        self.clear_editor()
    
    def on_entry_selected(self, event=None):
        """Handle entry selection"""
        if HAS_TABLEVIEW:
            selection = self.entry_table.get_rows(selected=True)
            if selection:
                selected_index = selection[0].iid
                try:
                    entry_index = int(selected_index)
                    if 0 <= entry_index < len(self.entries_data):
                        self.load_entry_for_editing(self.entries_data[entry_index])
                except (ValueError, IndexError):
                    pass
        else:
            selection = self.entry_listbox.curselection()
            if selection:
                entry_index = selection[0]
                if 0 <= entry_index < len(self.entries_data):
                    self.load_entry_for_editing(self.entries_data[entry_index])
    
    def load_entry_for_editing(self, entry):
        """Load an entry into the editor"""
        self.current_entry_id = entry['id']
        self.author_combo.set(entry['member_name'])
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, entry['title'] or '')
        
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, entry['content'])
        
        # Update date label
        created_date = datetime.fromisoformat(entry['created_at'])
        self.date_label.config(text=f"Created: {created_date.strftime('%m/%d/%Y %I:%M %p')}")
        
        self.update_word_count()
    
    def new_entry(self):
        """Start a new diary entry"""
        self.clear_editor()
        self.current_entry_id = None
        self.date_label.config(text="")
    
    def clear_editor(self):
        """Clear the editor fields"""
        self.current_entry_id = None
        self.title_entry.delete(0, tk.END)
        self.content_text.delete(1.0, tk.END)
        self.date_label.config(text="")
        self.update_word_count()
    
    def save_entry(self):
        """Save the current entry"""
        author_name = self.author_var.get()
        title = self.title_entry.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not author_name:
            messagebox.showerror("Error", "Please select an author.")
            return
        
        if not content:
            messagebox.showerror("Error", "Please enter some content.")
            return
        
        # Find member ID
        member = next((m for m in self.members if m['name'] == author_name), None)
        if not member:
            messagebox.showerror("Error", "Invalid member selected.")
            return
        
        try:
            if self.current_entry_id:
                # Update existing entry
                self.system_db.update_diary_entry(self.current_entry_id, title, content)
                self.logger.info(f"Updated diary entry {self.current_entry_id} for {author_name}")
            else:
                # Create new entry
                entry_id = self.system_db.add_diary_entry(member['id'], title, content)
                self.current_entry_id = entry_id
                self.logger.info(f"Created new diary entry {entry_id} for {author_name}")
            
            # Show success toast if available
            try:
                from ttkbootstrap.toast import ToastNotification
                toast = ToastNotification(
                    title="Entry Saved!",
                    message=f"Diary entry saved for {author_name}",
                    duration=3000,
                    bootstyle="success"
                )
                toast.show_toast()
            except ImportError:
                # Fallback to messagebox
                messagebox.showinfo("Success", "Entry saved successfully!")
            
            # Reload entries
            self.load_entries()
            
        except Exception as e:
            self.logger.error(f"Error saving diary entry: {e}")
            messagebox.showerror("Error", f"Failed to save entry: {str(e)}")
    
    def delete_entry(self):
        """Delete the selected entry"""
        if not self.current_entry_id:
            messagebox.showwarning("No Selection", "Please select an entry to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?"):
            try:
                self.system_db.delete_diary_entry(self.current_entry_id)
                self.logger.info(f"Deleted diary entry {self.current_entry_id}")
                
                # Show success toast
                try:
                    from ttkbootstrap.toast import ToastNotification
                    toast = ToastNotification(
                        title="Entry Deleted",
                        message="Diary entry has been deleted",
                        duration=3000,
                        bootstyle="warning"
                    )
                    toast.show_toast()
                except ImportError:
                    messagebox.showinfo("Success", "Entry deleted successfully!")
                
                self.clear_editor()
                self.load_entries()
                
            except Exception as e:
                self.logger.error(f"Error deleting diary entry: {e}")
                messagebox.showerror("Error", f"Failed to delete entry: {str(e)}")
    
    def export_diary(self):
        """Export diary entries to a text file"""
        member_name = self.member_var.get()
        
        if member_name == 'All Members':
            entries = self.system_db.get_diary_entries()
            filename_prefix = "AllMembers"
        else:
            member = next((m for m in self.members if m['name'] == member_name), None)
            if member:
                entries = self.system_db.get_diary_entries(member['id'])
                # Clean filename
                filename_prefix = member_name.replace(' ', '_').replace('[', '').replace(']', '').replace('/', '_')
            else:
                messagebox.showerror("Error", "Invalid member selected.")
                return
        
        if not entries:
            messagebox.showwarning("No Entries", "No diary entries to export.")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            title="Export Diary",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialname=f"{filename_prefix}_diary_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if member_name == 'All Members':
                    f.write("=== PLURAL CHAT DIARY EXPORT ===\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total entries: {len(entries)}\n\n")
                else:
                    f.write(f"=== {member_name}'s Diary ===\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total entries: {len(entries)}\n\n")
                
                for entry in reversed(entries):  # Chronological order
                    created_date = datetime.fromisoformat(entry['created_at'])
                    f.write(f"Date: {created_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Author: {entry['member_name']}\n")
                    if entry['title']:
                        f.write(f"Title: {entry['title']}\n")
                    f.write(f"{'='*60}\n")
                    f.write(f"{entry['content']}\n\n")
                    f.write(f"{'='*60}\n\n")
            
            # Show success toast
            try:
                from ttkbootstrap.toast import ToastNotification
                toast = ToastNotification(
                    title="Export Complete!",
                    message=f"Diary exported to {os.path.basename(filename)}",
                    duration=5000,
                    bootstyle="success"
                )
                toast.show_toast()
            except ImportError:
                messagebox.showinfo("Success", f"Diary exported successfully to {filename}")
            
            self.logger.info(f"Exported diary to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error exporting diary: {e}")
            messagebox.showerror("Error", f"Failed to export diary: {str(e)}")
    
    def show_search_dialog(self):
        """Show search dialog"""
        search_term = tk.simpledialog.askstring("Search", "Enter search term:", parent=self.window)
        if search_term:
            self.search_entries(search_term)
    
    def search_entries(self, search_term):
        """Search diary entries"""
        member_name = self.member_var.get()
        
        if member_name == 'All Members':
            entries = self.system_db.search_diary_entries(search_term)
        else:
            member = next((m for m in self.members if m['name'] == member_name), None)
            if member:
                entries = self.system_db.search_diary_entries(search_term, member['id'])
            else:
                entries = []
        
        if HAS_TABLEVIEW:
            self.load_entries_tableview(entries)
        else:
            self.load_entries_listbox(entries)
        
        # Show results count
        try:
            from ttkbootstrap.toast import ToastNotification
            toast = ToastNotification(
                title="Search Results",
                message=f"Found {len(entries)} entries matching '{search_term}'",
                duration=3000,
                bootstyle="info"
            )
            toast.show_toast()
        except ImportError:
            messagebox.showinfo("Search Results", f"Found {len(entries)} entries matching '{search_term}'")
    
    def update_word_count(self, event=None):
        """Update the word count display"""
        content = self.content_text.get(1.0, tk.END).strip()
        word_count = len(content.split()) if content else 0
        self.word_count_label.config(text=f"Words: {word_count}")
    
    def close_dialog(self):
        """Close the diary dialog"""
        self.window.destroy()
    
    def show(self):
        """Show the dialog"""
        self.window.focus_set()
        self.window.wait_window()