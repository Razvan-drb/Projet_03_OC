import random
import secrets
import logging

from tinydb import TinyDB, Query, where


class Player:
    """players model class"""
    db = TinyDB('./data/players.json')

    def __init__(self,
                 firstname: str,
                 lastname: str,
                 birthdate: str = "1970-01-01",
                 player_id: int | None = None,
                 ) -> None:
        """Init method for players"""

        self.player_id = player_id if player_id else secrets.token_hex(4)
        self.firstname = firstname.capitalize()
        self.lastname = lastname.upper()
        self.birthdate = birthdate

        # TODO: implement init method
        pass

    def to_dict(self) -> dict:
        """convert player to dict"""
        return self.__dict__

        # TODO: implement to dict method
        pass

    @classmethod
    def from_dict(cls, player_dict):
        """convert dict to player"""
        return Player(**player_dict)

    def create(self) -> None:
        """Create method for players"""
        self.db.insert(self.to_dict())

    @classmethod
    def read_one(cls, player_id: str) -> dict | None:
        """Read method for players (Read one)"""
        player = Query()
        result = cls.db.search(player.player_id == player_id)
        return result[0] if result else None

    @classmethod
    def read_all(cls) -> list[dict]:
        """Read all method for players"""
        return cls.db.all()

    @classmethod
    def search_by(cls, key: str, value) -> list[dict]:
        """Search method for players by key and value"""
        return cls.db.search(where(key) == value)

    def update(self) -> None:
        """Update method for players"""
        # not necessary
        raise NotImplementedError("not included in specs")

    def delete(self) -> None:
        """Delete method for players"""
        # not necessary
        raise NotImplementedError("not included in specs")

    def __repr__(self) -> str:
        """Player representation"""

        return f"Player(firstname={self.firstname}, lastname={self.lastname}, birthdate={self.birthdate}, " \
               f"player_id={self.player_id})"

    @classmethod
    def delete_all(cls) -> None:
        """delete all method for players"""
        cls.db.truncate()

    @classmethod
    def bootstrap(cls, num_players: int = 3) -> None:
        """Create method for players (Bootstrap)"""
        for _ in range(num_players):
            firstname = "test" + secrets.token_hex(4)
            lastname = "test" + secrets.token_hex(4)
            birthdate = f"{random.randint(1970, 2000)}-01-01"
            p = Player(firstname, lastname, birthdate)
            p.create()

    @classmethod
    def reboot(cls,num_players: int = 100) -> None:
        """delete all players and create 100 players"""
        cls.delete_all()
        cls.bootstrap(num_players)
