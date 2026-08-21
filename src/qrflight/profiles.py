from qrflight.models import Scenario

QUICK_PROFILE = (
    Scenario("blur-mild", "blur", 1.0),
    Scenario("jpeg-mild", "jpeg", 60.0),
    Scenario("downsample-mild", "downsample", 0.6),
    Scenario("contrast-mild", "contrast", 0.6),
)

PRINT_PROFILE = (
    Scenario("blur-mild", "blur", 1.0),
    Scenario("blur-strong", "blur", 2.0),
    Scenario("jpeg-mild", "jpeg", 60.0),
    Scenario("jpeg-strong", "jpeg", 30.0),
    Scenario("downsample-mild", "downsample", 0.6),
    Scenario("downsample-strong", "downsample", 0.35),
    Scenario("contrast-mild", "contrast", 0.6),
    Scenario("contrast-strong", "contrast", 0.35),
)


def profile_scenarios(name: str) -> tuple[Scenario, ...]:
    """Return the deterministic scenarios for a public profile name."""
    if name == "quick":
        return QUICK_PROFILE
    if name == "print":
        return PRINT_PROFILE
    raise ValueError(f"unknown profile: {name}")
