import logging
from django.test import TestCase
from django.urls import NoReverseMatch
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APIClient

from .models import (
    User,
    Product,
    Order,
    OrderItem
)


class StoreRestTestCase(TestCase):

    def define_users(self):
        self.easy_password = {
            "email": "user1@test.com",
            "password": "12345",
            "password_confirmation": "12345",
            "birth_date": "1990-09-19"}
        self.no_password_confirmation = {
            "email": "user2@test.com",
            "password": "5dnoewqhndf23i",
            "password_confirmation": "",
            "birth_date": "1990-09-19"}
        self.user1 = {
            "email": "user1@test.com",
            "password": "dcwsdcwsqfdwe",
            "password_confirmation": "dcwsdcwsqfdwe",
            "birth_date": "1990-09-19"}
        self.email_exists = {
            "email": "user1@test.com",
            "password": "wefcwefew2",
            "password_confirmation": "wefcwefew2",
            "birth_date": "1999-09-19"}
        self.birth_date_wrong = {
            "email": "user1@test.com",
            "password": "wefcwefew2",
            "password_confirmation": "wefcwefew2",
            "birth_date": "09-19-1999"}
        self.user2 = {
            "email": "user2@test.com",
            "password": "wefcwefew2",
            "password_confirmation": "wefcwefew2",
            "birth_date": "1990-09-19"}
        self.user3 = {
            "email": "user3@test.com",
            "password": "wefcwefew2",
            "password_confirmation": "wefcwefew2",
            "birth_date": "1999-09-19"}

    def define_products(self):
        self.empty_product = {}
        self.non_named_product = {'name': '', 'description': 'non_named_product', 'price': '5.50'}
        self.non_detailed_product = {'name': 'no detail', 'description': '', 'price': '5.50'}
        self.non_priced_product = {'name': 'no priced', 'description': 'no priced product', 'price': ''}
        self.negative_priced_product = {'name': 'negative priced', 'description': 'dsc', 'price': '-5.50'}
        self.product1 = {'name': 'product1', 'description': 'product1 description', 'price': '5.50'}
        self.product2 = {'name': 'product2', 'description': 'product2 description', 'price': '4.51'}
        self.product2_updt = {'name': 'product2', 'description': 'product2 description', 'price': '5.51'}
        self.product3 = {'name': 'product3', 'description': 'product3 description', 'price': '5.52'}
        self.product4 = {'name': 'product4', 'description': 'product4 description', 'price': '5.53'}
        self.product5 = {'name': 'product5', 'description': 'product5 description', 'price': '5.54'}
        self.product6 = {'name': 'product6', 'description': 'product6 description', 'price': '101.5'}
        pass

    def define_orders(self):
        self.empty_user_order = {}
        self.non_existent_user_order = {'user': 367}
        self.negative_value_user_order = {'user': -21}
        self.order1_user1 = {'user': 1}
        self.order1_user2 = {'user': 2}
        self.order1_user3 = {'user': 3}
        self.order2_user1 = {'user': 1}
        self.order3_user2 = {'user': 2}  # This will be an error order, to be fixed to user 1
        self.order3_user1 = {'user': 1}
        pass

    def define_order_items(self):
        self.no_product_no_order_no_quantity = {}
        self.no_product_no_order_quantity = {'quantity': 3}
        self.no_product_no_order_quantity_negative = {'quantity': -3}
        self.no_product_no_order_quantity_float = {'quantity': 3.4}
        self.no_product_order_no_quantity = {'order': 1}
        self.no_product_order_quantity = {'order': 1, 'quantity': 3}
        self.no_product_order_quantity_negative = {'order': 1, 'quantity': -3}
        self.no_product_order_quantity_float = {'order': 1, 'quantity': 3.4}
        self.no_product_invalid_order_no_quantity = {'order': 1001}
        self.no_product_invalid_order_quantity = {'order': 1001, 'quantity': 3}
        self.no_product_invalid_order_quantity_negative = {'order': 1001, 'quantity': -3}
        self.no_product_invalid_order_quantity_float = {'order': 1001, 'quantity': 3.4}
        self.product_no_order_no_quantity = {'product': 1}
        self.product_no_order_quantity = {'product': 1, 'quantity': 3}
        self.product_no_order_quantity_negative = {'product': 1, 'quantity': -3}
        self.product_no_order_quantity_float = {'product': 1, 'quantity': 3.4}
        self.invalid_product_no_order_no_quantity = {'product': 1001}
        self.invalid_product_no_order_quantity = {'product': 1001, 'quantity': 3}
        self.invalid_product_no_order_quantity_negative = {'product': 1001, 'quantity': -3}
        self.invalid_product_no_order_quantity_float = {'product': 1001, 'quantity': 3.4}
        self.invalid_product_order_no_quantity = {'product': 1001, 'order': 1}
        self.invalid_product_order_quantity = {'product': 1001, 'order': 1, 'quantity': 3}
        self.invalid_product_order_quantity_negative = {'product': 1001, 'order': 1, 'quantity': -3}
        self.invalid_product_order_quantity_float = {'product': 1001, 'order': 1, 'quantity': 3.4}
        self.product_order_no_quantity = {'product': 1001, 'order': 1}
        self.product_order_quantity_negative = {'product': 1001, 'order': 1, 'quantity': -3}
        self.product_order_quantity_float = {'product': 1001, 'order': 1, 'quantity': 3.4}

        """Orders:
            Order1 User1: +1 products > 100, Each qtt > 1
            User2: 1 product > 100 qtt > 1
            User3: 1 product > 100 qtt = 1
            Order2 User1: +1 Product < 100, Each qtt >1
            Order3 User1: +1 Product < 100, Each qtt >1
        """
        self.product1_order1_user1 = {'product': 1, 'order': 1, 'quantity': 5}
        self.product2_order1_user1 = {'product': 2, 'order': 1, 'quantity': 10}
        self.product3_order1_user1 = {'product': 3, 'order': 1, 'quantity': 8}
        self.product1_order2_user1 = {'product': 1, 'order': 4, 'quantity': 3}
        self.product5_order2_user1 = {'product': 5, 'order': 4, 'quantity': 2}
        self.product4_order1_user2 = {'product': 4, 'order': 2, 'quantity': 20}
        self.product6_order1_user3 = {'product': 6, 'order': 3, 'quantity': 1}
        self.product4_order3_user1 = {'product': 5, 'order': 5, 'quantity': 2}
        self.product1_order3_user1 = {'product': 1, 'order': 5, 'quantity': 3}
        self.product3_order3_user1 = {'product': 3, 'order': 5, 'quantity': 4}

    def setUser(self):
        #   Recreate users (each routine erases the DB)
        self.test_api_register_user()
        # Retrieve the user1 from the DB and ensure it exists
        user1 = User.objects.get(email='user1@test.com')
        self.assertEqual(user1.email, 'user1@test.com')
        # Authenticate user 1
        token = self.client.post(
            reverse('store_api:get_token'),
            data={'username': 'user1@test.com', 'password': 'dcwsdcwsqfdwe'})
        self.assertEqual(token.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=user1)
        # Consider user 1 authenticated
        return user1

    def setUp(self):
        self.client = APIClient()
        self.define_users()
        self.define_products()
        self.define_orders()
        self.define_order_items()

    def test_get_authorization_is_enforced(self):
        """First Test
        Check the endpoints that need authentication prior to authenticate.
        """
        failed_products_access = self.client.get(reverse("store_api:products"))
        self.assertEqual(failed_products_access.status_code, status.HTTP_403_FORBIDDEN)
        failed_users_access = self.client.get(reverse("store_api:users"))
        self.assertEqual(failed_users_access.status_code, status.HTTP_403_FORBIDDEN)
        failed_orders_access = self.client.get(reverse("store_api:orders"))
        self.assertEqual(failed_orders_access.status_code, status.HTTP_403_FORBIDDEN)
        failed_order_items_access = self.client.get(reverse("store_api:order_items"))
        self.assertEqual(failed_order_items_access.status_code, status.HTTP_403_FORBIDDEN)
        failed_product_access = self.client.get(reverse("store_api:product", kwargs={'pk': 1}))
        self.assertEqual(failed_product_access.status_code, status.HTTP_403_FORBIDDEN)
        failed_user_access = self.client.get(reverse("store_api:user", kwargs={'pk': 1}))
        self.assertEqual(failed_user_access.status_code, status.HTTP_403_FORBIDDEN)
        failed_user_orders_access = self.client.get(reverse("store_api:user_orders", kwargs={'pk': 1}))
        self.assertEqual(failed_user_orders_access.status_code, status.HTTP_403_FORBIDDEN)
        failed_order_access = self.client.get(reverse("store_api:order", kwargs={'pk': 1}))
        self.assertEqual(failed_order_access.status_code, status.HTTP_403_FORBIDDEN)
        failed_order_item_access = self.client.get(reverse("store_api:order_item", kwargs={'pk': 1}))
        self.assertEqual(failed_order_item_access.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_authorization_is_enforced(self):
        """First Test
        Check the endpoints that need authentication prior to authenticate.
        """
        prod_update = {
            'name': 'to_fail',
            'description': 'this should have failed!',
            'price': '5.00'
        }
        user_update = {
            'email': 'failed_update@fail.com',
            'password': 'failed_password',
            'password_confirmation': 'failed_password',
            'birth_date': '1999-12-31'
        }
        order_update = {
            'user': '1'
        }
        order_item_update = {
            'order': '1',
            'product': '1',
            'quantity': '1'
        }
        failed_product_update = self.client.put(reverse("store_api:product", kwargs={'pk': 1}), data=prod_update)
        self.assertEqual(failed_product_update.status_code, status.HTTP_403_FORBIDDEN)
        failed_user_update = self.client.put(reverse("store_api:user", kwargs={'pk': 1}), data=user_update)
        self.assertEqual(failed_user_update.status_code, status.HTTP_403_FORBIDDEN)
        failed_order_update = self.client.put(reverse("store_api:order", kwargs={'pk': 1}), data=order_update)
        self.assertEqual(failed_order_update.status_code, status.HTTP_403_FORBIDDEN)
        failed_order_item_update = self.client.put(
            reverse("store_api:order_item", kwargs={'pk': 1}), data=order_item_update)
        self.assertEqual(failed_order_item_update.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_authorization_required(self):
        """
        Authorization in posts are not required only for users
        :return:
        """
        prod_create = {
            'name': 'to_fail',
            'description': 'this should have failed!',
            'price': '5.00'
        }
        order_create = {
            'user': '1'
        }
        order_item_create = {
            'order': '1',
            'product': '1',
            'quantity': '1'
        }
        failed_product_create = self.client.post(reverse("store_api:products_create"), data=prod_create)
        self.assertEqual(failed_product_create.status_code, status.HTTP_403_FORBIDDEN)
        failed_order_create = self.client.post(reverse("store_api:orders_create"), data=order_create)
        self.assertEqual(failed_order_create.status_code, status.HTTP_403_FORBIDDEN)
        failed_order_item_create = self.client.post(reverse("store_api:order_items"), data=order_item_create)
        self.assertEqual(failed_order_item_create.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_register_user(self):

        res_easy_password = self.client.post(reverse('store_api:register'), data=self.easy_password)
        res_no_password_confirmation = self.client.post(reverse('store_api:register'),
                                                        data=self.no_password_confirmation)
        res_user1 = self.client.post(reverse('store_api:register'), data=self.user1)
        res_email_exists = self.client.post(reverse('store_api:register'), data=self.email_exists)
        res_birth_date_wrong = self.client.post(reverse('store_api:register'), data=self.birth_date_wrong)
        res_user2 = self.client.post(reverse('store_api:register'), data=self.user2)
        res_user3 = self.client.post(reverse('store_api:register'), data=self.user3)
        self.assertEqual(res_easy_password.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_password_confirmation.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_email_exists.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_birth_date_wrong.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_user2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_user3.status_code, status.HTTP_201_CREATED)

    def test_api_users(self):
        #   Recreate users (each routine erases the DB)
        self.test_api_register_user()
        # Retrieve the user1 from the DB and ensure it exists
        user1 = User.objects.filter(email='user1@test.com').first()
        self.assertEqual(user1.email, 'user1@test.com')
        # Authenticate user 1
        token = self.client.post(
            reverse('store_api:get_token'),
            data={'username': 'user1@test.com', 'password': 'dcwsdcwsqfdwe'})
        self.assertEqual(token.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=user1)
        # Retrieve users list
        users_list = self.client.get(reverse('store_api:users'))
        self.assertEqual(users_list.status_code, status.HTTP_200_OK)
        # there are 3 users
        self.assertEqual(len(users_list.data['results']), 3)
        # Retrieve user 1
        print(user1.id)
        res_user1_retrieved = self.client.get(reverse('store_api:user', kwargs={'pk': user1.id}))
        self.assertEqual(res_user1_retrieved.status_code, status.HTTP_200_OK)
        # Retrieve user 2 (this should not happen)
        res_user2_retrieved = self.client.get(reverse('store_api:user', kwargs={'pk': 2}))
        self.assertEqual(res_user2_retrieved.status_code, status.HTTP_403_FORBIDDEN)
        # Retrieve user 100
        res_user100_retrieved = self.client.get(reverse('store_api:user', kwargs={'pk': 100}))
        self.assertEqual(res_user100_retrieved.status_code, status.HTTP_404_NOT_FOUND)
        # Retrieve user -1
        try:
            res_user_neg_retrieved = self.client.get(reverse('store_api:user', kwargs={'pk': -1}))
        except NoReverseMatch:
            pass
        self.assertRaises(NoReverseMatch)
        # update user 1
        res_updt_user1 = self.client.put(reverse('store_api:user', kwargs={'pk': user1.id}), data={
            'email': user1.email,
            'password': user1.password,
            'password_confirmation': user1.password,
            'birth_date': '1989-10-10'
        })
        self.assertEqual(res_updt_user1.status_code, status.HTTP_200_OK)
        # update user 2
        res_updt_user2 = self.client.put(reverse('store_api:user', kwargs={'pk': 2}), data={
            'email': 'user2@test.com',
            'password': 'mfoikpjfw',
            'password_confirmation': 'mfoikpjfw',
            'birth_date': '1989-10-10'
        })
        self.assertEqual(res_updt_user2.status_code, status.HTTP_403_FORBIDDEN)
        # retrieve user_orders from user 1 to check access
        res_orders_user_1 = self.client.get(reverse('store_api:user_orders', kwargs={'pk': 1}))
        self.assertEqual(res_orders_user_1.status_code, status.HTTP_200_OK)
        # retrieve user_orders from user 2 to check access
        res_orders_user_2 = self.client.get(reverse('store_api:user_orders', kwargs={'pk': 2}))
        self.assertEqual(res_orders_user_2.status_code, status.HTTP_403_FORBIDDEN)
        pass

    def setProducts(self):
        # create products 1 - 6
        res_prod1_staff = self.client.post(reverse('store_api:products_create'), data=self.product1)
        self.assertEqual(res_prod1_staff.status_code, status.HTTP_201_CREATED)
        res_create_prod2 = self.client.post(reverse('store_api:products_create'), data=self.product2)
        self.assertEqual(res_create_prod2.status_code, status.HTTP_201_CREATED)
        res_create_prod3 = self.client.post(reverse('store_api:products_create'), data=self.product3)
        self.assertEqual(res_create_prod3.status_code, status.HTTP_201_CREATED)
        res_create_prod4 = self.client.post(reverse('store_api:products_create'), data=self.product4)
        self.assertEqual(res_create_prod4.status_code, status.HTTP_201_CREATED)
        res_create_prod5 = self.client.post(reverse('store_api:products_create'), data=self.product5)
        self.assertEqual(res_create_prod5.status_code, status.HTTP_201_CREATED)
        res_create_prod6 = self.client.post(reverse('store_api:products_create'), data=self.product6)
        self.assertEqual(res_create_prod6.status_code, status.HTTP_201_CREATED)

    def test_api_products(self):
        user1 = self.setUser()
        # create product 1 without permission (need to be staff)
        res_prod1_non_staff = self.client.post(reverse('store_api:products_create'), data=self.product1)
        self.assertEqual(res_prod1_non_staff.status_code, status.HTTP_403_FORBIDDEN)
        # set user1 as staff and create prod1
        user1.is_staff = True
        user1.save()
        # create_empty_product
        res_empty_prod = self.client.post(reverse('store_api:products_create'), data=self.empty_product)
        self.assertEqual(res_empty_prod.status_code, status.HTTP_400_BAD_REQUEST)
        # create non_named_product
        res_non_named_prod = self.client.post(reverse('store_api:products_create'), data=self.non_named_product)
        self.assertEqual(res_non_named_prod.status_code, status.HTTP_400_BAD_REQUEST)
        # create non_detailed_product
        res_non_detailed_prod = self.client.post(reverse('store_api:products_create'), data=self.non_detailed_product)
        self.assertEqual(res_non_detailed_prod.status_code, status.HTTP_400_BAD_REQUEST)
        # create non_priced_product
        res_non_priced_prod = self.client.post(reverse('store_api:products_create'), data=self.non_priced_product)
        self.assertEqual(res_non_priced_prod.status_code, status.HTTP_400_BAD_REQUEST)
        # create negative_priced_product
        res_negative_priced_prod = self.client.post(reverse('store_api:products_create'),
                                                    data=self.negative_priced_product)
        self.assertEqual(res_negative_priced_prod.status_code, status.HTTP_400_BAD_REQUEST)
        self.setProducts()
        # update product 2
        res_updt_prod2 = self.client.put(reverse('store_api:product', kwargs={'pk': 2}), data=self.product2_updt)
        self.assertEqual(res_updt_prod2.status_code, status.HTTP_200_OK)
        # retrieve product 4
        res_prod4 = self.client.get(reverse('store_api:product', kwargs={'pk': 4}))
        self.assertEqual(res_prod4.status_code, status.HTTP_200_OK)
        # test high_order access
        res_high_order = self.client.get(reverse('store_api:high_orders'))
        self.assertEqual(res_high_order.status_code, status.HTTP_200_OK)

    def setOrders(self):
        # create order 1 user 1
        res_order1_user1 = self.client.post(reverse('store_api:orders_create'), data=self.order1_user1)
        self.assertEqual(res_order1_user1.status_code, status.HTTP_201_CREATED)
        # create order 1 user 2
        res_order1_user2 = self.client.post(reverse('store_api:orders_create'), data=self.order1_user2)
        self.assertEqual(res_order1_user2.status_code, status.HTTP_201_CREATED)
        # create order 1 user 3
        res_order1_user3 = self.client.post(reverse('store_api:orders_create'), data=self.order1_user3)
        self.assertEqual(res_order1_user3.status_code, status.HTTP_201_CREATED)
        # create order 2 user 1
        res_order2_user1 = self.client.post(reverse('store_api:orders_create'), data=self.order2_user1)
        self.assertEqual(res_order2_user1.status_code, status.HTTP_201_CREATED)
        # create order 3 user 1 (as user 2)
        res_order3_user2 = self.client.post(reverse('store_api:orders_create'), data=self.order3_user2)
        self.assertEqual(res_order1_user1.status_code, status.HTTP_201_CREATED)
        # update order 3 fixing to user 1
        res_order3_user1 = self.client.put(reverse('store_api:order', kwargs={'pk': 5}), data=self.order3_user1)
        self.assertEqual(res_order3_user1.status_code, status.HTTP_200_OK)
        # retrieve order 1 user 1

    def test_api_orders(self):
        user1 = self.setUser()
        user1.is_staff = True
        user1.save()
        self.setOrders()

    def setInvalidOrdersItems(self):
        res_no_product_no_order_no_quantity = self.client.post(reverse('store_api:order_items'),
                                                               data=self.no_product_no_order_no_quantity)
        res_no_product_no_order_quantity = self.client.post(reverse('store_api:order_items'),
                                                            data=self.no_product_no_order_quantity)
        res_no_product_no_order_quantity_negative = self.client.post(reverse('store_api:order_items'),
                                                                     data=self.no_product_no_order_quantity_negative)
        res_no_product_no_order_quantity_float = self.client.post(reverse('store_api:order_items'),
                                                                  data=self.no_product_no_order_quantity_float)
        res_no_product_order_no_quantity = self.client.post(reverse('store_api:order_items'),
                                                            data=self.no_product_order_no_quantity)
        res_no_product_order_quantity = self.client.post(reverse('store_api:order_items'),
                                                         data=self.no_product_order_quantity)
        res_no_product_order_quantity_negative = self.client.post(reverse('store_api:order_items'),
                                                                  data=self.no_product_order_quantity_negative)
        res_no_product_order_quantity_float = self.client.post(reverse('store_api:order_items'),
                                                               data=self.no_product_order_quantity_float)
        res_no_product_invalid_order_no_quantity = self.client.post(reverse('store_api:order_items'),
                                                                    data=self.no_product_invalid_order_no_quantity)
        res_no_product_invalid_order_quantity = self.client.post(reverse('store_api:order_items'),
                                                                 data=self.no_product_invalid_order_quantity)
        res_no_product_invalid_order_quantity_negative = self.client.post(reverse('store_api:order_items'),
                                                                          data=self.no_product_invalid_order_quantity_negative)
        res_no_product_invalid_order_quantity_float = self.client.post(reverse('store_api:order_items'),
                                                                       data=self.no_product_invalid_order_quantity_float)
        res_product_no_order_no_quantity = self.client.post(reverse('store_api:order_items'),
                                                            data=self.product_no_order_no_quantity)
        res_product_no_order_quantity = self.client.post(reverse('store_api:order_items'),
                                                         data=self.product_no_order_quantity)
        res_product_no_order_quantity_negative = self.client.post(reverse('store_api:order_items'),
                                                                  data=self.product_no_order_quantity_negative)
        res_product_no_order_quantity_float = self.client.post(reverse('store_api:order_items'),
                                                               data=self.product_no_order_quantity_float)
        res_invalid_product_no_order_no_quantity = self.client.post(reverse('store_api:order_items'),
                                                                    data=self.invalid_product_no_order_no_quantity)
        res_invalid_product_no_order_quantity = self.client.post(reverse('store_api:order_items'),
                                                                 data=self.invalid_product_no_order_quantity)
        res_invalid_product_no_order_quantity_negative = self.client.post(reverse('store_api:order_items'),
                                                                          data=self.invalid_product_no_order_quantity_negative)
        res_invalid_product_no_order_quantity_float = self.client.post(reverse('store_api:order_items'),
                                                                       data=self.invalid_product_no_order_quantity_float)
        res_invalid_product_order_no_quantity = self.client.post(reverse('store_api:order_items'),
                                                                 data=self.invalid_product_order_no_quantity)
        res_invalid_product_order_quantity = self.client.post(reverse('store_api:order_items'),
                                                              data=self.invalid_product_order_quantity)
        res_invalid_product_order_quantity_negative = self.client.post(reverse('store_api:order_items'),
                                                                       data=self.invalid_product_order_quantity_negative)
        res_invalid_product_order_quantity_float = self.client.post(reverse('store_api:order_items'),
                                                                    data=self.invalid_product_order_quantity_float)
        res_product_order_no_quantity = self.client.post(reverse('store_api:order_items'),
                                                         data=self.product_order_no_quantity)
        res_product_order_quantity_negative = self.client.post(reverse('store_api:order_items'),
                                                               data=self.product_order_quantity_negative)
        res_product_order_quantity_float = self.client.post(reverse('store_api:order_items'),
                                                            data=self.product_order_quantity_float)

        self.assertEqual(res_no_product_no_order_no_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_no_order_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_no_order_quantity_negative.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_no_order_quantity_float.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_order_no_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_order_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_order_quantity_negative.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_order_quantity_float.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_invalid_order_no_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_invalid_order_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_invalid_order_quantity_negative.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_product_invalid_order_quantity_float.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_product_no_order_no_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_product_no_order_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_product_no_order_quantity_negative.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_product_no_order_quantity_float.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_invalid_product_no_order_no_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_invalid_product_no_order_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_invalid_product_no_order_quantity_negative.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_invalid_product_no_order_quantity_float.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_invalid_product_order_no_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_invalid_product_order_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_invalid_product_order_quantity_negative.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_invalid_product_order_quantity_float.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_product_order_no_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_product_order_quantity_negative.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_product_order_quantity_float.status_code, status.HTTP_400_BAD_REQUEST)

    def setOrdersItems(self):
        """Orders:
            Order1 User1: +1 products > 100, Each qtt > 1
            User2: 1 product > 100 qtt > 1
            User3: 1 product > 100 qtt = 1
            Order2 User1: +1 Product < 100, Each qtt >1
            Order3 User1: +1 Product < 100, Each qtt >1
        """
        res_product1_order1_user1 = self.client.post(reverse('store_api:order_items'), data=self.product1_order1_user1)
        res_product2_order1_user1 = self.client.post(reverse('store_api:order_items'), data=self.product1_order2_user1)
        res_product3_order1_user1 = self.client.post(reverse('store_api:order_items'), data=self.product1_order3_user1)
        res_product1_order2_user1 = self.client.post(reverse('store_api:order_items'), data=self.product2_order1_user1)
        res_product5_order2_user1 = self.client.post(reverse('store_api:order_items'), data=self.product3_order1_user1)
        res_product4_order1_user2 = self.client.post(reverse('store_api:order_items'), data=self.product3_order3_user1)
        res_product6_order1_user3 = self.client.post(reverse('store_api:order_items'), data=self.product4_order1_user2)
        res_product4_order3_user1 = self.client.post(reverse('store_api:order_items'), data=self.product4_order3_user1)
        res_product1_order3_user1 = self.client.post(reverse('store_api:order_items'), data=self.product5_order2_user1)
        res_product3_order3_user1 = self.client.post(reverse('store_api:order_items'), data=self.product6_order1_user3)

        print(res_product1_order1_user1)

        self.assertEqual(res_product1_order1_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_product2_order1_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_product3_order1_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_product1_order2_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_product5_order2_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_product4_order1_user2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_product6_order1_user3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_product4_order3_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_product1_order3_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_product3_order3_user1.status_code, status.HTTP_201_CREATED)
        pass

    def test_api_orders_items(self):
        user1 = self.setUser()
        user1.is_staff = True
        user1.save()
        self.setProducts()
        self.setOrders()
        # Consider user 1 authenticated
        # create order items (with error)
        self.setInvalidOrdersItems()
        # create order items Ok
        self.setOrdersItems()
        # update order items
        # list order items
        # view order item
        pass

    def test_api_extra(self):
        # Consider user 1 authenticated
        # retrieve orders from user 1
        # retrieve orders from user 2
        # search products with query
        # retrieve products in high orders with multiple products
        pass
