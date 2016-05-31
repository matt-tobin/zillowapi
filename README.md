# zillowapi
=================
A small RESTful API using the [flask](http://flask.pocoo.org/) microframework that extracts property data from the Zillow API. I chose the Flask framework due to the small scale of the API. Flask has integrated unit testing support and RESTful request dispatching making it ideal for this application. [Flask-MongoEngine](http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/) provided a powerful Document-Object Mapper for working with MongoDB.

Installation
------------
  1. Clone the repository
  2. Install [pip](http://www.pip-installer.org/en/latest/installing.html)
  3. Make a [virtualenv](http://virtualenvwrapper.readthedocs.org/en/latest/#introduction) for this project
  4. Install the required dependencies: `pip install -r requirements.txt`

Requirements
------------
MongoDB

Execution
------------
Start it with:
```
python zillow.py --key MyZWSID
```


### Consuming the API
```shell
# Return the Zillow estimated price given a property id.
curl http://localhost:5000/estimated_price/25077638
# Given home address and zipcode, extract property data from the Zillow API.
curl -H "Content-Type: application/json" -X POST -d '{"address":"2114 Bigelow Ave","zipcode":"98109"}' http://localhost:5000/property_data
