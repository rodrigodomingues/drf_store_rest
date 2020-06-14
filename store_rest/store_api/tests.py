import logging
from django.test import TestCase
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


    def test_authorization_is_enforced(self):
        self.client = APIClient()

    def test_api_register_user(self):
        easy_password = {
            "email": "user1@test.com",
            "password": "12345",
            "password_confirmation": "12345",
            "birth_date": "1990-09-19"}
        no_password_confirmation = {
            "email": "user2@test.com",
            "password": "5dnoewqhndf23i",
            "password_confirmation": "",
            "birth_date": "1990-09-19"}
        user1 = {
            "email": "user1@test.com",
            "password": "dcwsdcwsqfdwe",
            "password_confirmation": "dcwsdcwsqfdwe",
            "birth_date": "1990-09-19"}
        email_exists = {
            "email": "user1@test.com",
            "password": "wefcwefew2",
            "password_confirmation": "wefcwefew2",
            "birth_date": "1999-09-19"}
        birth_date_wrong = {
            "email": "user1@test.com",
            "password": "wefcwefew2",
            "password_confirmation": "wefcwefew2",
            "birth_date": "09-19-1999"}
        user2 = {
            "email": "user2@test.com",
            "password": "wefcwefew2",
            "password_confirmation": "wefcwefew2",
            "birth_date": "1990-09-19"}
        user3 = {
            "email": "user3@test.com",
            "password": "wefcwefew2",
            "password_confirmation": "wefcwefew2",
            "birth_date": "1999-09-19"}
        res_easy_password = self.client.post(reverse('store_api:register'), data=easy_password)
        res_no_password_confirmation = self.client.post(reverse('store_api:register'), data=no_password_confirmation)
        res_user1 = self.client.post(reverse('store_api:register'), data=user1)
        res_email_exists = self.client.post(reverse('store_api:register'), data=email_exists)
        res_birth_date_wrong = self.client.post(reverse('store_api:register'), data=birth_date_wrong)
        res_user2 = self.client.post(reverse('store_api:register'), data=user2)
        res_user3 = self.client.post(reverse('store_api:register'), data=user3)
        self.assertEqual(res_easy_password.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_no_password_confirmation.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_email_exists.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_birth_date_wrong.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_user2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_user3.status_code, status.HTTP_201_CREATED)



    def test_api_products(self):
        pass

    def test_api_orders(self):
        pass

    def test_api_orders_items(self):
        pass

    def test_api_extra(self):
        pass
