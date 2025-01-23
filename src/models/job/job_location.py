from typing import Literal

from pydantic import BaseModel


class JobLocation(BaseModel):
    """Type of work location.

    Attributes:
        type: One of:
            - Remote: Fully remote position
            - Hybrid: Mix of remote and onsite work
            - Onsite: Fully onsite position
    """

    type: Literal["Remote", "Hybrid", "Onsite"]
