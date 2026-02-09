from django.test import TestCase
from django.contrib.auth.models import User

from .models import Customer, Commande


class CustomerModelTests(TestCase):

    def test_customer_str_returns_username(self):
        user = User.objects.create_user(username="alice", password="pwd12345")
        customer = Customer.objects.create(
            user=user,
            adresse="Abidjan",
            contact_1="0101010101",
        )

        self.assertEqual(str(customer), "alice")


class CommandeModelTests(TestCase):

    def test_check_paiement_always_true(self):
        user = User.objects.create_user(username="bob", password="pwd12345")
        customer = Customer.objects.create(
            user=user,
            adresse="Yopougon",
            contact_1="0202020202",
        )

        commande = Commande.objects.create(
            customer=customer,
            prix_total=1000,
        )

        self.assertTrue(commande.check_paiement)
