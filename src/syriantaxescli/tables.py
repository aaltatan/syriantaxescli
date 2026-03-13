from rich.table import Table

from .schemas import Salary


def get_salary_table(*salaries: Salary, title: str = "Results") -> Table:
    table = Table(title=title, title_justify="center", caption_justify="center")

    table.add_column("#", justify="right", overflow="fold")
    table.add_column("Gross", justify="right")
    table.add_column("Comps", justify="right")
    table.add_column("Total", justify="right", style="green")
    table.add_column("Brackets Tax", justify="right")
    table.add_column("Fixed Tax", justify="right")
    table.add_column("Net", justify="right", style="green")

    for idx, salary in enumerate(salaries, start=1):
        table.add_row(
            str(idx),
            f"{salary.gross:,.2f}",
            f"{salary.compensations:,.2f}",
            f"{salary.total:,.2f}",
            f"{salary.brackets_tax:,.2f}",
            f"{salary.fixed_tax:,.2f}",
            f"{salary.net:,.2f}",
        )

    return table
