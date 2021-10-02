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

@app.route('/')
def index():
    return render_template('index.html')

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



@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))