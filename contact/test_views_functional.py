"""
Tests fonctionnels pour les vues de l'application contact
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from contact.models import Contact, NewsLetter


class ContactViewTests(TestCase):
    """Tests fonctionnels pour la vue contact"""

    def setUp(self):
        self.client = Client()

    def test_contact_page_get(self):
        """Test l'accès à la page de contact"""
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_post_contact_success(self):
        """Test l'envoi d'un message de contact réussi"""
        data = {
            'nom': 'John Doe',
            'email': 'john@example.com',
            'sujet': 'Question',
            'messages': 'Ceci est un message de test'
        }
        response = self.client.post(
            reverse('post_contact'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Vérifier que le contact a été créé
        self.assertTrue(Contact.objects.filter(email='john@example.com').exists())

    def test_post_contact_invalid_email(self):
        """Test l'envoi d'un message avec email invalide"""
        data = {
            'nom': 'John Doe',
            'email': 'invalid-email',
            'sujet': 'Question',
            'messages': 'Message test'
        }
        response = self.client.post(
            reverse('post_contact'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_post_contact_missing_fields(self):
        """Test l'envoi d'un message avec des champs manquants"""
        data = {
            'nom': 'John Doe',
            'email': 'john@example.com',
            # 'sujet' manquant
            'messages': 'Message test'
        }
        response = self.client.post(
            reverse('post_contact'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])


class NewsletterViewTests(TestCase):
    """Tests fonctionnels pour la vue newsletter"""

    def setUp(self):
        self.client = Client()

    def test_post_newsletter_success(self):
        """Test l'abonnement à la newsletter réussi"""
        data = {
            'email': 'user@example.com'
        }
        response = self.client.post(
            reverse('post_newsletter'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Vérifier que l'abonnement a été créé
        self.assertTrue(NewsLetter.objects.filter(email='user@example.com').exists())

    def test_post_newsletter_invalid_email(self):
        """Test l'abonnement avec email invalide"""
        data = {
            'email': 'invalid-email'
        }
        response = self.client.post(
            reverse('post_newsletter'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

