import json

from django import conf

from django.test import TestCase

from mixer.backend.django import mixer


class TestWoDidMiddleware(TestCase):
    def setUp(self):
        self.user = mixer.blend(conf.settings.AUTH_USER_MODEL)
        self.user2 = mixer.blend(conf.settings.AUTH_USER_MODEL)

    def test_create_by_and_update_by(self):

        # 测试作者创建接口在创建作者后, create_by 和 update_by 字段是否有值
        self.client.force_login(self.user)
        res = self.client.post('/api/authors', {
            'name': 'Tom'
        })
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data['create_by'], self.user.pk)
        self.assertEqual(data['update_by'], self.user.pk)

        # 测试书籍创建接口在创建书籍后, create_by 和 update_by 字段是否有值
        author_id = data['id']
        res = self.client.post('/api/books', {
            'name': 'Tome and Jerry',
            'author_id': author_id
        })
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data['create_by'], self.user.pk)
        self.assertEqual(data['update_by'], self.user.pk)

        # 测试书籍名称更新后，update_by 值是否为更新者的值
        book_id = data['id']

        self.client.force_login(self.user2)
        res = self.client.put('/api/books/%s' % book_id, json.dumps({
            'name': 'Tome and Jerry 2',
            'author_id': author_id
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['create_by'], self.user.pk)
        self.assertEqual(data['update_by'], self.user2.pk)
