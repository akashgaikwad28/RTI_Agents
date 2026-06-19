"""Synthetic data generator for RTI documents."""

from __future__ import annotations

import faker

fake = faker.Faker("en_IN")

class SyntheticRTIGenerator:
    @staticmethod
    def generate_circular(department: str = "General") -> str:
        date = fake.date_this_decade()
        return f"""
        GOVERNMENT OF MAHARASHTRA
        Department: {department}
        Circular No: {fake.bban()}
        Date: {date}
        
        Subject: {fake.catch_phrase()}
        
        {fake.text(max_nb_chars=1000)}
        
        By Order,
        {fake.name()}
        """
        
    @staticmethod
    def generate_table_markdown(rows: int = 5) -> str:
        lines = ["| District | Budget | Status |", "|---|---|---|"]
        for _ in range(rows):
            lines.append(f"| {fake.city()} | {fake.random_int(min=10, max=500)} Cr | {fake.random_element(elements=('Approved', 'Pending'))} |")
        return "\n".join(lines)
