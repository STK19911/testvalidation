"""
Tests fonctionnels pour les vues de l'application shop
"""
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta

from customer.models import Customer, Panier, Commande, ProduitPanier
from shop.models import Produit, CategorieProduit, CategorieEtablissement, Etablissement, Favorite


class ShopViewTests(TestCase):
    """Tests fonctionnels pour la vue shop"""

    def setUp(self):
        self.client = Client()
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
            status=True
        )

    def test_shop_page_get(self):
        """Test l'accès à la page shop"""
        response = self.client.get(reverse('shop'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.produit, response.context['produits'])

    def test_shop_only_shows_active_products(self):
        """Test que seulement les produits actifs sont affichés"""
        produit_inactive = Produit.objects.create(
            nom="Inactive Product",
            description="Test",
            description_deal="Deal",
            prix=500,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
            status=False
        )
        response = self.client.get(reverse('shop'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.produit, response.context['produits'])
        self.assertNotIn(produit_inactive, response.context['produits'])


class ProductDetailViewTests(TestCase):
    """Tests fonctionnels pour la vue product_detail"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
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
        self.related_produit = Produit.objects.create(
            nom="Pizza",
            description="Pizza test",
            description_deal="Deal pizza",
            prix=2000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )

    def test_product_detail_page_get(self):
        """Test l'accès à la page de détail d'un produit"""
        response = self.client.get(reverse('product_detail', args=[self.produit.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['produit'], self.produit)

    def test_product_detail_shows_related_products(self):
        """Test que les produits similaires sont affichés"""
        response = self.client.get(reverse('product_detail', args=[self.produit.slug]))
        self.assertEqual(response.status_code, 200)
        related_products = response.context['produits']
        self.assertIn(self.related_produit, related_products)

    def test_product_detail_404_for_invalid_slug(self):
        """Test que 404 est retourné pour un slug invalide"""
        response = self.client.get(reverse('product_detail', args=['invalid-slug']))
        self.assertEqual(response.status_code, 404)

    def test_product_detail_shows_favorite_status_for_authenticated_user(self):
        """Test que le statut favori est affiché pour un utilisateur authentifié"""
        self.client.login(username="testuser", password="testpass123")
        Favorite.objects.create(user=self.user, produit=self.produit)
        response = self.client.get(reverse('product_detail', args=[self.produit.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_favorited'])

    def test_product_detail_shows_not_favorite_for_unauthenticated_user(self):
        """Test que is_favorited est False pour un utilisateur non authentifié"""
        response = self.client.get(reverse('product_detail', args=[self.produit.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_favorited'])


class ToggleFavoriteViewTests(TestCase):
    """Tests fonctionnels pour la vue toggle_favorite"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
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

    def test_toggle_favorite_adds_favorite(self):
        """Test l'ajout d'un favori"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('toggle_favorite', args=[self.produit.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Favorite.objects.filter(user=self.user, produit=self.produit).exists())

    def test_toggle_favorite_removes_favorite(self):
        """Test la suppression d'un favori"""
        self.client.login(username="testuser", password="testpass123")
        Favorite.objects.create(user=self.user, produit=self.produit)
        response = self.client.get(reverse('toggle_favorite', args=[self.produit.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(Favorite.objects.filter(user=self.user, produit=self.produit).exists())

    def test_toggle_favorite_requires_login(self):
        """Test que la connexion est requise pour ajouter un favori"""
        response = self.client.get(reverse('toggle_favorite', args=[self.produit.id]))
        self.assertEqual(response.status_code, 302)  # Redirect vers login


class CheckoutViewTests(TestCase):
    """Tests fonctionnels pour la vue checkout"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_checkout_requires_login(self):
        """Test que la connexion est requise pour le checkout"""
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)  # Redirect vers login

    def test_checkout_page_get(self):
        """Test l'accès à la page checkout pour un utilisateur authentifié"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)


class CartViewTests(TestCase):
    """Tests fonctionnels pour la vue cart"""

    def setUp(self):
        self.client = Client()

    def test_cart_page_get(self):
        """Test l'accès à la page panier"""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)


class DashboardViewTests(TestCase):
    """Tests fonctionnels pour la vue dashboard"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="merchant",
            email="merchant@example.com",
            password="testpass123"
        )
        self.categorie_etab = CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie test"
        )
        self.etablissement = Etablissement.objects.create(
            user=self.user,
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

    def test_dashboard_requires_login(self):
        """Test que la connexion est requise pour le dashboard"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect vers login

    def test_dashboard_page_get(self):
        """Test l'accès à la page dashboard"""
        self.client.login(username="merchant", password="testpass123")
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['etablissement'], self.etablissement)
        self.assertIn('total_articles', response.context)
        self.assertIn('total_commandes', response.context)


class PostPaiementDetailsViewTests(TestCase):
    """Tests fonctionnels pour la vue post_paiement_details"""

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
        self.produit_panier = ProduitPanier.objects.create(
            produit=self.produit,
            panier=self.panier,
            quantite=2
        )

    def test_post_paiement_details_success(self):
        """Test la création d'une commande depuis un panier"""
        self.client.login(username="testuser", password="testpass123")
        data = {
            'transaction_id': 'TXN123456',
            'notify_url': 'http://example.com/notify',
            'return_url': 'http://example.com/return',
            'panier': self.panier.id
        }
        response = self.client.post(
            reverse('paiement_detail'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Vérifier qu'une commande a été créée
        self.assertTrue(Commande.objects.filter(customer=self.customer).exists())
        # Vérifier que le panier a été supprimé
        self.assertFalse(Panier.objects.filter(id=self.panier.id).exists())

