#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPBasicAuth
from flask_pymongo import PyMongo
import pymongo
import numpy as np


app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/prt'
mongo_mgr = PyMongo(app)

@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': error}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': '%s Not Found'%error }), 404)


@auth.get_password
def get_pw(username):
    auths = mongo_mgr.db.auths
    _user = auths.find_one({'username':username})
    if _user:
        return _user['password']
    return None

user_fields = ['firstname', 'lastname', 'latitude', 'longitude']

def get_user_dict(u):
    user = {'id':u['id']}
    for k in user_fields:
        try:
            user[k] = u[k]
        except:
            pass
    return user

@app.route('/prt/api/v1.0/users', methods=['GET'])
@auth.login_required
def get_users():
    """
    Update this to return a json stream defining a listing of the users
    Note: Always return the appropriate response for the action requested.
    """

    output = []
    users = mongo_mgr.db.users.find()
    for user in users:
        output.append(get_user_dict(user))
    return jsonify(output)


@app.route('/prt/api/v1.0/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    users = mongo_mgr.db.users
    user = users.find_one({'id':user_id})
    if user:
        u = get_user_dict(user)
        return jsonify(u)
    return not_found("user {} ".format(user_id))


@app.route('/prt/api/v1.0/users', methods=['POST'])
@auth.login_required
def create_user():
    """
    Should add a new user to the users collection, with validation
    note: Always return the appropriate response for the action requested.
    """
    users = mongo_mgr.db.users
    data = request.get_json()

    for k in user_fields:
        if k not in data:
            return bad_request('Missing param %s'%k)

    last = users.find().sort([('id',pymongo.DESCENDING)]).limit(1)
    new_id = 1
    try:
        new_id += last[0]['id']
    except:
        pass
    data['id'] = new_id
    users.insert(data.copy())
    
    return jsonify(data), 201

@app.route('/prt/api/v1.0/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    """
    Update user specified with user ID and return updated user contents
    Note: Always return the appropriate response for the action requested.
    """
    users = mongo_mgr.db.users
    user = users.find_one({'id': user_id})
    if not user:
        return not_found('User with ID %d ' % user_id)
    input_data = request.get_json()
    input_data['id'] = user_id
    data = get_user_dict(input_data)
    mongo_mgr.db.users.update_one({
        'id': user_id
    }, {
        '$set': data
    }, upsert=False)
    return jsonify(data)


@app.route('/prt/api/v1.0/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    """
    Delete user specified in user ID
    Note: Always return the appropriate response for the action requested.
    """
    users = mongo_mgr.db.users
    user = users.find_one({'id': user_id})
    if not user:
        return not_found('User with ID %d ' % user_id)
    mongo_mgr.db.users.remove({'id': user['id']})
    return jsonify({'message': 'User with ID %d deleted.' % user_id})



@app.route('/prt/api/v1.0/distances', methods=['GET'])
@auth.login_required
def get_distances():
    """
    Each user has a lat/lon associated with them.  Determine the distance
    between each user pair, and provide the min/max/average/std as a json response.
    This should be GET only.
    You can use numpy or whatever suits you
    """

    from math import radians, cos, sin, asin, sqrt
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6371* c
        return km

    def _get_distance(a, b):

        return {
            'user_a' : a,
            'user_b' : b,
            'distance': haversine(a['longitude'], a['latitude'], b['longitude'], b['latitude']) #vincenty(coords_1, coords_2).km
          }


    def get_combinations(s):
        for i, v1 in enumerate(s):
            for j in range(i+1, len(s)):
                yield [v1, s[j]]


    users = []
    for user in mongo_mgr.db.users.find():
      users.append(get_user_dict(user))
    
    distances = []
    for comb in get_combinations(users):
        distances.append(_get_distance(*comb))

    np_distances = np.array([d['distance'] for d in distances])
    stats = {
        'min': np.amin(np_distances, axis=0),
        'max': np.amax(np_distances, axis=0),
        'average': np.mean(np_distances),
        'std': np.std(np_distances)
    }
    return jsonify({'distances': distances, 'stats': stats})


if __name__ == '__main__':
    app.run(debug=True)
