# import necessary libraries
import os
from sqlalchemy.sql import select, column, text
from sqlalchemy.sql.expression import func
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
from models import create_classes
import simplejson
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', '') or "sqlite:///db.sqlite"

# Remove tracking modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


Breweries = create_classes(db)

# create route that renders index.html template
@app.route("/")
def home():
    """
    Render the index.html template
    """
    return render_template("index.html")

def query_results_to_dicts(results):
    return simplejson.dumps(results)

@app.route("/api/all")
def all():
    results = db.session.query(
        Breweries.name,
        Breweries.brewery_type,
        Breweries.address,
        Breweries.state,
        Breweries.phone,
        Breweries.website_url,
        Breweries.country,
        Breweries.region,
        Breweries.division
    ).all()

    return query_results_to_dicts(results)

def get_selected_region():
    selected_region = request.args.get("region")

    # If we receive "All" from the front-end no filtering
    if selected_region == "All":
        return None

    # Given the characters races in the database are title cased
    # e.g. "Orc" not "orc"
    if selected_region is not None:
        selected_region = selected_region.title()
    
    return selected_region

@app.route("/api/count_by_region")
def count_by_region():
    results = db.session.query(
        Breweries.region,
        func.count(Breweries.region).label("total")
    )

    results = results.group_by(
        Breweries.region
    ).all()

    return query_results_to_dicts(results)


@app.route("/api/count_by/<count_by>", defaults={'optional_count_by': None})
@app.route("/api/count_by/<count_by>/<optional_count_by>")
def count_by(count_by, optional_count_by=None):

    # first let's check if we need to filter
    selected_region = get_selected_region()
   
    # let's first handle the case we there is no `optional_count_by`
    if optional_count_by is None:
        results = db.session.query(
            getattr(Breweries, count_by),
            func.count(getattr(Breweries, count_by)).label("total")
        )

        # apply the query stirng filter if present
        if selected_region is not None:
            results = results.filter(Breweries.region == selected_region)

        results = results.group_by(
            getattr(Breweries, count_by)
        ).order_by(
            getattr(Breweries, count_by)
        ).all()

    else:
        # lets handle grouping by two columns
        results = db.session.query(
            getattr(Breweries, count_by),
            getattr(Breweries, optional_count_by),
            func.count(getattr(Breweries, count_by)).label("total")
        )

        if selected_region is not None:
            results = results.filter(Breweries.region == selected_region)

        results = results.group_by(
            getattr(Breweries, count_by),
            getattr(Breweries, optional_count_by)
        ).order_by(
            getattr(Breweries, count_by),
            getattr(Breweries, optional_count_by),
        ).all()

    return query_results_to_dicts(results)


def get_column_values(for_column, selected_region = None):
    """
    Let's get the unique distinct values from column in
    our database, optionally filtering by query string.
    """
    
    value_query = db.session.query(
        func.distinct(getattr(Breweries, for_column))
    )

    if selected_region is not None:
        value_query = value_query.filter(
            Breweries.region == selected_region
        )
    
    values = sorted([x[0] for x in value_query.all()])

    return values

@app.route("/api/values/<for_column>/<group_by>")
@app.route("/api/values/<for_column>/", defaults={'group_by': None})
def values(for_column, group_by = None):
  

    selected_region = get_selected_region()

    if group_by is None:
        values = get_column_values(for_column, selected_region)
        return jsonify(values)

    values_for_groupby = dict()

    group_by_values = get_column_values(group_by, selected_region)

    results = db.session.query(
        getattr(Breweries, group_by),
        getattr(Breweries, for_column),
    )

    if selected_region is not None:
        results = results.filter(
            Breweries.region, selected_region
        )

    results = results.order_by(
        getattr(Breweries, group_by),
        getattr(Breweries, for_column),
    ).all()

    for group in group_by_values:
        values_for_groupby[group] = [x[1] for x in results if x[0] == group]

    return query_results_to_dicts(values_for_groupby)

@app.route("/api/where/<region>")
def where(region):
    """
    This will demonstrate running a SQL Query using the SQLAlchemy 
    execute method. 

    http://localhost:5000/api/where/the%20barrens will return:
    [
        {
            "char_class": "Hunter", 
            "guild": "Guild Guild -1", 
            "id": 6, 
            "level": 16, 
            "race": "Orc", 
            "region": "The Barrens"
        }, 
        {
            "char_class": "Warlock", 
            "guild": "Guild Guild -1", 
            "id": 7, 
            "level": 18, 
            "race": "Orc", 
            "region": "The Barrens"
        }
        ...
    ] 
    """

    """
    Because we using user input we need to a VERY 
    simple attempt to mitigate SQL injection
    using SQLAlchemy sql.text and bindparams
    
    https://docs.sqlalchemy.org/en/13/core/tutorial.html#specifying-bound-parameter-behaviors
    """
    results = db.engine.execute(text("""
        SELECT * FROM breweries 
        WHERE UPPER(region) = :region
    """).bindparams(
        region=region.upper().strip()
    ))
    
    """
    result will be a ResultProxy, see:
    https://docs.sqlalchemy.org/en/13/core/connections.html?highlight=execute#sqlalchemy.engine.Engine.execute

    so to convert into something that can be json 
    serialisable we need to iterate over each item 
    in the results and convert into a dictionary 
    and then jsonify the result.
    """
    return jsonify([dict(row) for row in results])

if __name__ == "__main__":
    app.run(debug=True)
