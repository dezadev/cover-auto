from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutConfig:
    """Physical cover template measurements in millimeters."""

    canvas_width_mm: float = 297.0
    canvas_height_mm: float = 430.0
    front_width_mm: float = 210.0
    front_height_mm: float = 297.0
    spine_width_mm: float = 18.0
    gap_mm: float = 5.0
    margin_top_mm: float = 32.0
    spine_left_mm: float = 57.0

    @property
    def front_x_mm(self) -> float:
        return self.spine_left_mm + self.spine_width_mm + self.gap_mm

    @property
    def front_y_mm(self) -> float:
        return self.margin_top_mm

    @property
    def spine_x_mm(self) -> float:
        return self.spine_left_mm

    @property
    def spine_y_mm(self) -> float:
        return self.margin_top_mm
