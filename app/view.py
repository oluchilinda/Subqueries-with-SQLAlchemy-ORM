import datetime
import decimal
import json

from flask import Blueprint
from sqlalchemy.sql import alias

from . import db
from .models import (Actor, Customer, Film, FilmActor, Inventory, Payment,
                     Rental)

bp = Blueprint("main", __name__)





def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)





@bp.route("/price", methods=("GET", "POST"))
def totalRevenues_from_PGrated_movies_acto_nameStarts_with_S():

    actors_s = (
        db.session.query(Actor.actor_id, Actor.first_name, Actor.last_name)
        .filter(Actor.last_name.like("S%"))
        .subquery()
    )

    film_filmactor = (
        db.session.query(actors_s, Film.film_id, Film.title)
        .join(FilmActor, actors_s.c.actor_id == FilmActor.actor_id)
        .join(Film, Film.film_id == FilmActor.film_id)
        .filter(Film.rating == "PG")
        .subquery()
    )

    inventory_rental = (
        db.session.query(
            film_filmactor.c.first_name, film_filmactor.c.last_name, Payment.amount
        )
        .join(Inventory, Inventory.film_id == film_filmactor.c.film_id)
        .join(Rental, Inventory.inventory_id == Rental.inventory_id)
        .join(Payment, Rental.rental_id == Payment.rental_id)
    ).subquery()

    spg_rev = inventory_rental.alias("spg")
    final_query = (
        db.session.query(
            spg_rev.c.first_name,
            spg_rev.c.last_name,
            db.func.sum(spg_rev.c.amount).label("tot_revenue"),
        )
        .group_by(spg_rev.c.first_name, spg_rev.c.last_name)
        .order_by(db.func.sum(spg_rev.c.amount).desc())
    )
    return json.dumps(
        [dict(r) for r in db.session.execute(final_query)], default=alchemyencoder
    )


@bp.route("/info", methods=("GET", "POST"))
def customer_IDs_with_filmRentals_and_totalPayments():

    stmt = (
        db.session.query(
            Payment.customer_id,
            db.func.count("*").label("num_rentals"),
            db.func.sum(Payment.amount).label("tot_payments"),
        )
        .group_by(Payment.customer_id)
        .subquery()
    )

    result = (
        db.session.query(
            Customer.first_name,
            Customer.last_name,
            stmt.c.num_rentals,
            stmt.c.tot_payments,
        )
        .join(stmt, Customer.customer_id == stmt.c.customer_id)
        .order_by(Customer.customer_id)
    )

    return json.dumps(
        [dict(r) for r in db.session.execute(result)], default=alchemyencoder
    )
