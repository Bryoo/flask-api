from flask import jsonify, request, abort, make_response
from app.models import User, Bucketlist, Item
from flask import Blueprint
from app import db
from functools import wraps

mod = Blueprint('api', __name__)


def verify_token(func):
    # Get the access token from the header
    @wraps(func)
    def token_verification(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header:
            access_token = auth_header.split(" ")[1]
            if not access_token:
                return jsonify({'message': 'No access token present'})
        else:
            return jsonify({'message': 'No authorization header present'})

        user_id = User.decode_token(access_token)

        if isinstance(user_id, str):
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

        return func(user_id=user_id, *args, **kwargs)

    return token_verification


@mod.route('bucketlist/', methods=['GET', 'POST'])
@mod.route('bucketlist/page=<int:page>', methods=['GET', 'POST'])
@verify_token
def display_all_bucketlist(user_id, page=1):
    limit = int(request.args.get('limit', '2'))
    query = request.args.get('q', '')

    if limit > 3:
        return jsonify({"message": "posts per page shouldn't be more than 3"})

    if request.method == "GET":
        if query:
            bucket_list = Bucketlist.query.filter_by(
                created_by=user_id).filter(
                Bucketlist.name.ilike(
                    '%' + query.replace('"', '') + '%')).order_by(
                Bucketlist.date_updated.desc()).paginate(
                page, limit, False).items

        else:
            bucket_list = Bucketlist.query.filter_by(created_by=user_id).paginate(page, limit, False).items

        result = []
        for member in bucket_list:
            bucket_items = []
            for item in member.items.all():
                item_obj = {
                    'item_id': item.id,
                    'name': item.item_name,
                    'date_created': item.date_created,
                    'date_updated': item.date_updated,
                    'done':item.done
                }
                bucket_items.append(item_obj)

            bucket_obj = {
                'id': member.id,
                'name': member.name,
                'date_created': member.date_created,
                'date_updated': member.date_updated,
                'items': bucket_items,
                'created_by': member.user.email
            }
            result.append(bucket_obj)
        response = jsonify(result)
        response.status_code = 200
        return response

    elif request.method == "POST":
        name = str(request.json.get('name', ''))
        if request.json.get('name', ''):
            items = request.json.get('items', '')

        if name:
            # search for bucketlist with similar name
            existing = Bucketlist.query.filter_by(name=name, created_by=user_id).first()
            if existing:
                response = jsonify({'result': 'Bucketlist already exists'})
                response.status_code = 422
                return response
            user = User.query.get(user_id)
            bucketlist = Bucketlist(name=name, user=user)
            bucketlist.save()
            if items:
                item_list =[]
                for item in items:
                    record = Item(item_name=item['name'], done=item['done'], bucketlist=bucketlist)
                    record.save_items()

                    item_obj = {
                        'item_id': record.id,
                        'name': record.item_name,
                        'date_created': record.date_created,
                        'date_updated': record.date_updated,
                        'done': record.done
                    }
                    item_list.append(item_obj)

                bucket_obj = {
                    'id': bucketlist.id,
                    'name': bucketlist.name,
                    'date_created': bucketlist.date_created,
                    'date_updated': bucketlist.date_updated,
                    'items': item_list,
                    'created_by': bucketlist.created_by
                }
                response = jsonify(bucket_obj)
                response.status_code = 201
                return response


@mod.route('bucketlist/<int:id>', methods=['GET'])
@verify_token
def get_single_item(user_id, id):
    single_list = Bucketlist.query.filter_by(id=id, created_by=user_id).first()
    item_list = []
    if single_list:
        for item in single_list.items.all():
            item_obj = {
                'item_id': item.id,
                'name': item.item_name,
                'date_created': item.date_created,
                'date_updated': item.date_updated,
                'done': item.done
            }
            item_list.append(item_obj)

        bucket_obj = {
            'items': item_list,
            'id': single_list.id,
            'name': single_list.name,
            'date_created': single_list.date_created,
            'date_updated': single_list.date_updated,

        }
        return jsonify(bucket_obj)
    else:
        abort(404)


@mod.route('bucketlist/<int:id>', methods=['PUT'])
@verify_token
def update_bucketlist(user_id, id):
    bucket_name = request.json.get('name')

    bucket_exists = Bucketlist.query.filter_by(name=bucket_name).first()
    if bucket_exists:
        return jsonify({'message': 'bucket name already exists'})

    bucket_entry = Bucketlist.query.filter_by(id=id, created_by=user_id).first()
    if bucket_entry:
        item_list = []
        bucket_entry.name = request.json.get('name', bucket_entry.name)
        db.session.commit()

        for item in bucket_entry.items.all():
            item_obj = {
                'item_id': item.id,
                'name': item.item_name,
                'date_created': item.date_created,
                'date_updated': item.date_updated,
                'done': item.done
            }
            item_list.append(item_obj)

        bucket_obj = {
            'items': item_list,
            'id': bucket_entry.id,
            'name': bucket_entry.name,
            'date_created': bucket_entry.date_created,
            'date_updated': bucket_entry.date_updated,

        }
        response = jsonify(bucket_obj)
        response.status_code = 200
        return response
    else:
        abort(404)


@mod.route('bucketlist/<int:id>', methods=['DELETE'])
@verify_token
def delete_bucketlist(user_id, id):
    del_bucketlist = Bucketlist.query.filter_by(id=id, created_by=user_id).first()
    if del_bucketlist:
        del_bucketlist.delete()
        return jsonify({'result': True})
    else:
        abort(404)


@mod.route('bucketlist/<int:id>/items', methods=['POST'])
@verify_token
def add_items(user_id, id):
    name = str(request.json.get('name', ''))
    done = request.json.get('done', '')

    bucketlist = Bucketlist.query.filter_by(id=id, created_by=user_id).first()
    if bucketlist:
        if request.method == 'POST':
            # search for item with similar name
            item_found = Item.query.filter_by(bucketlist_id=id, item_name=name).first()
            if item_found:
                return jsonify({'message': "Duplicate item found"})

            # add item related to current bucketlist
            item = Item(item_name=name, done=done, bucketlist=bucketlist)
            item.save_items()

            item_list = []
            for member in bucketlist.items.all():

                item_obj = {
                    'item_id': member.id,
                    'name': member.item_name,
                    'date_created': member.date_created,
                    'date_updated': member.date_updated,
                    'done': member.done
                }
                item_list.append(item_obj)

            bucket_obj = {
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_updated': bucketlist.date_updated,
                'items': item_list
            }
            response = jsonify(bucket_obj)
            response.status_code = 201
            return response


@mod.route('bucketlist/<int:id>/items/<int:item_id>', methods=['PUT', 'DELETE'])
@verify_token
def update_items(user_id, id, item_id):
    bucketlist = Bucketlist.query.filter_by(id=id, created_by=user_id).first()
    item = Item.query.filter_by(bucketlist_id=id, id=item_id).first()
    if not item or not bucketlist:
        abort(404)

    if request.method == "PUT":
        if bucketlist:
            item.item_name = request.json.get('name', item.item_name)
            item_done = request.json.get('done', '')
            if item_done in [True, False]:
                item.done = item_done

            db.session.commit()
            item_obj = {
                "item_id": item.id,
                "item_name": item.item_name,
                "date-created": item.date_created,
                "date_updated": item.date_updated,
                "done": item.done
            }
            response = jsonify(item_obj)
            response.status_code = 200
            return response

    else:
        # if request is delete
        if item:
            item.delete()
        return jsonify({'result': True})
