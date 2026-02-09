"""
Tests unitaires pour les modèles de l'application shop
"""
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from shop.models import CategorieEtablissement, CategorieProduit, Etablissement, Produit, Favorite


class CategorieEtablissementModelTests(TestCase):
    """Tests unitaires pour le modèle CategorieEtablissement"""

    def test_categorie_etablissement_creation(self):
        """Test la création d'une catégorie d'établissement"""
        categorie = CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie de restaurants"
        )
        self.assertIsNotNone(categorie.id)
        self.assertEqual(categorie.nom, "Restaurant")
        self.assertTrue(categorie.status)

    def test_categorie_etablissement_slug_auto_generation(self):
        """Test la génération automatique du slug"""
        categorie = CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie de restaurants"
        )
        self.assertIsNotNone(categorie.slug)
        self.assertIn("restaurant", categorie.slug.lower())

    def test_categorie_etablissement_str(self):
        """Test la représentation string"""
        categorie = CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie de restaurants"
        )
        self.assertEqual(str(categorie), "Restaurant")


class CategorieProduitModelTests(TestCase):
    """Tests unitaires pour le modèle CategorieProduit"""

    def setUp(self):
        self.categorie_etab = CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie test"
        )

    def test_categorie_produit_creation(self):
        """Test la création d'une catégorie de produit"""
        categorie = CategorieProduit.objects.create(
            nom="Plat",
            description="Plats du jour",
            categorie=self.categorie_etab
        )
        self.assertIsNotNone(categorie.id)
        self.assertEqual(categorie.nom, "Plat")
        self.assertEqual(categorie.categorie, self.categorie_etab)

    def test_categorie_produit_slug_auto_generation(self):
        """Test la génération automatique du slug"""
        categorie = CategorieProduit.objects.create(
            nom="Plat",
            description="Plats du jour",
            categorie=self.categorie_etab
        )
        self.assertIsNotNone(categorie.slug)
        self.assertIn("plat", categorie.slug.lower())

    def test_categorie_produit_str(self):
        """Test la représentation string"""
        categorie = CategorieProduit.objects.create(
            nom="Plat",
            description="Plats du jour",
            categorie=self.categorie_etab
        )
        self.assertEqual(str(categorie), "Plat")


class EtablissementModelTests(TestCase):
    """Tests unitaires pour le modèle Etablissement"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="merchant",
            email="merchant@example.com",
            password="testpass123"
        )
        self.categorie_etab = CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie test"
        )

    def test_etablissement_creation(self):
        """Test la création d'un établissement"""
        etablissement = Etablissement.objects.create(
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
        self.assertIsNotNone(etablissement.id)
        self.assertEqual(etablissement.nom, "Chez Test")
        self.assertEqual(etablissement.user, self.user)

    def test_etablissement_slug_auto_generation(self):
        """Test la génération automatique du slug"""
        etablissement = Etablissement.objects.create(
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
        self.assertIsNotNone(etablissement.slug)

    def test_etablissement_save_updates_user(self):
        """Test que la sauvegarde met à jour les informations de l'utilisateur"""
        etablissement = Etablissement.objects.create(
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
        # Rafraîchir l'utilisateur depuis la base de données
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.email, "test@example.com")

    def test_etablissement_str(self):
        """Test la représentation string"""
        etablissement = Etablissement.objects.create(
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
        self.assertEqual(str(etablissement), "Chez Test")


class ProduitModelTests(TestCase):
    """Tests unitaires pour le modèle Produit"""

    def setUp(self):
        self.user = User.objects.create_user(
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

    def test_produit_creation(self):
        """Test la création d'un produit"""
        produit = Produit.objects.create(
            nom="Burger",
            description="Burger test",
            description_deal="Super deal",
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )
        self.assertIsNotNone(produit.id)
        self.assertEqual(produit.nom, "Burger")
        self.assertEqual(produit.prix, 1000)

    def test_produit_slug_auto_generation(self):
        """Test la génération automatique du slug"""
        produit = Produit.objects.create(
            nom="Burger",
            description="Burger test",
            description_deal="Super deal",
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )
        self.assertIsNotNone(produit.slug)

    def test_produit_save_sets_categorie_etab(self):
        """Test que la sauvegarde définit automatiquement categorie_etab"""
        produit = Produit.objects.create(
            nom="Burger",
            description="Burger test",
            description_deal="Super deal",
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )
        self.assertEqual(produit.categorie_etab, self.etablissement.categorie)

    def test_produit_check_promotion_true_when_valid_dates(self):
        """Test check_promotion retourne True quand les dates sont valides"""
        produit = Produit.objects.create(
            nom="Promo",
            description="Produit en promo",
            description_deal="Deal",
            prix_promotionnel=500,
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
            date_debut_promo=timezone.now().date() - datetime.timedelta(days=1),
            date_fin_promo=timezone.now().date() + datetime.timedelta(days=30),
        )
        self.assertTrue(produit.check_promotion)

    def test_produit_check_promotion_false_when_no_dates(self):
        """Test check_promotion retourne False quand il n'y a pas de dates"""
        produit = Produit.objects.create(
            nom="Sans promo",
            description="Produit sans promo",
            description_deal="Deal",
            prix_promotionnel=0,
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )
        self.assertFalse(produit.check_promotion)

    def test_produit_check_promotion_false_when_start_future(self):
        """Test check_promotion retourne False quand date_debut est dans le futur"""
        produit = Produit.objects.create(
            nom="Promo future",
            description="Produit",
            description_deal="Deal",
            prix_promotionnel=500,
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
            date_debut_promo=timezone.now().date() + datetime.timedelta(days=1),
            date_fin_promo=timezone.now().date() + datetime.timedelta(days=30),
        )
        self.assertFalse(produit.check_promotion)

    def test_produit_check_promotion_false_when_end_past(self):
        """Test check_promotion retourne False quand date_fin est dans le passé"""
        produit = Produit.objects.create(
            nom="Promo expirée",
            description="Produit",
            description_deal="Deal",
            prix_promotionnel=500,
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
            date_debut_promo=timezone.now().date() - datetime.timedelta(days=30),
            date_fin_promo=timezone.now().date() - datetime.timedelta(days=1),
        )
        self.assertFalse(produit.check_promotion)

    def test_produit_str(self):
        """Test la représentation string"""
        produit = Produit.objects.create(
            nom="Burger",
            description="Burger test",
            description_deal="Super deal",
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )
        self.assertEqual(str(produit), "Burger")


class FavoriteModelTests(TestCase):
    """Tests unitaires pour le modèle Favorite"""

    def setUp(self):
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

    def test_favorite_creation(self):
        """Test la création d'un favori"""
        favorite = Favorite.objects.create(
            user=self.user,
            produit=self.produit
        )
        self.assertIsNotNone(favorite.id)
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.produit, self.produit)

    def test_favorite_unique_together(self):
        """Test que l'unique_together fonctionne (un utilisateur ne peut avoir qu'un favori par produit)"""
        Favorite.objects.create(
            user=self.user,
            produit=self.produit
        )
        # Tenter de créer un deuxième favori pour le même utilisateur et produit
        with self.assertRaises(Exception):
            Favorite.objects.create(
                user=self.user,
                produit=self.produit
            )

    def test_favorite_str(self):
        """Test la représentation string"""
        favorite = Favorite.objects.create(
            user=self.user,
            produit=self.produit
        )
        expected = f"{self.user.username} - {self.produit.nom}"
        self.assertEqual(str(favorite), expected)

