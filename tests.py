import unittest
import json
from zillow import create_app as create_app_base
from models import PropertyData
from datetime import timedelta, datetime


class ZillowTestCase(unittest.TestCase):
    def create_app(self):
        return create_app_base(
            MONGODB_SETTINGS={'DB': 'testing'},
            ZKEY="X1-ZWz1far8gxnjt7_9ljvt",
            TESTING=True,
        )

    def setUp(self):
        self.app = self.create_app().test_client()

    def tearDown(self):
        PropertyData.objects.all().delete()

    # Tests if the property data is stored in the db when a valid address is given.
    def test_property_data_stored_in_db(self):
        rv = self.app.post('/property_data', data=json.dumps(dict(
            address="2114 Bigelow Ave",
            zipcode="98109")),content_type='application/json'
        )
        self.assertEqual(PropertyData.objects.all().count(), 1)

    # Tests if an error is returned when an invalid address is given
    def test_error_returned_when_given_invalid_address(self):
        rv = self.app.post('/property_data', data=json.dumps(dict(
            address="123 Fake St",
            zipcode="9810999")), content_type='application/json'
                           )
        rv_decoded = json.loads(rv.get_data(as_text=True))
        self.assertEqual(rv_decoded['error']['code'], 508)
        self.assertEqual(PropertyData.objects.all().count(), 0)

    # Tests old entry deleted and new one added if already exists in database
    def test_refresh_entry_if_exists_already(self):
        rv = self.app.post('/property_data', data=json.dumps(dict(
            address="2114 Bigelow Ave",
            zipcode="98109")), content_type='application/json'
                           )
        z_id = json.loads(rv.get_data(as_text=True))['zillow_id']
        pd = PropertyData.objects(zillow_id=z_id)[0]
        pd.zestimate_amount = 5000
        pd.save()
        rv = self.app.post('/property_data', data=json.dumps(dict(
            address="2114 Bigelow Ave",
            zipcode="98109")), content_type='application/json'
                           )
        self.assertEqual(PropertyData.objects.all().count(), 1)
        pd = PropertyData.objects(zillow_id=z_id)[0]
        self.assertNotEqual(pd.zestimate_amount, 5000)

    # Tests if the zillow estimated price is returned when a valid property ID is given.
    def test_price_returned_given_property_id(self):
        rv = self.app.get('/estimated_price/25077638')
        rv_decoded = json.loads(rv.get_data(as_text=True))
        self.assertGreater(int(rv_decoded['estimate']), 0)

    # Tests price is returned from local DB if exists
    def test_price_returned_from_db_given_property_id(self):
        pd = PropertyData(zillow_id='1234567', zestimate_amount='5000')
        pd.save()
        rv = self.app.get('/estimated_price/1234567')
        rv_decoded = json.loads(rv.get_data(as_text=True))
        self.assertEqual(int(rv_decoded['estimate']), 5000)

    # Tests price is returned from zillow api if exists in db but is older than 7 days
    def test_price_returned_from_zillow_if_db_data_stale_given_property_id(self):
        pd = PropertyData(zillow_id='1234567', zestimate_amount='5000')
        pd.created_at = datetime.now()-timedelta(days=8)
        pd.save()
        rv = self.app.get('/estimated_price/1234567')
        rv_decoded = json.loads(rv.get_data(as_text=True))
        self.assertNotEqual(int(rv_decoded['estimate']), 5000)

    # Tests if an error is returned when an invalid property ID is given.
    def test_error_returned_given_invalid_property_id(self):
        rv = self.app.get('/estimated_price/2507763899999999999')
        rv_decoded = json.loads(rv.get_data(as_text=True))
        self.assertEqual(rv_decoded['error']['code'], 500)


if __name__=='__main__':
    unittest.main()