import mongoengine


class AccessToken(mongoengine.Document):
    user_id = mongoengine.IntField()
    client_id = mongoengine.IntField()
    access_token = mongoengine.StringField()
    refresh_token = mongoengine.StringField()
    scope = mongoengine.ListField(mongoengine.StringField())
    expire = mongoengine.DateTimeField()

    meta = {
        'indexes': ['access_token', 'expire'],
    }