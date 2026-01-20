"""
Settings Repository - manages application key-value settings.
"""

from typing import Dict, Optional

from mfdp_app.db.base_repository import BaseRepository


class SettingsRepository(BaseRepository):
    """Handle all settings-related database operations."""
    
    @staticmethod
    def load_settings() -> Dict[str, str]:
        """
        Load all application settings from database.
        
        Returns:
            Dictionary of key-value settings
        """
        rows = BaseRepository.execute_query(
            "SELECT key, value FROM settings",
            fetch_all=True
        )
        
        settings = {}
        if rows:
            for row in rows:
                settings[row['key']] = row['value']
        
        return settings
    
    @staticmethod
    def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a single setting by key.
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist
        
        Returns:
            Setting value or default
        """
        row = BaseRepository.execute_query(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
            fetch_one=True
        )
        
        return row['value'] if row else default
    
    @staticmethod
    def save_setting(key: str, value: str) -> bool:
        """
        Save or update a setting.
        
        Args:
            key: Setting key
            value: Setting value
        
        Returns:
            True if successful, False otherwise
        """
        return BaseRepository.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, str(value)),
            commit=True
        ) is not None
    
    @staticmethod
    def delete_setting(key: str) -> bool:
        """
        Delete a setting by key.
        
        Args:
            key: Setting key
        
        Returns:
            True if successful, False otherwise
        """
        return BaseRepository.execute_query(
            "DELETE FROM settings WHERE key = ?",
            (key,),
            commit=True
        ) is not None
    
    @staticmethod
    def clear_all_settings() -> bool:
        """
        Delete all settings (use with caution).
        
        Returns:
            True if successful, False otherwise
        """
        return BaseRepository.execute_query(
            "DELETE FROM settings",
            commit=True
        ) is not None
