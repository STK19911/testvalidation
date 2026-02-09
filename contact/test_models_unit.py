"""
Tests unitaires pour les modèles de l'application contact
"""
from django.test import TestCase
from contact.models import Contact, NewsLetter


class ContactModelTests(TestCase):
    """Tests unitaires pour le modèle Contact"""

    def test_contact_creation(self):
        """Test la création d'un contact"""
        contact = Contact.objects.create(
            nom="John Doe",
            sujet="Question",
            email="john@example.com",
            message="Ceci est un message de test"
        )
        self.assertIsNotNone(contact.id)
        self.assertEqual(contact.nom, "John Doe")
        self.assertEqual(contact.email, "john@example.com")
        self.assertTrue(contact.status)

    def test_contact_date_fields(self):
        """Test que les champs de date sont automatiquement remplis"""
        contact = Contact.objects.create(
            nom="John Doe",
            sujet="Question",
            email="john@example.com",
            message="Message test"
        )
        self.assertIsNotNone(contact.date_add)
        self.assertIsNotNone(contact.date_update)

    def test_contact_str(self):
        """Test la représentation string"""
        contact = Contact.objects.create(
            nom="John Doe",
            sujet="Question",
            email="john@example.com",
            message="Message test"
        )
        self.assertEqual(str(contact), "John Doe")


class NewsLetterModelTests(TestCase):
    """Tests unitaires pour le modèle NewsLetter"""

    def test_newsletter_creation(self):
        """Test la création d'un abonnement newsletter"""
        newsletter = NewsLetter.objects.create(
            email="user@example.com"
        )
        self.assertIsNotNone(newsletter.id)
        self.assertEqual(newsletter.email, "user@example.com")
        self.assertTrue(newsletter.status)

    def test_newsletter_date_fields(self):
        """Test que les champs de date sont automatiquement remplis"""
        newsletter = NewsLetter.objects.create(
            email="user@example.com"
        )
        self.assertIsNotNone(newsletter.date_add)
        self.assertIsNotNone(newsletter.date_update)

    def test_newsletter_str(self):
        """Test la représentation string"""
        newsletter = NewsLetter.objects.create(
            email="user@example.com"
        )
        self.assertEqual(str(newsletter), "user@example.com")

