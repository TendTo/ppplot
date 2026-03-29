from .api import compute_performance_profile_data, plot_performance_profile

__all__ = ["plot_performance_profile", "compute_performance_profile_data", "main"]


def main() -> None:
    print(
        "ppplot CLI is minimal for now. Use plot_performance_profile(...) from Python."
    )
