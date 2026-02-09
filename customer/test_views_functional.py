"""
Tests fonctionnels pour les vues de l'application customer
"""
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.urls import reverse
from django.core import mail
from django.utils import timezone
from datetime import timedelta

from customer.models import Customer, Panier, ProduitPanier, CodePromotionnel, PasswordResetToken
from shop.models import Produit, CategorieProduit, CategorieEtablissement, Etablissement


class LoginViewTests(TestCase):
    """Tests fonctionnels pour la vue de connexion"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_login_page_get(self):
        """Test l'accès à la page de connexion"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_if_authenticated(self):
        """Test que l'utilisateur authentifié est redirigé"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_login_post_success(self):
        """Test la connexion réussie"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(
            reverse('post'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

    def test_login_post_with_email(self):
        """Test la connexion avec email"""
        data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(
            reverse('post'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

    def test_login_post_failure_wrong_password(self):
        """Test la connexion échouée avec mauvais mot de passe"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(
            reverse('post'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_login_post_failure_wrong_username(self):
        """Test la connexion échouée avec mauvais nom d'utilisateur"""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }
        response = self.client.post(
            reverse('post'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])


class SignupViewTests(TestCase):
    """Tests fonctionnels pour la vue d'inscription"""

    def setUp(self):
        self.client = Client()

    def test_signup_page_get(self):
        """Test l'accès à la page d'inscription"""
        response = self.client.get(reverse('guests_signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_redirects_if_authenticated(self):
        """Test que l'utilisateur authentifié est redirigé"""
        user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('guests_signup'))
        self.assertEqual(response.status_code, 302)  # Redirect


class InscriptionViewTests(TestCase):
    """Tests fonctionnels pour la vue d'inscription POST"""

    def setUp(self):
        self.client = Client()

    def test_inscription_success(self):
        """Test l'inscription réussie"""
        data = {
            'nom': 'Doe',
            'prenoms': 'John',
            'username': 'johndoe',
            'email': 'john@example.com',
            'phone': '0101010101',
            'adresse': '123 Test Street',
            'password': 'testpass123',
            'passwordconf': 'testpass123'
        }
        response = self.client.post(
            reverse('inscription'),
            data=data
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Vérifier que l'utilisateur a été créé
        self.assertTrue(User.objects.filter(username='johndoe').exists())
        self.assertTrue(Customer.objects.filter(user__username='johndoe').exists())

    def test_inscription_failure_password_mismatch(self):
        """Test l'inscription échouée avec mots de passe non correspondants"""
        data = {
            'nom': 'Doe',
            'prenoms': 'John',
            'username': 'johndoe',
            'email': 'john@example.com',
            'phone': '0101010101',
            'adresse': '123 Test Street',
            'password': 'testpass123',
            'passwordconf': 'differentpass'
        }
        response = self.client.post(
            reverse('inscription'),
            data=data
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_inscription_failure_invalid_email(self):
        """Test l'inscription échouée avec email invalide"""
        data = {
            'nom': 'Doe',
            'prenoms': 'John',
            'username': 'johndoe',
            'email': 'invalid-email',
            'phone': '0101010101',
            'adresse': '123 Test Street',
            'password': 'testpass123',
            'passwordconf': 'testpass123'
        }
        response = self.client.post(
            reverse('inscription'),
            data=data
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_inscription_failure_duplicate_username(self):
        """Test l'inscription échouée avec username existant"""
        User.objects.create_user(
            username="johndoe",
            email="existing@example.com",
            password="testpass123"
        )
        data = {
            'nom': 'Doe',
            'prenoms': 'John',
            'username': 'johndoe',
            'email': 'john@example.com',
            'phone': '0101010101',
            'adresse': '123 Test Street',
            'password': 'testpass123',
            'passwordconf': 'testpass123'
        }
        response = self.client.post(
            reverse('inscription'),
            data=data
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])


class CartViewTests(TestCase):
    """Tests fonctionnels pour les vues de panier"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            adresse="123 Test Street",
            contact_1="0101010101",
        )
        self.session = Session.objects.create(
            session_key="test_session_key",
            session_data="",
            expire_date=timezone.now() + timedelta(days=1)
        )
        self.panier = Panier.objects.create(
            customer=self.customer,
            session_id=self.session
        )
        # Créer les dépendances pour les produits
        self.user_merchant = User.objects.create_user(
            username="merchant",
            email="merchant@example.com",
            password="testpass123"
        )
        self.categorie_etab = CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie test"
        )
        self.categorie_produit = CategorieProduit.objects.create(
            nom="Plat",
            description="Plat du jour",
            categorie=self.categorie_etab
        )
        self.etablissement = Etablissement.objects.create(
            user=self.user_merchant,
            nom="Chez Test",
            description="Etablissement de test",
            logo="logo.png",
            couverture="cover.png",
            categorie=self.categorie_etab,
            nom_du_responsable="Doe",
            prenoms_duresponsable="John",
            adresse="Abidjan",
            pays="CI",
            contact_1="0101010101",
            email="test@example.com",
        )
        self.produit = Produit.objects.create(
            nom="Burger",
            description="Burger test",
            description_deal="Super deal",
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )

    def test_add_to_cart_success(self):
        """Test l'ajout d'un produit au panier"""
        self.client.login(username="testuser", password="testpass123")
        data = {
            'panier': self.panier.id,
            'produit': self.produit.id,
            'quantite': 2
        }
        response = self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Vérifier que le produit a été ajouté
        self.assertTrue(ProduitPanier.objects.filter(
            panier=self.panier,
            produit=self.produit
        ).exists())

    def test_add_to_cart_updates_quantity(self):
        """Test que l'ajout du même produit met à jour la quantité"""
        self.client.login(username="testuser", password="testpass123")
        # Ajouter le produit une première fois
        ProduitPanier.objects.create(
            panier=self.panier,
            produit=self.produit,
            quantite=1
        )
        data = {
            'panier': self.panier.id,
            'produit': self.produit.id,
            'quantite': 3
        }
        response = self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Vérifier que la quantité a été mise à jour
        produit_panier = ProduitPanier.objects.get(
            panier=self.panier,
            produit=self.produit
        )
        self.assertEqual(produit_panier.quantite, 3)

    def test_delete_from_cart_success(self):
        """Test la suppression d'un produit du panier"""
        self.client.login(username="testuser", password="testpass123")
        produit_panier = ProduitPanier.objects.create(
            panier=self.panier,
            produit=self.produit,
            quantite=1
        )
        data = {
            'panier': self.panier.id,
            'produit_panier': produit_panier.id
        }
        response = self.client.post(
            reverse('delete_from_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Vérifier que le produit a été supprimé
        self.assertFalse(ProduitPanier.objects.filter(id=produit_panier.id).exists())

    def test_update_cart_success(self):
        """Test la mise à jour de la quantité d'un produit dans le panier"""
        self.client.login(username="testuser", password="testpass123")
        ProduitPanier.objects.create(
            panier=self.panier,
            produit=self.produit,
            quantite=1
        )
        data = {
            'panier': self.panier.id,
            'produit': self.produit.id,
            'quantite': 5
        }
        response = self.client.post(
            reverse('update_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Vérifier que la quantité a été mise à jour
        produit_panier = ProduitPanier.objects.get(
            panier=self.panier,
            produit=self.produit
        )
        self.assertEqual(produit_panier.quantite, 5)

    def test_add_coupon_success(self):
        """Test l'ajout d'un code promotionnel"""
        self.client.login(username="testuser", password="testpass123")
        code = CodePromotionnel.objects.create(
            libelle="Promo Test",
            etat=True,
            date_fin=timezone.now().date() + timedelta(days=30),
            reduction=0.1,
            code_promo="PROMO10"
        )
        data = {
            'panier': self.panier.id,
            'coupon': 'PROMO10'
        }
        response = self.client.post(
            reverse('add_coupon'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Vérifier que le coupon a été ajouté
        self.panier.refresh_from_db()
        self.assertEqual(self.panier.coupon, code)

    def test_add_coupon_invalid(self):
        """Test l'ajout d'un code promotionnel invalide"""
        self.client.login(username="testuser", password="testpass123")
        data = {
            'panier': self.panier.id,
            'coupon': 'INVALID_CODE'
        }
        response = self.client.post(
            reverse('add_coupon'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])


class PasswordResetViewTests(TestCase):
    """Tests fonctionnels pour les vues de réinitialisation de mot de passe"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpassword"
        )

    def test_request_reset_password_page_get(self):
        """Test l'accès à la page de demande de réinitialisation"""
        response = self.client.get(reverse('request_reset_password'))
        self.assertEqual(response.status_code, 200)

    def test_request_reset_password_post_success(self):
        """Test la demande de réinitialisation réussie"""
        data = {
            'email': 'test@example.com'
        }
        response = self.client.post(
            reverse('request_reset_password'),
            data=data
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        # Vérifier qu'un token a été créé
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())
        # Vérifier qu'un email a été envoyé
        self.assertEqual(len(mail.outbox), 1)

    def test_request_reset_password_post_invalid_email(self):
        """Test la demande de réinitialisation avec email invalide"""
        data = {
            'email': 'invalid-email'
        }
        response = self.client.post(
            reverse('request_reset_password'),
            data=data
        )
        self.assertEqual(response.status_code, 302)  # Redirect avec message d'erreur

    def test_reset_password_get(self):
        """Test l'accès à la page de réinitialisation avec token valide"""
        token_obj = PasswordResetToken.objects.create(
            user=self.user,
            token="valid_token_12345"
        )
        response = self.client.get(
            reverse('reset_password', args=['valid_token_12345'])
        )
        self.assertEqual(response.status_code, 200)

    def test_reset_password_post_success(self):
        """Test la réinitialisation réussie du mot de passe"""
        token_obj = PasswordResetToken.objects.create(
            user=self.user,
            token="valid_token_12345"
        )
        data = {
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(
            reverse('reset_password', args=['valid_token_12345']),
            data=data
        )
        self.assertEqual(response.status_code, 302)  # Redirect vers login
        # Vérifier que le mot de passe a été changé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        # Vérifier que le token a été supprimé
        self.assertFalse(PasswordResetToken.objects.filter(token="valid_token_12345").exists())

    def test_reset_password_post_password_mismatch(self):
        """Test la réinitialisation échouée avec mots de passe non correspondants"""
        token_obj = PasswordResetToken.objects.create(
            user=self.user,
            token="valid_token_12345"
        )
        data = {
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        }
        response = self.client.post(
            reverse('reset_password', args=['valid_token_12345']),
            data=data
        )
        self.assertEqual(response.status_code, 302)  # Redirect avec message d'erreur


class DeconnexionViewTests(TestCase):
    """Tests fonctionnels pour la vue de déconnexion"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_deconnexion(self):
        """Test la déconnexion"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('deconnexion'))
        self.assertEqual(response.status_code, 302)  # Redirect
        # Vérifier que l'utilisateur est déconnecté
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

