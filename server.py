import datetime
import json

from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open("clubs.json") as c:
        return json.load(c)["clubs"]


def loadCompetitions():
    with open("competitions.json") as comps:
        return json.load(comps)["competitions"]


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()
places_max = 12

@app.route('/')
def index():
    return render_template('index.html', clubs=clubs)

def future_or_old_competitions(competitions):
    """Sort the old and future competitons."""
    old_competitions = [
        c
        for c in competitions
        if datetime.datetime.strptime(c["date"], "%Y-%m-%d %H:%M:%S")
        < datetime.datetime.now()
    ]
    future_competitions = [
        c
        for c in competitions
        if datetime.datetime.strptime(c["date"], "%Y-%m-%d %H:%M:%S")
        >= datetime.datetime.now()
    ]
    return old_competitions, future_competitions


@app.route("/showSummary", methods=["POST"])
def showSummary():
    try:
        club = [club for club in clubs if club["email"] == request.form["email"]][0]
        old_competitions, future_competitions = future_or_old_competitions(competitions)
        return render_template(
            "welcome.html",
            club=club,
            competitions=future_competitions,
            old_competitions=old_competitions,
            clubs=clubs,
        )
    except IndexError:
        flash("Sorry, that email wasn't found !")
        return render_template("index.html", clubs=clubs), 403


def is_competition_expired(competition):
    """Check if the competition has expired."""
    if (
        datetime.datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
        < datetime.datetime.now()
    ):
        raise ValueError("The booking has expired !")


@app.route("/book/<competition>/<club>")
def book(competition, club):
    club = [c for c in clubs if c["name"] == club][0]
    competition = [c for c in competitions if c["name"] == competition][0]
    try:
        is_competition_expired(competition)
    except ValueError as error:
        flash(error)
        status_code = 403
        old_competitions, future_competitions = future_or_old_competitions(competitions)
        return (
            render_template(
                "welcome.html",
                club=club,
                competitions=future_competitions,
                old_competitions=old_competitions,
                clubs=clubs,
            ),
            status_code,
        )
    return render_template("booking.html", club=club, competition=competition)



def not_more_twelve_places(placesRequired):
    """Check the club is trying to buy more than places_max."""
    if placesRequired > places_max:
        raise ValueError("More places than authorized to book by club !")


def available_places(competition, placesRequired):
    """Check if the club is trying to buy more places than available."""
    if int(competition["numberOfPlaces"]) < placesRequired:
        raise ValueError("More places requested than available !")
    else:
        competition["numberOfPlaces"] = (
            int(competition["numberOfPlaces"]) - placesRequired
        )


def enough_points(club, placesRequired):
    """Check if the club is trying to buy more points than available."""
    if int(club["points"]) < placesRequired :
        raise ValueError("More places requested than available points !")
    else:
        club["points"] = int(club["points"]) - placesRequired 

def not_negatif_point(placesRequired):
    """Check if places required haven't zero or negative value."""
    if placesRequired <= 0:
        raise ValueError("This is not a positive value !")


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][
        0
    ]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    placesRequired = int(request.form["places"])
    try:
        not_negatif_point(placesRequired)
        not_more_twelve_places(placesRequired)
        enough_points(club, placesRequired)
        available_places(competition, placesRequired)
        flash("Great - booking complete!")
        status_code = 200
    except ValueError as error:
        flash(error)
        status_code = 403
    old_competitions, future_competitions = future_or_old_competitions(competitions)
    return (
        render_template(
            "welcome.html",
            club=club,
            competitions=future_competitions,
            old_competitions=old_competitions,
            clubs=clubs,
        ),
        status_code,
    )

@app.route('/logout')
def logout():
    return redirect(url_for('index'))