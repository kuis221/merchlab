from app import db
from flask_login import UserMixin
import firebase_api
from sqlalchemy import func, Index



class User(UserMixin):
    """
    User Class for flask-Login
    """
    def __init__(self, userDetails, addresses=[]):
        self.id = userDetails.get("objectId")
        self.username = userDetails.get("username")
        self.object_id = userDetails.get("objectId")
        self.password = userDetails.get("password")
        self.email = userDetails.get("email")
        self.role = userDetails.get("role")
        self.seller_id = userDetails.get("sellerId")
        self.auth_token = userDetails.get("authToken")
        self.auth_profile = userDetails.get("authProfile") or "jeff"
        self.user_details = userDetails
        self.addresses=addresses
 
    def get_auth_token(self):
        """
        Encode a secure token for cookie
        """
        data = [str(self.id), self.password]
        return login_serializer.dumps(data)
 
    @staticmethod
    def get(user_identifier):
        #print("checking current user", current_user.id, current_user.username)
        #print("hitting the get function", user_identifier)
        if not user_identifier:
            return None

        user = firebase_api.find_user_by_object_id(user_identifier)
        if user == None:
            return None
        
        """
        Static method to search the database and see if userid exists.  If it 
        does exist then return a User Object.  If not then return None as 
        required by Flask-Login. 
        """

        """
        if '@' in user_identifier:
            email = user_identifier
            user = firebase_api.find_user_by_email(email)
        else:
            username = user_identifier
            user = firebase_api.find_user_by_username(username)
        if user == None:
            return None
        """

        return User(user)

class AsinSnapshot(db.Model):
    __tablename = 'asin_snapshot'

    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String())
    salesrank = db.Column(db.Integer())
    salesrank_category = db.Column(db.String())
    list_price = db.Column(db.Float())
    currency_code = db.Column(db.String())    
    timestamp = db.Column(db.String())

    def __init__(self, data):
        self.asin = data.get("asin", "")
        self.salesrank = data.get("salesrank", None)
        self.salesrank_category = data.get("salesrank_category", None)
        self.list_price = data.get("list_price", None)
        self.currency_code = data.get("currency_code", None)
        self.timestamp = data.get("timestamp", "")

class AsinMetadata(db.Model):
    __tablename__ = 'asin_metadata'

    id = db.Column(db.String(), primary_key=True)
    title = db.Column(db.String())
    parent_asin = db.Column(db.String())
    brand = db.Column(db.String())
    image = db.Column(db.String())
    color = db.Column(db.String())
    studio = db.Column(db.String())
    genre = db.Column(db.String())
    manufacturer = db.Column(db.String())
    publisher = db.Column(db.String())
    binding = db.Column(db.String())
    product_group = db.Column(db.String())
    label = db.Column(db.String())
    department = db.Column(db.String())
    product_type_name = db.Column(db.String())
    part_number = db.Column(db.String())
    marketplace_id = db.Column(db.String())
    discovery_keyword = db.Column(db.String())
    search_index = db.Column(db.String())
    browse_node = db.Column(db.String())
    discovery_timestamp = db.Column(db.String())
    removed = db.Column(db.Boolean())
    asin_salesrank = db.Column(db.Integer())
    asin_unthrottled_salesrank = db.Column(db.Integer())

    def __init__(self, data):
        self.title = data.get('title', '')
        self.id = data.get('asin', '')
        self.parent_asin = data.get('parent_asin', '')
        self.brand = data.get('brand', '')
        self.image = data.get('image', '')
        self.color = data.get('color', '')
        self.studio = data.get('studio', '')
        self.genre = data.get('genre', '')
        self.manufacturer = data.get('manufacturer', '')
        self.publisher = data.get('publisher', '')
        self.binding = data.get('binding', '')
        self.product_group = data.get('product_group', '')
        self.label = data.get('label', '')
        self.department = data.get('department', '')
        self.product_type_name = data.get('product_type_name', '')
        self.part_number = data.get('part_number', '')
        self.marketplace_id = data.get('marketplace_id', '')
        self.discovery_keyword = data.get('discovery_keyword', '')
        self.search_index = data.get('search_index', '')
        self.browse_node = data.get('browse_node', '')
        self.discovery_timestamp = data.get('discovery_timestamp', None)
        self.removed = data.get('removed', False)
        self.asin_salesrank = data.get('asin_salesrank')
        self.asin_unthrottled_salesrank = data.get('asin_unthrottled_salesrank')

Index('product_title_case_insensitive', func.lower(AsinMetadata.title))


class IndexedKeyword(db.Model):
    __tablename = 'indexed_keywords'

    id = db.Column(db.String(), primary_key=True)
    last_indexed_date = db.Column(db.String())
    number_of_times_indexed = db.Column(db.Integer())
    first_indexed_date = db.Column(db.String())
    number_of_merch_shirts_found = db.Column(db.Integer())
    average_salesrank_of_shirts_found = db.Column(db.Float())

    def __init__(self, data):
        self.id = data.get("keyword", "")
        self.last_indexed_date = data.get("last_indexed_date", "")
        self.number_of_times_indexed = int(data.get("number_of_times_indexed", "0"))
        self.first_indexed_date = data.get("first_indexed_date", "")
        self.number_of_merch_shirts_found = int(data.get("number_of_merch_shirts_found", "0"))
        self.average_salesrank_of_shirts_found = data.get("average_salesrank_of_shirts_found", None)


class UserQuery(db.Model):
    __tablename = 'user_query'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String())
    user_object_id = db.Column(db.String())
    query_type = db.Column(db.String())
    timestamp = db.Column(db.String())
    query = db.Column(db.String())
    number_of_merch_shirts_found = db.Column(db.Integer())
    average_salesrank = db.Column(db.Float())
    lowest_salesrank = db.Column(db.Float())
    bottom_tenth_percentile_salesrank = db.Column(db.Float())
    average_list_price = db.Column(db.Float())
    lowest_price = db.Column(db.Float())
    highest_price = db.Column(db.Float())
    best_product_image = db.Column(db.String())
    best_product_title = db.Column(db.String())
    best_product_brand = db.Column(db.String())

    def __init__(self, data):
        self.query_type = data.get("query_type", "")
        self.username = data.get("username", None)
        self.user_object_id = data.get("user_object_id", None)
        self.timestamp = data.get("timestamp", None)
        self.query = data.get("query", "").strip()
        self.number_of_merch_shirts_found = data.get("number_of_merch_shirts_found", None)
        self.average_salesrank = data.get("average_salesrank", None)
        self.lowest_salesrank = data.get("lowest_salesrank", None)
        self.bottom_tenth_percentile_salesrank = data.get("bottom_tenth_percentile_salesrank", None)
        self.average_list_price = data.get("average_list_price", None)
        self.lowest_price = data.get("lowest_price", None)
        self.highest_price = data.get("highest_price", None)
        self.best_product_image = data.get("best_product_image", None)
        self.best_product_title = data.get("best_product_title", None)
        self.best_product_brand = data.get("best_product_brand", None)


class AsinAnalytics(db.Model):
    __tablename = 'asin_analytics'

    id = db.Column(db.String(), primary_key=True)
    last_indexed_date = db.Column(db.String())
    last_trademark_indexed_date = db.Column(db.String())
    salesrank = db.Column(db.Integer())
    unthrottled_salesrank = db.Column(db.Integer())
    last_7d_salesrank = db.Column(db.Float())
    last_1mo_salesrank = db.Column(db.Float())
    last_3mo_salesrank = db.Column(db.Float())
    list_price = db.Column(db.Float())
    last_7d_list_price = db.Column(db.Float())
    last_1mo_list_price = db.Column(db.Float())
    last_3mo_list_price = db.Column(db.Float())
    last_7d_volatility = db.Column(db.Float())
    last_1mo_volatility = db.Column(db.Float())
    last_3mo_volatility = db.Column(db.Float())
    escore = db.Column(db.Float())
    weighted_escore_v1 = db.Column(db.Float())
    weighted_escore_v2 = db.Column(db.Float())
    weighted_escore_v3 = db.Column(db.Float())
    streak_score_v1 = db.Column(db.Float())
    streak_score_v2 = db.Column(db.Float())

    def __init__(self, data):
        self.id = data.get("asin", "")
        self.last_indexed_date = data.get("last_indexed_date", None)
        self.salesrank = data.get("salesrank", None)
        self.unthrottled_salesrank = data.get("unthrottled_salesrank", None)
        self.last_7d_salesrank = data.get("last_7d_salesrank", None)
        self.last_1mo_salesrank = data.get("last_1mo_salesrank", None)
        self.last_3mo_salesrank = data.get("last_3mo_salesrank", None)
        self.list_price = data.get("list_price", None)
        self.last_7d_list_price = data.get("last_7d_list_price", None)
        self.last_1mo_list_price = data.get("last_1mo_list_price", None)
        self.last_3mo_list_price = data.get("last_3mo_list_price", None)
        self.last_7d_volatility = data.get("last_7d_volatility", None)
        self.last_1mo_volatility = data.get("last_1mo_volatility", None)
        self.last_3mo_volatility = data.get("last_3mo_volatility", None)
        self.escore = data.get("escore", None)
        self.weighted_escore_v1 = data.get("weighted_escore_v1", None)
        self.weighted_escore_v2 = data.get("weighted_escore_v2", None)
        self.weighted_escore_v3 = data.get("weighted_escore_v3", None)
        self.streak_score_v1 = data.get("streak_score_v1", None)
        self.streak_score_v2 = data.get("streak_score_v2", None)

    def update_item(self, data):
        self.last_indexed_date = data.get("last_indexed_date", self.last_indexed_date)
        self.last_trademark_indexed_date = data.get("last_trademark_indexed_date", self.last_trademark_indexed_date)
        self.salesrank = data.get("salesrank", self.salesrank)
        self.unthrottled_salesrank = data.get("unthrottled_salesrank", self.salesrank)
        self.last_7d_salesrank = data.get("last_7d_salesrank", self.last_7d_salesrank)
        self.last_1mo_salesrank = data.get("last_1mo_salesrank", self.last_1mo_salesrank)
        self.last_3mo_salesrank = data.get("last_3mo_salesrank", self.last_3mo_salesrank)
        self.list_price = data.get("list_price", self.list_price)
        self.last_7d_list_price = data.get("last_7d_list_price", self.last_7d_list_price)
        self.last_1mo_list_price = data.get("last_1mo_list_price", self.last_1mo_list_price)
        self.last_3mo_list_price = data.get("last_3mo_list_price", self.last_3mo_list_price)
        self.last_7d_volatility = data.get("last_7d_volatility", self.last_7d_volatility)
        self.last_1mo_volatility = data.get("last_1mo_volatility", self.last_1mo_volatility)
        self.last_3mo_volatility = data.get("last_3mo_volatility", self.last_3mo_volatility)
        self.escore = data.get("escore", self.escore)
        self.weighted_escore_v1 = data.get("weighted_escore_v1", self.weighted_escore_v1)
        self.weighted_escore_v2 = data.get("weighted_escore_v2", self.weighted_escore_v2)
        self.streak_score_v1 = data.get("streak_score_v1", self.streak_score_v1)
        self.streak_score_v2 = data.get("streak_score_v2", self.streak_score_v2)
