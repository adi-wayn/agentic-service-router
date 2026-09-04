import json
from typing import List, Dict, Any, Optional
from src.config import config


class ServiceCatalogue:
    _instance = None
    _templates: Dict[str, Any] = {}
    _metadata = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceCatalogue, cls).__new__(cls)
            cls._instance._load_catalogue()
        return cls._instance

    def _load_catalogue(self) -> None:
        """Loads and caches the service catalogue from the JSON file into a Hash Map."""
        try:
            with open(config.CATALOGUE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Convert the list into a dictionary keyed by 'id' for O(1) lookups
                raw_templates = data.get("templates", [])
                self._templates = {t["id"]: t for t in raw_templates if "id" in t}

                self._metadata = {
                    "catalogue_version": data.get("catalogue_version"),
                    "notes": data.get("notes"),
                    "urgency_tiers": data.get("urgency_tiers", {}),
                }
        except FileNotFoundError:
            raise RuntimeError(
                f"Service catalogue file not found at {config.CATALOGUE_PATH}"
            )
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse service catalogue JSON: {e}")

    @property
    def templates(self) -> List[Dict[str, Any]]:
        """Returns the full list of template dictionaries."""
        return list(self._templates.values())

    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single template dictionary by its ID in O(1) time."""
        return self._templates.get(template_id)

    def get_required_fields(self, template_id: str) -> List[str]:
        """Retrieves the list of required intake fields for a specific template."""
        template = self.get_template_by_id(template_id)
        if template:
            return template.get("required_intake_fields", [])
        return []

    def get_signals(self, template_id: str) -> List[str]:
        """Retrieves the list of signal arrays (symptoms) for a specific template."""
        template = self.get_template_by_id(template_id)
        if template:
            return template.get("signals", [])
        return []

    def get_trade_definition(self, template_id: str) -> Optional[str]:
        """Retrieves the trade definition (category) for a specific template."""
        template = self.get_template_by_id(template_id)
        if template:
            return template.get("category")
        return None
