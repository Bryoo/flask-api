import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')


class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')


class DevelopmentConfig(Config):
    DEBUG = True


app_configs = {
    "testing": TestingConfig,
    "development": DevelopmentConfig
}

"""
#post bucketlist
curl -i -H "Content-Type: application/json" -X POST -d '{"name": "Goto mombasas", "date_created": "2017-07-19 11:43:50","date_updated": "2017-09-20 11:54:50","items": [{"date_created": "2017-09-20 11:54:50","date_updated": "2017-09-27 12:00:50","done": false,"item_id": 1,"name": "Cows are awesome"},{"date_created": "2017-09-20 11:54:50","date_updated": "2017-12-20 11:54:50","done": true,"item_id": 1,"name": "Everybody is a  cow"}]}' http://localhost:5000/api/v1/bucketlist/

# add items
curl -i -H "Content-Type: application/json" -X POST -d '{"date_created": "2017-01-20 11:54:50","date_updated": "2017-02-27 12:00:50","done": false,"item_id": 1,"name": "Cows suck ass"}' http://localhost:5000/api/v1/bucketlist/6/items

#edit items
curl -i -H "Content-Type: application/json" -X PUT -d '{"done": true, "name": "Cows are awesome"}' http://localhost:5000/api/v1/bucketlist/6/items/11

# get bucketlist
curl -i -X GET http://localhost:5000/api/v1/bucketlist/6

# delete item
curl -i -X DELETE http://localhost:5000/api/v1/bucketlist/6/items/11

"""