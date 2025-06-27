from enum import Enum


class MeansTestCalculator(Enum):
    CFE = "CFE"
    CLA_BACKEND = "CLA_BACKEND"

    @classmethod
    def from_env(cls, env_value, default=None):
        if env_value is None:
            if default is not None:
                return default
            raise ValueError("Environment variable not set and no default provided")

        try:
            return cls(env_value.upper())
        except ValueError:
            valid_values = [e.value for e in cls]
            raise ValueError(f"Invalid decision value '{env_value}'. Must be one of {valid_values}")
