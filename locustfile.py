from locust import HttpUser, task, between

from server import loadClubs, loadCompetitions


class LocustServer(HttpUser):
    """Test server.py using Locust."""

    wait_time = between(1, 5)

    competitions = loadCompetitions()
    competition = competitions[-1]

    clubs = loadClubs()
    club = clubs[-1]

    def on_start(self):
        """Test to access to the index page."""
        self.client.get("/")

    @task
    def showSummary(self):
        """Test the function showSummary()."""
        self.client.post("/showSummary", data={"email": self.club["email"]})

    @task()
    def book(self):
        """Test the function book()."""
        self.client.get(f"/book/{self.competition['name']}/{self.club['name']}")

    @task()
    def purchasePlaces(self):
        """Test access the function purchasePlaces()."""
        placesRequired = 1
        self.client.post(
            "/purchasePlaces",
            data={
                "club": self.club["name"],
                "competition": self.competition["name"],
                "places": placesRequired,
            },
        )

    @task
    def test_logout(self):
        """Test to log out."""
        self.client.get("http://127.0.0.1:5000/logout")
