from cassandra.cluster import Cluster, CloudSecureConnectionBundle
from cassandra.auth import PlainTextAuthProvider
from typing import Optional, Dict, Any
from app.core.config import ConfigManager
import logging

class AstraDBClient:
    """Client for interacting with AstraDB."""
    
    def __init__(self, config_manager: ConfigManager):
        self.token = config_manager.get_setting("ASTRA_DB_TOKEN")
        self.db_id = config_manager.get_setting("ASTRA_DB_ID")
        self.db_secret = config_manager.get_setting("ASTRA_DB_SECRET")
        self.keyspace = config_manager.get_setting("ASTRA_KEYSPACE")
        self.bundle_path = config_manager.get_setting("ASTRA_SECURE_BUNDLE_PATH")
        
        self.cluster = None
        self.session = None
        
        if not self.token and (not self.db_id or not self.db_secret):
            logging.warning("AstraDB credentials are not fully configured.")
        
    async def connect(self):
        """Establish connection to AstraDB."""
        if self.session and not self.session.is_shutdown:
            return  # Already connected
        
        if not self.token and (not self.db_id or not self.db_secret):
            logging.error("Missing credentials for AstraDB connection.")
            return
        
        try:
            if self.bundle_path:
                bundle = CloudSecureConnectionBundle(self.bundle_path)
                auth_provider = PlainTextAuthProvider(self.db_id, self.db_secret) if self.db_id and self.db_secret else None
                self.cluster = Cluster(cloud={'secure_connect_bundle': self.bundle_path}, auth_provider=auth_provider)
            else:
                logging.error("Secure bundle path is required for connection.")
                return
            
            self.session = self.cluster.connect(keyspace=self.keyspace)
            logging.info("Connected to AstraDB successfully.")
        except Exception as e:
            logging.error(f"Failed to connect to AstraDB: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from AstraDB."""
        if self.cluster:
            self.cluster.shutdown()
            self.session = None
            self.cluster = None
            logging.info("Disconnected from AstraDB.")
    
    async def execute_query(self, query: str, parameters: Optional[tuple] = None) -> Any:
        """Execute a query against AstraDB."""
        if not self.session:
            await self.connect()
            if not self.session:
                raise RuntimeError("No active connection to AstraDB.")
        
        try:
            result = await self.session.execute_async(query, parameters)
            return result
        except Exception as e:
            logging.error(f"Query execution failed: {str(e)}")
            return None

    async def get_astra_schema_version(self) -> Optional[str]:
        """Get the schema version from AstraDB."""
        query = "SELECT schema_version FROM system.local;"
        result = await self.execute_query(query)
        return result[0].schema_version if result else None