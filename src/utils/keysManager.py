from typing import Any

class KeysManager:
    def __init__(self):
        self.keys = {}

    def add_key(self, key_name, key_value):
        """Add a new key to the manager."""
        self.keys[key_name] = key_value

    def get_key(self, key_name):
        """Retrieve a key by its name."""
        return self.keys.get(key_name)

    def get_all_keys(self):
        """Return a dictionary of all keys and their values."""
        return self.keys.copy()

    def remove_key(self, key_name):
        """Remove a key from the manager."""
        if key_name in self.keys:
            del self.keys[key_name]

    def list_keys(self):
        """List all keys managed by the KeysManager."""
        return list(self.keys.keys())

    def clear_keys(self):
        """Clear all keys from the manager."""
        self.keys.clear()

    def key_exists(self, key_name):
        """Check if a key exists in the manager."""
        return key_name in self.keys

    def update_key(self, key_name, new_value):
        """Update the value of an existing key."""
        if key_name in self.keys:
            self.keys[key_name] = new_value
        else:
            raise KeyError(f"Key '{key_name}' does not exist.")