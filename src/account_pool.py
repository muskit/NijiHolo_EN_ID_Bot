from dotenv import dotenv_values

## Track multiple accounts in a pool, cycling to the next one when requested.
class AccountPool:
    def __init__(self):
        self.__accounts: list[tuple[str, str]] = list()
        self.__idx = -1
        creds = dotenv_values()
        i = 0
        while True:
            if f'scraper_username{i}' in creds \
				and f'scraper_password{i}' in creds:
                self.__accounts.append((
                    creds[f'scraper_username{i}'],
                    creds[f'scraper_password{i}']
				))
                i += 1
            else:
                break
    
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
