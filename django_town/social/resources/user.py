import datetime
from django_town.utils import json, urlopen, urlencode, HTTPError

from django.db import transaction, IntegrityError
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from django_town.rest import ModelResource, RestFormRequired, RestFormInvalid, RestAlreadyExists
from django_town.facebook import get_object
from django_town.social.models import User, UserFacebook, UserGoogle


class UserResource(ModelResource):
    def data_with_facebook(self, access_token):
        # TODO apply facebook v2 api.
        profile = get_object('me', fields="id,name,bio,birthday,locale,timezone,gender,email,picture",
                             access_token=access_token)
        fb_id = profile['id']
        bio = profile.get('bio', '')
        photo_url = "http://graph.facebook.com/%s/picture?width=400&height=400" % fb_id \
            if not profile['picture']['data']['is_silhouette'] else None

        if photo_url:
            img_temp = NamedTemporaryFile()
            img_temp.write(urlopen(photo_url).read())
            img_temp.flush()
            img_temp.seek(0)
            photo = File(img_temp)
        else:
            photo = None

        name = profile['name']
        email = profile.get('email', '#' + fb_id + '@inva.lid')
        timezone = profile.get('timezone', 0)
        dob = datetime.datetime.strptime(profile['birthday'], "%m/%d/%Y") if 'birthday' in profile else None
        locale = profile.get('locale', 'en')[:2]
        gender = profile.get('gender', 'U')
        if gender == 'male':
            gender = 'M'
        elif gender == 'female':
            gender = 'F'
        data = {'name': name, 'dob': dob, 'locale': locale, 'email': email,
                'timezone_offset': timezone, 'gender': gender, 'bio': bio, 'fb_id': fb_id}
        if photo:
            files = {'photo': photo}
        else:
            files = None
        return data, files

    def data_with_google(self, access_token):
        try:
            ret = urlopen("https://www.googleapis.com/plus/v1/people/me?" +
                                  urlencode({'access_token': access_token})).read()
            email_ret = urlopen("https://www.googleapis.com/oauth2/v3/userinfo?" +
                                        urlencode({'access_token': access_token, 'fields': 'email'})).read()
            email = json.loads(email_ret)['email']
            user_data = json.loads(ret)
            if not user_data['isPlusUser'] or not email:
                return None, None
            google_id = user_data['id']
            name = user_data['displayName']
            try:
                locale = user_data['language']
            except KeyError:
                locale = "en"
            gender = user_data.get('gender', 'unknown')
            if gender == 'male':
                gender = 'M'
            elif gender == 'female':
                gender = 'F'
            # location = user_data.get('currentLocation','')
            photo_url = user_data.get('image', {'url': None}).get('url')
            if photo_url:
                img_temp = NamedTemporaryFile()
                img_temp.write(urlopen(photo_url).read())
                img_temp.flush()
                img_temp.seek(0)
                photo = File(img_temp)
            else:
                photo = None
            data = {'name': name, 'locale': locale, 'email': email, 'gender': gender, 'google_id': google_id}
            if photo:
                files = {'photo': photo}
            else:
                files = None
            return data, files
        except HTTPError:
            return None, None

    def create(self, data=None, files=None, acceptable=None, required=None, exclude=None, request=None,
               request_kwargs=None):
        if data:
            self.validate_create(data=data, files=files, acceptable=acceptable,
                                 required=required, exclude=exclude)
            if 'facebook_access_token' in data:
                new_data, new_files = self.data_with_facebook(data['facebook_access_token'])
                if not new_data:
                    raise RestFormInvalid('facebook_access_token')
                email = new_data['email']

                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = None

                with transaction.atomic():
                    fb_id = new_data['fb_id']
                    del new_data['fb_id']
                    if not user:
                        user, created = self.create_from_db(data=new_data, files=new_files)
                    new_data['user'] = user
                    try:
                        user_facebook = UserFacebook.objects.get(facebook_id=fb_id)
                    except UserFacebook.DoesNotExist:
                        user_facebook = None
                    if not user_facebook:
                        UserFacebook(user=user, facebook_id=fb_id,
                                     access_token=data['facebook_access_token']).save()
                    else:
                        if user_facebook.user != user:
                            user_facebook.delete()
                            UserFacebook(user=user, facebook_id=fb_id,
                                         access_token=data['facebook_access_token']).save()
                        else:
                            user_facebook.access_token = data['facebook_access_token']
                            user_facebook.save()
                    return self._meta.resource_instance_cls(user.pk, self, instance=user)
            elif 'google_access_token' in data:
                new_data, new_files = self.data_with_google(data['google_access_token'])
                if not new_data:
                    raise RestFormInvalid('google_access_token')

                email = new_data['email']

                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = None

                with transaction.atomic():
                    google_id = new_data['google_id']
                    del new_data['google_id']
                    if not user:
                        user, created = self.create_from_db(data=new_data, files=new_files)
                    new_data['user'] = user
                    try:
                        user_google = UserGoogle.objects.get(google_id=google_id)
                    except UserGoogle.DoesNotExist:
                        user_google = None
                    if not user_google:
                        UserGoogle(user=user, google_id=google_id, email=email).save()
                    else:
                        if user_google.user != user:
                            user_google.delete()
                            UserGoogle(user=user, google_id=google_id, email=email).save()
                        elif user_google.email != email:
                            user_google.email = email
                            user_google.save()
                    del new_data['email']
                    return self._meta.resource_instance_cls(user.pk, self, instance=user)
            elif 'email' in data and 'password' in data:
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(data['email'], password=data['password'])
                        if 'photo' in files:
                            user.photo = files['photo']
                        user.save()
                        return self._meta.resource_instance_cls(user.pk, self, instance=user)
                except IntegrityError:
                    raise RestAlreadyExists('email')

            else:
                if 'email' in data:
                    raise RestFormRequired('password')
                raise RestFormRequired('email')
        else:
            raise RestFormRequired('email')

    class Meta:
        model = User
        cache_key_format = "_ut_user:%(pk)s"
        exclude = ['password', 'is_super', 'is_active', 'is_staff']
        create_acceptable = ['email', 'facebook_access_token', 'google_access_token', 'password', 'name', 'photo']

user_public_resource = UserResource(filter=['id', 'name', 'photo'])


class UserFollowResource(ModelResource):
    pass