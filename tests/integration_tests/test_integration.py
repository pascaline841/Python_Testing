import server


class TestDisplayClub:
    """Test server.py using pytest"""

    client_test = server.app.test_client()
    clubs_test = [
        {"name": "club TEST 01", "email": "club01@test.com", "points": "20"},
    ]
    club_email = "club01@test.com"

    def setup(self):
        """Change server.py variable datas."""
        server.clubs = self.clubs_test

    def test_display_club_email(self):
        """Test if the email is displayed."""
        result = self.client_test.post("/showSummary", data={"email": self.club_email})
        assert result.status_code in [200]
        assert f"Welcome, {self.club_email}" in result.data.decode()


class TestDisplayPlace:
    """Test server.py using pytest"""

    client_test = server.app.test_client()
    clubs_test = [
        {"name": "club TEST 01", "email": "club01@test.com", "points": "20"},
    ]
    competitions_test = [
        {
            "name": "competition TEST 01",
            "date": "2030-05-12 10:00:00",
            "numberOfPlaces": "15",
        },
    ]
    competition_name = "competition TEST 01"

    def setup(self):
        """Change server.py variable datas."""
        server.clubs = self.clubs_test
        server.competitions = self.competitions_test

    def test_display_board_clubs(self):
        """Test book a place and display the modified data in board."""

        result = self.client_test.post(
            "/purchasePlaces",
            data={
                "places": 5,
                "club": self.clubs_test[0]["name"],
                "competition": self.competition_name,
            },
        )
        assert result.status_code in [200]
        assert f"<td>{self.clubs_test[0]['name']}</td>" in result.data.decode()
        assert f"<td>{self.clubs_test[0]['points']}</td>" in result.data.decode()
