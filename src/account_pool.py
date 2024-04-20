import os
from dotenv import dotenv_values
from util import working_path


## Track multiple accounts in a pool, cycling to the next one when requested.
class AccountPool:
    def __init__(self):
        self.__accounts: list[tuple[str, str]] = list()
        self.__idx = 0
        creds = dotenv_values(working_path(file=".env"))
        i = 0
        while True:
            if f"scraper{i}_username" in creds and f"scraper{i}_password" in creds:
                self.__accounts.append(
                    (creds[f"scraper{i}_username"], creds[f"scraper{i}_password"])
                )
                i += 1
            else:
                break
        print(f"{len(self.__accounts)} scraper credentials found!")

    def use_index(self, idx):
        self.__idx = idx
        return self.current()

    def current(self):
        if 0 <= self.__idx < len(self.__accounts):
            return self.__accounts[self.__idx]
        return None

    def next(self) -> tuple[str, str] | None:
        self.__idx += 1
        if self.__idx >= len(self.__accounts):
            self.__idx = -1
            return None
        return self.current()
