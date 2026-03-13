import json
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(kw_only=True)
class Salary:
    gross: Decimal = Decimal(0)
    compensations: Decimal = Decimal(0)
    ss_deduction: Decimal = Decimal(0)
    brackets_tax: Decimal = Decimal(0)
    fixed_tax: Decimal = Decimal(0)

    total: Decimal = field(init=False)
    taxes: Decimal = field(init=False)
    deductions: Decimal = field(init=False)
    net: Decimal = field(init=False)
    compensations_to_total_ratio: Decimal = field(init=False)

    def __post_init__(self) -> None:
        self.total = self.gross + self.compensations
        self.taxes = self.brackets_tax + self.fixed_tax
        self.deductions = self.ss_deduction + self.taxes
        self.net = self.total - self.deductions
        self.compensations_to_total_ratio = self.compensations / self.total

    def model_dump_json(self, indent: int = 4) -> str:
        return json.dumps(
            {
                "gross": float(self.gross),
                "compensations": float(self.compensations),
                "ss_deduction": float(self.ss_deduction),
                "brackets_tax": float(self.brackets_tax),
                "fixed_tax": float(self.fixed_tax),
                "total": float(self.total),
                "taxes": float(self.taxes),
                "deductions": float(self.deductions),
                "net": float(self.net),
                "compensations_to_total_ratio": float(self.compensations_to_total_ratio),
            },
            indent=indent,
        )
