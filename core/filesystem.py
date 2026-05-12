import os

class VirtualFileSystem:
    """Simulates a stateful Linux filesystem structure."""
    def __init__(self):
        self.tree = {
            "/": ["bin", "etc", "home", "var", "tmp", "root", "proc"],
            "/etc": ["passwd", "shadow", "hosts", "ssh", "network"],
            "/home": ["web-admin", "guest"],
            "/home/web-admin": [".bashrc", ".ssh", "projects", "logs"],
            "/var": ["log", "www", "mail"],
            "/tmp": [".X11-unix"],
            "/root": [".bashrc", ".ssh"]
        }
        self.current_path = "/home/web-admin"

    def change_directory(self, path: str) -> str:
        if path == "..":
            if self.current_path != "/":
                self.current_path = os.path.dirname(self.current_path) or "/"
        elif path.startswith("/"):
            if path in self.tree:
                self.current_path = path
        else:
            potential = os.path.join(self.current_path, path).rstrip("/")
            if potential in self.tree:
                self.current_path = potential
        return self.current_path

    def list_dir(self) -> str:
        items = self.tree.get(self.current_path, [])
        return "  ".join(items)

    def get_pwd(self) -> str:
        return self.current_path