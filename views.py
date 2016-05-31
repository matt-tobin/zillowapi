from flask import request, abort, Blueprint, jsonify, current_app
from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults, GetUpdatedPropertyDetails
from pyzillow.pyzillowerrors import ZillowError
from models import PropertyData
from datetime import datetime, timedelta


class PropDetailsWithAddressAndZip(GetUpdatedPropertyDetails):
    def __init__(self, data, *args, **kwargs):
        self.attribute_mapping['street'] = 'address/street'
        self.attribute_mapping['zip'] = 'address/zipcode'
        super().__init__(data, *args, **kwargs)


zillow_app = Blueprint('zillow_app', __name__)


@zillow_app.route('/estimated_price/<int:zillow_id>', methods=['GET'])
def get_estimated_price(zillow_id):
    zkey = current_app.config['ZKEY']
    zillow_data = ZillowWrapper(zkey)

    # check if already exists in DB and if so, that data is less than a week old, otherwise call zillow API
    db_results = PropertyData.objects(zillow_id=zillow_id)
    if db_results.count() > 0 and db_results[0].created_at > datetime.now()-timedelta(days=7):
        zestimate_amount = db_results[0].zestimate_amount
    else:
        try:
            detail_result = PropDetailsWithAddressAndZip(zillow_data.get_updated_property_details(zillow_id))
            deep_search_result = GetDeepSearchResults(zillow_data.get_deep_search_results(
                detail_result.street, detail_result.zip))
            zestimate_amount = deep_search_result.zestimate_amount
        except ZillowError as err:
            return jsonify({'error': err.message, 'estimate': 0})
    return jsonify({'estimate': zestimate_amount, 'error': ''})


@zillow_app.route('/property_data', methods=['POST'])
def store_property_data():
    zkey = current_app.config['ZKEY']
    if not request.get_json() or 'address' not in request.json or 'zipcode' not in request.json:
        abort(400)
    zillow_data = ZillowWrapper(zkey)
    address = request.json['address']
    zipcode = request.json['zipcode']
    try:
        response = zillow_data.get_deep_search_results(address, zipcode)
        result = GetDeepSearchResults(response)
    except ZillowError as err:
        return jsonify({'error': err.message, 'estimate': 0})

    # delete from db if already exists to prevent duplicates
    # (property data my have changed so need to refresh entry)
    pd = PropertyData.objects(zillow_id=result.zillow_id)
    for doc in pd:
        doc.delete()
    pd = fill_property_document(result)
    pd.save()
    return jsonify({'zillow_id': result.zillow_id, 'error': ''})


def fill_property_document(data):
    pd = PropertyData(
        home_type=getattr(data, 'home_type', None),
        home_detail_link=getattr(data, 'home_detail_link', None),
        graph_data_link=getattr(data, 'graph_data_link', None),
        map_this_home_link=getattr(data, 'map_this_home_link', None),
        zillow_id=getattr(data, 'zillow_id', None),
        latitude=getattr(data, 'latitude', None),
        longitude=getattr(data, 'longitude', None),
        tax_year=getattr(data, 'tax_year', None),
        tax_value=getattr(data, 'tax_value', None),
        year_built=getattr(data, 'year_built', None),
        property_size=getattr(data, 'property_size', None),
        home_size=getattr(data, 'home_size', None),
        bathrooms=getattr(data, 'bathrooms', None),
        bedrooms=getattr(data, 'bedrooms', None),
        zestimate_amount=getattr(data, 'zestimate_amount', None),
        zestimate_value_change=getattr(data, 'zestimate_value_change', None),
        zestimate_last_updated=getattr(data, 'zestimate_last_updated', None),
        zestimate_valuation_range_high=getattr(data, 'zestimate_valuation_range_high', None),
        zestimate_valuationRange_low=getattr(data, 'zestimate_valuationRange_low', None),
        zestimate_percentile=getattr(data, 'zestimate_percentile', None),
        last_sold_date=getattr(data, 'last_sold_date', None),
        last_sold_price=getattr(data, 'last_sold_price', None)
    )
    last_sold_date = getattr(data, 'last_sold_date', None)
    if last_sold_date is not None:
        pd.last_sold_date = datetime.strptime(last_sold_date, "%m/%d/%Y")
    zestimate_last_updated = getattr(data, 'zestimate_last_updated', None)
    if zestimate_last_updated is not None:
        pd.zestimate_last_updated = datetime.strptime(zestimate_last_updated, "%m/%d/%Y")

    return pd

