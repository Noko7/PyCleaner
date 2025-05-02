# src/Delete.py

import os
import shutil
import ctypes
from pathlib import Path
from tkinter import messagebox
import winreg  # <-- Added for registry deletion

class DeleteFiles:
    def __init__(self, scan_results, checkboxes):
        self.scan_results = scan_results
        self.checkboxes = checkboxes
        self.total_freed = 0
        self.registry_cleaned_count = 0  # <-- Track deleted registry keys

    def delete_selected(self):
        total_freed = 0

        for label, var in self.checkboxes.items():
            if var.get() and label in self.scan_results:
                target_data = self.scan_results[label]

                # Handle Registry Junk specially
                if label == "Registry Junk":
                    self.registry_cleaned_count = self._delete_registry_keys(
                        target_data.get("details", [])
                    )
                    print(f"[Registry Junk] Deleted {self.registry_cleaned_count} orphaned registry keys.")
                    continue

                target_path = target_data["path"]
                total_freed += self._delete_files_from_directory(target_path)

        self.total_freed = total_freed
        return total_freed

    def _delete_files_from_directory(self, path):
        total_freed = 0
        if not os.path.exists(path):
            return total_freed

        if not self._has_write_permission(path):
            messagebox.showerror("Permission Error", f"Cannot delete from {path}. Insufficient permissions.")
            return total_freed

        try:
            for root, dirs, files in os.walk(path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        total_freed += file_size
                    except (PermissionError, FileNotFoundError) as e:
                        print(f"[Error] Failed to delete file {file_path}: {e}")
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path)
                    except (PermissionError, FileNotFoundError) as e:
                        print(f"[Error] Failed to delete directory {dir_path}: {e}")
        except Exception as e:
            print(f"[Error] General deletion error in {path}: {e}")

        return total_freed

    def _delete_registry_keys(self, junk_entries):
        deleted = 0
        uninstall_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, uninstall_path, 0, winreg.KEY_ALL_ACCESS) as base_key:
                index = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(base_key, index)
                        subkey_path = uninstall_path + "\\" + subkey_name
                        with winreg.OpenKey(base_key, subkey_name) as subkey:
                            try:
                                display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            except FileNotFoundError:
                                display_name = f"Unnamed Key {subkey_name}"

                            if any(display_name in entry for entry in junk_entries):
                                winreg.DeleteKey(base_key, subkey_name)
                                deleted += 1
                                continue  # Don't increment index if we deleted a key
                        index += 1
                    except OSError:
                        break
        except Exception as e:
            print(f"[Registry Deletion Error] {e}")
        return deleted

    def _has_write_permission(self, path):
        try:
            test_file = os.path.join(path, "test_permission.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except (PermissionError, FileNotFoundError):
            return False
        except Exception as e:
            print(f"[Error] Permission check failed for {path}: {e}")
            return False

    def confirm_deletion(self):
        return messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete the selected files and folders?"
        )

    def show_results(self):
        human_readable_size = self._human_readable_size(self.total_freed)
        messagebox.showinfo("Cleanup Complete", f"🧹 Successfully freed {human_readable_size} of space.")

    def _human_readable_size(self, size, decimal_places=2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024
        return f"{size:.{decimal_places}f} PB"
