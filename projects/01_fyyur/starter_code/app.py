# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
import datetime
from logging import Formatter, FileHandler
#if I'm using this...
from flask_wtf import Form
#do I still need this???
from forms import *
from models import Venue, Show, Artist, app, db


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#
def SQL_obj_as_dict(obj):
    """Converts SQLALchemy Query Results to Dict
  *Input: ORM Object
  *Output: Single Object as Dict
  Makes use of the SQLAlchemy inspection system (https://docs.sqlalchemy.org/en/13/core/inspection.html)
  Used in following Views:
    - /venues
  """
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def return_res_as_dict(result):
    """Converts SQLALchemy Collections Results to Dict
  * Input: sqlalchemy.util._collections.result
  * Output: Result as list
  Source: https://stackoverflow.com/questions/48232222/how-to-deal-with-sqlalchemy-util-collections-result
  Used in following Views:
    - /venues
  """
    list_dict = []
    for i in result:
        i_dict = i._asdict()
        list_dict.append(i_dict)
    return list_dict


def format_datetime(value, format="medium"):
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(value, format)


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    # BONUS
    recent_artists = Artist.query.order_by(Artist.id).all()
    recent_venues = Venue.query.order_by(Venue.id).all()
    return render_template(
        "pages/home.html", recent_artists=recent_artists, recent_venues=recent_venues
    )


#  Venues
#  ----------------------------------------------------------------
@app.route("/venues")
def venues():
    grouped_venues = db.session.query(Venue.city, Venue.state).group_by(Venue.city)
    venue_data = return_res_as_dict(grouped_venues)

    for loc in venue_data:
        loc["venues"] = [
            SQL_obj_as_dict(each_venue)
            for each_venue in Venue.query.filter_by(city=loc["city"]).all()
        ]
        for each_venue in loc["venues"]:
            each_venue["num_of_shows"] = db.session.query(
                func.count(show.c.Venue_id)
            ).filter(
                Show.c.Venue_id
                == each_venue["id"]
                .filter(Show.c.start_time > datetime.now())
                .all()[0][0]
            )
        return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "")

    cnt_search_venues = (
        db.session.query(func.count(Venue.id))
        .filter(Venue.name.contains(search_term))
        .all()
    )
    search_venues_res = Venue.query.filter(Venue.name.contains(search_term)).all()
    response = {"count": cnt_search_venues[0][0], "data": search_venues_res}
    # change search_term to be equal to search_term should it not work
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    one_venue = Venue.query.get(venue_id)
    one_venue.past_shows = (
        db.sesssion.query(
            Artist.id.label("artist_id"),
            Artist.name.label("artist_name"),
            Artist.image_link.label("artist_image_link"),
            Show,
        )
        .filter(Show.c.Venue_id == venue_id)
        .filter(Show.c.Artist_id == Artist.id)
        .filter(Show.c.start_time <= datetime.now())
        .all()
    )
    one_venue.upcoming_shows = (
        db.session.query(
            Artist.id.label("artist_id"),
            Artist.name.label("artist_name"),
            Artist.image_link.label("artist_image_link"),
            Show,
        )
        .filter(Show.c.Venue_id == venue_id)
        .filter(Show.c.Artist_id == Artist.id)
        .filter(Show.c.start_time > datetime.now())
        .all()
    )
    # Step 4: Get Number of past Shows
    one_venue.past_shows_count = (
        db.session.query(func.count(Show.c.Venue_id))
        .filter(Show.c.Venue_id == venue_id)
        .filter(Show.c.start_time < datetime.now())
        .all()
    )[0][0]
    # Step 5: Get Number of Upcoming Shows
    one_venue.upcoming_shows_count = (
        db.session.query(func.count(Show.c.Venue_id))
        .filter(Show.c.Venue_id == venue_id)
        .filter(Show.c.start_time > datetime.now())
        .all()
    )[0][0]

    return render_template("pages/show_venue.html", venue=one_venue)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    form = VenueForm(
        request.form
    )  # Initialize form instance with values from the request
    flashType = "danger"  # Initialize flashType to danger. Either it will be changed to "success" on successfully db insert, or in all other cases it should be equal to "danger"
    if form.validate():
        try:
            # Create a new instance of Venue with data from VenueForm
            newVenue = Venue(
                name=request.form["name"],
                city=request.form["city"],
                state=request.form["state"],
                address=request.form["address"],
                phone=request.form["phone"],
                genres=request.form.getlist("genres"),
                facebook_link=request.form["facebook_link"],
            )
            db.session.add(newVenue)
            db.session.commit()
            # on successful db insert, flash success
            flashType = "success"
            flash("Venue {} was successfully listed!".format(newVenue.name))
        except:
            flash(
                "An error occurred due to database insertion error. Venue {} could not be listed.".format(
                    request.form["name"]
                )
            )
        finally:
            # Close the session
            db.session.close()
    else:
        flash(
            form.errors
        )  # Flashes reason, why form is unsuccessful (not really pretty)
        flash(
            "An error occurred due to form validation. Venue {} could not be listed.".format(
                request.form["name"]
            )
        )
    return render_template("pages/home.html", flashType=flashType)


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        # This will alert User that Venue could not be deleted because they are still Shows attached
        return jsonify({"success": False})
    finally:
        db.session.close()
    # This will return the User to the HomePage
    return jsonify({"success": True})


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    artists = Artist.query.all()
    return render_template("pages/artists.html", artists=artists)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term", "")
    # use search term to count, how many occurance can be find in database
    cnt_search_artist = (
        db.session.query(func.count(Artist.id))
        .filter(Artist.name.contains(search_term))
        .all()
    )
    # use search term to find all Artist records in database
    search_artist_res = Artist.query.filter(Artist.name.contains(search_term)).all()
    # create a well formatted response with above results
    response = {"count": cnt_search_artist[0][0], "data": search_artist_res}
    return render_template(
        "pages/search_artists.html", results=response, search_term=search_term
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    one_artist = Artist.query.get(artist_id)

    one_artist.past_shows = (
        db.session.query(
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
            Venue.image_link.label("venue_image_link"),
            Show,
        )
        .filter(Show.c.Artist_id == artist_id)
        .filter(Show.c.Venue_id == Venue.id)
        .filter(Show.c.start_time <= datetime.now())
        .all()
    )

    one_artist.upcoming_shows = (
        db.session.query(
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
            Venue.image_link.label("venue_image_link"),
            Show,
        )
        .filter(Show.c.Artist_id == artist_id)
        .filter(Show.c.Venue_id == Venue.id)
        .filter(Show.c.start_time > datetime.now())
        .all()
    )

    one_artist.past_shows_count = (
        db.session.query(func.count(Show.c.Artist_id))
        .filter(Show.c.Artist_id == artist_id)
        .filter(Show.c.start_time < datetime.now())
        .all()
    )[0][0]

    one_artist.upcoming_shows_count = (
        db.session.query(func.count(Show.c.Artist_id))
        .filter(Show.c.Artist_id == artist_id)
        .filter(Show.c.start_time > datetime.now())
        .all()
    )[0][0]

    return render_template("pages/show_artist.html", artist=single_artist)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    artist = Venue.query.get(artist_id)
    artist.name = (request.form["name"],)
    artist.city = (request.form["city"],)
    artist.state = (request.form["state"],)
    artist.phone = (request.form["phone"],)
    artist.genres = (request.form["genres"],)
    artist.facebook_link = request.form["facebook_link"]
    db.session.add(artist)
    db.session.commit()
    db.session.close()

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link

    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):

    venue = Venue.query.get(venue_id)
    venue.name = (request.form["name"],)
    venue.city = (request.form["city"],)
    venue.state = (request.form["state"],)
    venue.address = (request.form["address"],)
    venue.phone = (request.form["phone"],)
    venue.genres = (request.form.getlist("genres"),)
    venue.facebook_link = request.form["facebook_link"]
    db.session.add(venue)
    db.session.commit()
    db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    form = ArtistForm(
        request.form
    )  # Initialize form instance with values from the request
    flashType = "danger"  # Initialize flashType to danger. Either it will be changed to "success" on successfully db insert, or in all other cases it should be equal to "danger"
    if form.validate():
        try:
            newArtist = Artist(
                name=request.form["name"],
                city=request.form["city"],
                state=request.form["state"],
                phone=request.form["phone"],
                facebook_link=request.form["facebook_link"],
                genres=request.form.getlist("genres"),
            )
            db.session.add(newArtist)
            db.session.commit()

            # on successful db insert, flash success
            flashType = "success"
            flash("Artist {} was successfully listed!".format(newArtist.name))
        except:
            flash(
                "An error occurred due to database insertion error. Artist {} could not be listed.".format(
                    request.form["name"]
                )
            )
        finally:
            db.session.close()
    else:
        flash(
            form.errors
        )  # Flashes reason, why form is unsuccessful (not really pretty)
        flash(
            "An error occurred due to form validation. Artist {} could not be listed.".format(
                request.form["name"]
            )
        )
    return render_template("pages/home.html", flashType=flashType)


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    shows = (
        db.session.query(
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
            Artist.id.label("artist_id"),
            Artist.name.label("artist_name"),
            Artist.image_link.label("artist_image_link"),
            Show,
        )
        .filter(Show.c.Venue_id == Venue.id)
        .filter(Show.c.Artist_id == Artist.id)
        .all()
    )

    return render_template("pages/shows.html", shows=shows)


@app.route("/shows/create")
def create_shows():
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    form = ShowForm(
        request.form
    )  # Initialize form instance with values from the request
    flashType = "danger"  # Initialize flashType to danger. Either it will be changed to "success" on successfully db insert, or in all other cases it should be equal to "danger"
    if form.validate():
        try:
            newShow = Show.insert().values(
                Venue_id=request.form["venue_id"],
                Artist_id=request.form["artist_id"],
                start_time=request.form["start_time"],
            )
            db.session.execute(newShow)
            db.session.commit()
            flashType = "success"
            flash("Show was successfully listed!")
        except:
            flash(
                "An error occurred due to database insertion error. Show could not be listed."
            )
        finally:
            db.session.close()
    else:
        flash(
            form.errors
        )  # Flashes reason, why form is unsuccessful (not really pretty)
        flash("An error occurred due to form validation. Show could not be listed.")
    return render_template("pages/home.html", flashType=flashType)


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run(debug=app.debug)

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
