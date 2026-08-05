"""
This module contains helper functions for generating test data.
"""
import time

from typing import Dict, Any

def generate_pet_data(pet_id: int = None, status: str = "available") -> Dict[str, Any]:
    """ This method defines a dynamic payload for creating/updating a pet """
    if pet_id is None:
        pet_id = int(time.time() * 1000) % 1000000000

    return {
        "id": pet_id,
        "category": {"id": 1, "name": "dogs"},
        "name": f"my_pet_{pet_id}",
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "automated_pet"}],
        "status": status
    }
