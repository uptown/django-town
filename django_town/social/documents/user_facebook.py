import mongoengine


class UserFacebook(mongoengine.Document):
    me = mongoengine.DictField()
    likes = mongoengine.ListField(mongoengine.DictField())
