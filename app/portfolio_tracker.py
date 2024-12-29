from typing import List, Dict, Type
from app.models.position import Position
from app.sources.trading212 import Trading212Source
from app.sources.debank import DebankSource
from app.sinks.notion import NotionSink
from app.services.web_driver import WebDriverService
from app.interfaces.data_source import DataSource
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)

class PortfolioTracker:
    """Core class for managing portfolio tracking operations."""

    def __init__(self, settings: Settings):
        """Initialize the portfolio tracker with configurations.
        
        Args:
            settings: Application settings instance containing necessary configurations
        """
        self.settings = settings
        self.web_driver_service = WebDriverService()
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize data sources and sinks."""
        # Initialize available sources
        self.source_registry: Dict[str, Type[DataSource]] = {
            'Trading212': Trading212Source,
            'Debank': DebankSource
        }

        # Create source instances
        self.available_sources: Dict[str, DataSource] = {
            name: source_class(self.settings, self.web_driver_service) 
            if name == 'Debank' else source_class(self.settings)
            for name, source_class in self.source_registry.items()
        }

        # Initialize active sources with all available sources
        self.active_sources: Dict[str, DataSource] = self.available_sources.copy()

        # Initialize data sink
        self.sink = NotionSink(self.settings)

    def set_active_sources(self, source_names: List[str]) -> None:
        """Update the list of active data sources.
        
        Args:
            source_names: List of source names to activate
        """
        self.active_sources = {
            name: source for name, source in self.available_sources.items()
            if name in source_names
        }
        logger.info(f"Active sources updated: {', '.join(self.active_sources.keys())}")

    def get_available_sources(self) -> List[str]:
        """Get list of all available source names.
        
        Returns:
            List of available source names
        """
        return list(self.source_registry.keys())

    def run(self) -> dict:
        """Execute portfolio tracking operation with active sources.
        
        Returns:
            Dictionary containing operation results and any errors
        """
        if not self.active_sources:
            logger.warning("No active sources configured")
            return {
                "status": "warning",
                "message": "No active sources configured",
                "positions": []
            }

        all_positions: List[Position] = []
        errors: Dict[str, str] = {}
        
        # Fetch positions from each active source
        for source_name, source in self.active_sources.items():
            try:
                logger.info(f"Fetching positions from {source_name}")
                positions = source.fetch_positions()
                all_positions.extend(positions)
                logger.info(f"Successfully fetched {len(positions)} positions from {source_name}")
            except Exception as e:
                error_msg = f"Error fetching positions from {source_name}: {str(e)}"
                logger.error(error_msg)
                errors[source_name] = error_msg

        # Save positions if any were fetched successfully
        if all_positions:
            try:
                logger.info(f"Saving {len(all_positions)} positions to Notion")
                self.sink.save_positions(all_positions)
                logger.info("Successfully saved positions to Notion")
            except Exception as e:
                error_msg = f"Error saving positions to Notion: {str(e)}"
                logger.error(error_msg)
                errors["notion"] = error_msg

        return {
            "status": "success" if not errors else "partial_success" if all_positions else "error",
            "message": "Portfolio tracking completed" + (f" with {len(errors)} errors" if errors else ""),
            "positions": len(all_positions),
            "errors": errors if errors else None
        }

    def validate_sources(self, source_names: List[str]) -> List[str]:
        """Validate a list of source names.
        
        Args:
            source_names: List of source names to validate
            
        Returns:
            List of valid source names
        """
        valid_sources = []
        for name in source_names:
            if name in self.source_registry:
                valid_sources.append(name)
            else:
                logger.warning(f"Invalid source name: {name}")
        return valid_sources