from __future__ import annotations

import logging
import random
import secrets
from typing import List

from tinydb import Query, TinyDB, where

from chess.models.rounds import Round


class Tournament:
    """Tournament model class

    Positionnal args:
        name - str - name of the tournament
        start_date - str - start date of the tournament
        end_date - str - end date of the tournament

    Optional args:
        description - str - description of the tournament - default = "" (empty string)
        location - str - location of the tournament - default = "" (empty string)
        tournament_id - str - id of the tournament - default = None
        round_id_list - List[str] - list of rounds id - default = None
        player_id_list - List[str] - list of players id - default = None
        current_round_number - int - current round number - default = -1
        status - str - status of the tournament - default = "Created"
    """

    db = TinyDB("./data/tournaments.json")

    N_PLAYERS = 4
    N_ROUNDS = 3
    N_MATCHES_PER_ROUND = 2
    AUTHORISED_STATUS = ["Created", "In Progress", "Completed"]

    def __init__(
        self,
        name: str,
        start_date: str,
        end_date: str,
        description: str = "",
        location: str = "",
        tournament_id: str | None = None,
        round_id_list: List[str] | None = None,
        player_id_list: List[str] | None = None,
        current_round_number: int = -1,  # change rand ? or ? !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        status: str = "Created",
    ):
        """Init method for tournaments"""

        # handle written args by user
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.location = location

        self.tournament_id = tournament_id if tournament_id else secrets.token_hex(4)
        self.round_id_list = round_id_list if round_id_list else []
        self.player_id_list = player_id_list if player_id_list else []
        self.current_round_number = current_round_number
        self.status = status

    def to_dict(self) -> dict:
        """Convert tournament to dict"""
        return self.__dict__

    @classmethod
    def from_dict(cls, tournament_dict):
        """Convert dict to tournament"""

        return Tournament(**tournament_dict)

    def create(self) -> None:
        """Create method for tournaments"""

        self.db.insert(self.to_dict())

    @classmethod
    def read_one(cls, tournament_id: str) -> dict | None:
        """Read method for tournaments (Read one)"""

        tournament = Query()
        result = cls.db.search(tournament.tournament_id == tournament_id)
        res = result[0] if result else None

        return Tournament.from_dict(res) if res else None

    @classmethod
    def read_all(cls) -> list[dict]:
        """Read all method for tournaments"""

        res = cls.db.all()
        return [Tournament.from_dict(tournament) for tournament in res]

    @classmethod
    def search(cls, tournament_id):
        """Search for a tournament by tournament_id"""

        tournament = Query()
        result = cls.db.search(tournament.tournament_id == tournament_id)
        res = result[0] if result else None

        return Tournament.from_dict(res) if res else None

    @classmethod
    def search_by(cls, key: str, value) -> list[dict]:
        """Search method for tournaments by key and value"""

        res = cls.db.search(where(key) == value)
        return [Tournament.from_dict(tournament) for tournament in res]

    def update(self) -> None:
        """Update method for tournaments"""

        """ PB MAJ TPURNEMENT"""
        self.db.update(self.to_dict(), where("tournament_id") == self.tournament_id)

        logging.warning(f"Tournament {self.tournament_id} updated successfully.")

    def delete(self) -> None:
        """Delete method for tournaments"""
        # Not necessary for now
        raise NotImplementedError("Not included in specs")

    @classmethod
    def delete_all(cls) -> None:
        """Delete all method for tournaments"""

        cls.db.truncate()

    @classmethod
    def bootstrap(cls, num_tournaments: int = 3) -> None:
        """Create method for tournaments (Bootstrap)"""

        for _ in range(num_tournaments):
            name = "Tournament" + secrets.token_hex(4)
            start_date = f"{random.randint(2023, 2025)}-01-01"
            end_date = f"{random.randint(2025, 2027)}-12-31"
            tournament_id = "boot_" + secrets.token_hex(4)
            # matches = [f"Match{i}" for i in range(random.randint(10, 20))]
            # participants = [f"Participant{i}" for i in range(random.randint(6, 10))]
            description = "Description for " + name
            location = [f"Location{i}" for i in range(random.randint(3, 5))]
            t = Tournament(
                name,
                start_date,
                end_date,
                description=description,
                location=location,
                tournament_id=tournament_id,
            )
            t.create()

    @classmethod
    def reboot(cls, num_tournaments: int = 100) -> None:
        """Delete all tournaments and create 100 tournaments"""

        cls.delete_all()
        cls.bootstrap(num_tournaments)

    # def get_n_players(self) -> int:
    #     """Return number of players"""

    #     # tournament = Tournament(**dict)
    #     # n_player = tournament.get_n_players()

    #     return len(self.player_id_list)

    @property
    def n_players(self) -> int:
        """Return number of players"""

        #######################"
        # une @property est un attribut qui est calculé à la volée
        # comme un attribut de classe MAIS EN FAIT cest une methode
        #######################""

        # tournament = Tournament(**dict)
        # n_player = tournament.n_players  PAS BESOIN DES ()

        return len(self.player_id_list)

    def add_player(self, player_id: str) -> None:  # !!!!!!!!!!
        """Add player to tournament"""

        # TODO : add verification that the player is not already in the tournament
        # TODO : add verification that the player is not already in the Player DB Table

        if player_id in self.player_id_list:
            raise ValueError("Le jouer existe deja dans le tournament.")

        # TODO: Add verification that the player is not already in the Player DB Table
        # if self._player_exists_in_db(player_id):  # a implementer
        #     raise ValueError("Le jouer existe deja dans Player DB Table .")

        # si status != created => trop tard mon coco :)

        # verify that current player number not higher than number of players (4)
        if len(self.player_id_list) > self.N_PLAYERS:
            raise AttributeError(
                "Current player number is higher than the number of players (4)"
            )

        # verify that the current player is not in the player list
        if player_id in self.player_id_list:
            raise AttributeError("Current player is already in the player list")

        # add player to the player list
        self.player_id_list.append(player_id)

        self.update()  # for now it is useless   !!!!!

    def _add_round(self, round_number: int, matches: List[str]) -> str:
        """Add a round to the tournament."""

        round_id = f"{self.tournament_id}_round_{round_number}"
        new_round = Round(round_number, matches, round_id=round_id)
        new_round.create()

        # Add the round to the list of rounds
        self.round_id_list.append(new_round.round_id)

        # save the tournament
        self.update()

        return new_round.round_id

    # def update_status(self, new_status: str):
    #     """ """
    #
    #     # check if new status is authorised
    #     if new_status not in self.AUTHORISED_STATUS:
    #         raise ValueError("Invalid tournament status.")
    #
    #     # manage created
    #     if self.status == "Created" and new_status == "In Progress":
    #         # if not good n players
    #         if len(self.player_id_list) != self.N_PLAYERS:
    #             raise ValueError(
    #                 "Pas possible de passer a 'In Progress' sans 4 jouers."
    #             )
    #
    #         # Calculate rounds and matches
    #         round_0 = [
    #             # 1er match du round 0
    #             [
    #                 (self.player_id_list[0], -1),  # Player 0, (son id, son score)
    #                 (self.player_id_list[1], -1),  # Player 1, (son id, son score)
    #             ],
    #             # 2eme match du round 0
    #             [
    #                 (self.player_id_list[2], -1),  # Player 2,son id son score
    #                 (self.player_id_list[3], -1),  # Player 3, son id son score
    #             ],
    #         ]
    #
    #         round_1 = [
    #             [
    #                 (self.player_id_list[0], -1),  # P0 (id, score)
    #                 (self.player_id_list[2], -1),  # P2 (id, score)
    #             ],  # 1er match
    #             [
    #                 (self.player_id_list[1], -1),
    #                 (self.player_id_list[3], -1),
    #             ],  # 2eme match
    #         ]
    #
    #         round_2 = [
    #             [
    #                 (self.player_id_list[0], -1),
    #                 (self.player_id_list[3], -1),
    #             ],  # 1er match
    #             [
    #                 (self.player_id_list[1], -1),
    #                 (self.player_id_list[2], -1),
    #             ],  # 2eme match
    #         ]
    #
    #         # match list
    #         match_list = [round_0, round_1, round_2]
    #
    #         for i, match_list in enumerate(match_list):
    #             # add round id db
    #             _ = self._add_round(i, match_list)
    #
    #         # Save rounds to DB
    #         self.status = "In Progress"
    #         self.update()
    #
    #     elif self.status == "In Progress" and new_status == "Completed":
    #         # Check if all rounds have been played
    #
    #         if len(self.round_id_list) < self.N_PLAYERS - 1:
    #             raise ValueError(
    #                 "Impossible de terminer le tournoi sans que tout les rounds sois finis."
    #             )
    #
    #     else:
    #         raise ValueError(
    #             f"Status invalid. Impossible de changer le status de {self.status} a {new_status}"
    #         )
    #
    #     self.update()

    def update_status(self, new_status: str):
        """Update the status of the tournament."""

        if new_status not in self.AUTHORISED_STATUS:
            raise ValueError("Invalid tournament status.")

        if self.status == "Created" and new_status == "In Progress":
            # Check if there are enough players
            if len(self.player_id_list) != self.N_PLAYERS:
                raise ValueError(
                    f"Impossible de passer à 'In Progress' sans {self.N_PLAYERS} joueurs."
                )

            # on initialize les matchs avec random scores (1 or 0)
            # Ca au final c'est pas top
            # car on peut avoir 1 1 en resultat ou 0 0
            match_list = [
                [
                    [
                        (player_id, random.choice([1, 0]))
                        for player_id in self.player_id_list
                    ]
                    for _ in range(self.N_MATCHES_PER_ROUND)
                ]
                for _ in range(self.N_ROUNDS)
            ]

            # Add rounds to database
            for i, round_matches in enumerate(match_list):
                _ = self._add_round(i, round_matches)

            # Update status to 'In Progress' and save
            self.status = "In Progress"
            self.current_round_number = 0
            self.update()

        elif self.status == "In Progress" and new_status == "Completed":
            # Check if all rounds are played
            if len(self.round_id_list) < self.N_ROUNDS:
                raise ValueError(
                    "Impossible de terminer le tournoi sans que tous les rounds soient finis."
                )

        else:
            raise ValueError(
                f"Statut invalide. Impossible de changer le statut de {self.status} à {new_status}."
            )

        # Update the status
        self.update()

    def _next_round(self):
        """change the round +=1"""

        # Check si toutes le rounds sont finished
        if self.current_round_number == self.N_ROUNDS - 1:
            # Update status et save
            self.status = "Completed"

        else:
            # On continue les rounds
            self.current_round_number += 1

        self.update()

    def get_current_round(self):
        """Get the current round number for the tournament."""

        if not self.round_id_list:
            logging.warning("No rounds have been computed yet.")
            return None

        current_round_id = self.round_id_list[-1]
        logging.warning(f"Current Round ID: {current_round_id}")

        # try to get current round data
        current_round = Round.search_by("round_id", current_round_id)

        if not current_round:
            logging.warning(f"No data found for Round ID: {current_round_id}")
            return None

        return current_round

    def update_current_round(self, match_list=None):
        """Update the current round number for the tournament."""

        # Check if there are rounds to update
        if not self.round_id_list:
            logging.warning("No rounds have been computed yet.")
            return

        # Find the round instance of the current round
        current_round_id = self.round_id_list[-1]
        current_round_data = Round.search_by("round_id", current_round_id)

        if not current_round_data:
            logging.warning(f"No data found for Round ID: {current_round_id}")
        else:
            logging.info(
                f"Found data for Round ID: {current_round_id}, Data: {current_round_data}"
            )
            return

        current_round = self.get_current_round()

        # Log or print relevant information
        logging.info(f"Before update - Current Round ID: {current_round.round_id}")
        logging.info(f"Before update - Current Round: {current_round}")
        print(
            "*****************************************************************************************"
        )
        # Update the round with match_list
        if match_list:
            # Check if match_list is a list with elements for each round
            if len(match_list) != self.N_ROUNDS:
                logging.error(
                    f"Invalid match_list length: {len(match_list)} (expected {self.N_ROUNDS}). Content: {match_list}"
                )
                return
            current_round.matches = match_list[self.current_round_number]

            # Log or print relevant information
            logging.info(f"Updated Round ID: {current_round.round_id}")
            logging.info(f"Updated Round: {current_round}")

            try:
                # Update the current round
                current_round.update()
            except Exception as e:
                # Log the exception
                logging.error(f"Error updating current round: {e}")

        # Increment round number
        if self.current_round_number >= 0:
            if self.current_round_number < self.N_ROUNDS - 1:
                self.current_round_number += 1

                match_list_for_next_round = match_list[self.current_round_number]
                new_round_number = self._add_round(
                    self.current_round_number, match_list_for_next_round
                )  # add to the DB
                self.round_id_list.append(
                    new_round_number
                )  # add new round number to the round id list
            else:
                self.status = "Completed"
                logging.warning("Tournament is completed.")

        self._next_round()
        self.update()

        # Log or print relevant information after the update
        logging.info(f"After update - Current Round ID: {current_round.round_id}")
        logging.info(f"After update - Current Round: {current_round}")

    def __repr__(self) -> str:
        """Tournament representation"""

        return (
            f"Tournament(name={self.name}, start_date={self.start_date}, end_date={self.end_date}, "
            f"tournament_id={self.tournament_id}, description={self.description},location={self.location}, "
            f"matches={self.round_id_list}, participants={self.player_id_list})"
        )

    def get_score(self, player_id):
        player_score = 0

        # Iterate through rounds
        for round_id in self.round_id_list:
            round_data = Round.search_by("round_id", round_id)

            if round_data:
                for match in round_data.matches:
                    # Iterate matches to find player's score
                    for player_tuple in match:
                        if player_tuple[0] == player_id:
                            player_score += player_tuple[1]

        return player_score
