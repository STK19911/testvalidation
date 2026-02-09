"""
Tests d'intégration pour l'application shop
Ces tests vérifient les flux complets d'utilisation
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from customer.models import Customer, Commande, ProduitPanier
from shop.models import Produit, CategorieProduit, CategorieEtablissement, Etablissement, Favorite


class CompleteMerchantFlowTests(TestCase):
    """Tests d'intégration pour le flux complet d'un marchand"""

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
        # Créer un client et une commande pour tester le dashboard
        self.user_client = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123"
        )
        self.customer = Customer.objects.create(
            user=self.user_client,
            adresse="123 Test Street",
            contact_1="0101010101",
        )
        self.produit = Produit.objects.create(
            nom="Burger",
            description="Burger test",
            description_deal="Super deal",
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )

    def test_dashboard_shows_correct_statistics(self):
        """Test que le dashboard affiche les bonnes statistiques"""
        self.client.login(username="merchant", password="testpass123")
        
        # Créer une commande
        commande = Commande.objects.create(
            customer=self.customer,
            prix_total=1000,
            transaction_id="TXN123"
        )
        ProduitPanier.objects.create(
            produit=self.produit,
            commande=commande,
            quantite=1
        )
        
        # Accéder au dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les statistiques
        self.assertEqual(response.context['total_articles'], 1)
        self.assertEqual(response.context['total_commandes'], 1)
        self.assertIn('commandes_aujourdhui', response.context)


class CompleteFavoriteFlowTests(TestCase):
    """Tests d'intégration pour le flux complet de gestion des favoris"""

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

    def test_complete_favorite_flow(self):
        """Test le flux complet d'ajout et suppression de favoris"""
        self.client.login(username="testuser", password="testpass123")
        
        # 1. Accéder à la page du produit (pas de favori)
        response = self.client.get(reverse('product_detail', args=[self.produit.slug]))
        self.assertFalse(response.context['is_favorited'])
        
        # 2. Ajouter aux favoris
        response = self.client.get(reverse('toggle_favorite', args=[self.produit.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Favorite.objects.filter(user=self.user, produit=self.produit).exists())
        
        # 3. Accéder à nouveau à la page du produit (devrait être favori)
        response = self.client.get(reverse('product_detail', args=[self.produit.slug]))
        self.assertTrue(response.context['is_favorited'])
        
        # 4. Retirer des favoris
        response = self.client.get(reverse('toggle_favorite', args=[self.produit.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Favorite.objects.filter(user=self.user, produit=self.produit).exists())
        
        # 5. Accéder à nouveau à la page du produit (pas de favori)
        response = self.client.get(reverse('product_detail', args=[self.produit.slug]))
        self.assertFalse(response.context['is_favorited'])

