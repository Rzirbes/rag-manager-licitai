import re


class SplitLawTextIntoArticlesUseCase:

    def execute(self, text: str) -> list[str]:
        articles = re.split(
            r"(?=Art\. ?\d+[º°]?)",
            text,
        )

        return [
            article.strip()
            for article in articles
            if article.strip().startswith("Art.")
        ]