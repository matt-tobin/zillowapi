from zillow import db
import datetime


class PropertyData(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    home_type = db.StringField(required=False)
    home_detail_link = db.StringField(required=False)
    graph_data_link = db.StringField(required=False)
    map_this_home_link = db.StringField(required=False)
    zillow_id = db.IntField(required=False)
    latitude = db.FloatField(required=False)
    longitude = db.FloatField(required=False)
    tax_year = db.IntField(required=False)
    tax_value = db.FloatField(required=False)
    year_built = db.IntField(required=False)
    property_size = db.IntField(required=False)
    home_size = db.IntField(required=False)
    bathrooms = db.FloatField(required=False)
    bedrooms = db.IntField(required=False)
    zestimate_amount = db.IntField(required=False)
    zestimate_value_change = db.IntField(required=False)
    zestimate_last_updated = db.DateTimeField(required=False)
    zestimate_valuation_range_high = db.IntField(required=False)
    zestimate_valuationRange_low = db.IntField(required=False)
    zestimate_percentile = db.IntField(required=False)
    last_sold_date = db.DateTimeField(required=False)
    last_sold_price = db.IntField(required=False)

    def __unicode__(self):
        return self.zillow_id