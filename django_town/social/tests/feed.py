from django_town.utils import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from .auth import join, sign_in, sign_out, get_access_token


class SocialFeedTests(TestCase):
    def create_feed(self, feed_name):
        join(self)
        access_token = get_access_token(self)
        return self._create_feed(feed_name, access_token)

    def _create_feed(self, feed_name, access_token):
        response = self.client.post(reverse('FeedsApiView'),  {'name': 'test feed', 'access_token': access_token})
        return response

    def test_feed_create(self):
        """
        Test for creating feed.
        """
        response = self.create_feed("test_feed")
        self.assertEqual(response.status_code, 201)


    def test_feed_delete(self):
        """
        feed delete is not implemented.
        """
        # join(self)
        # access_token = get_access_token(self)
        # response = self._create_feed("test_feed", access_token)
        # self.assertEqual(response.status_code, 201)
        # feed_id = json.loads(response.content)['id']
        #
        # response = self.client.delete(reverse('FeedApiView', kwargs={'pk': feed_id}), {'access_token': access_token})
        # print response


    def test_feed_post(self):
        join(self)
        access_token = get_access_token(self)
        response = self._create_feed("test_feed", access_token)
        self.assertEqual(response.status_code, 201)
        feed_id = json.loads(response.content)['id']
        sign_in(self)
        response = self.client.get(reverse("FeedTokenApiView", kwargs={'pk': feed_id}))
        # print response
        feed_token = json.loads(response.content)['feed_token']
        response = self.client.post(reverse("FeedPostsApiView", kwargs={'pk': feed_id}),
                         {'content': 'test', 'token': feed_token})

        # print response.content
        post_id = json.loads(response.content)['id']
        response = self.client.delete(reverse("PostApiView", kwargs={'pk': post_id}),
                         {'access_token': access_token})

        response = self.client.post(reverse("FeedPostsApiView", kwargs={'pk': feed_id}),
                         {'content': 'test', 'link': json.dumps({'url': 'http://www.daum.net', 'name': 'asdasd'})
                             ,'token': feed_token})

        print response