from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date

from .models import CategorieEtablissement, CategorieProduit, Etablissement, Produit


class ProduitModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="merchant", password="pwd12345")
        self.categorie_etab = CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie test",
        )
        self.categorie_produit = CategorieProduit.objects.create(
            nom="Plat",
            description="Plat du jour",
            categorie=self.categorie_etab,
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

    def test_produit_str_returns_name(self):
        produit = Produit.objects.create(
            nom="Burger",
            description="Burger test",
            description_deal="Super deal",
            prix_promotionnel=500,
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )

        self.assertEqual(str(produit), "Burger")

    def test_check_promotion_true_when_dates_valid(self):
        produit = Produit.objects.create(
            nom="Promo",
            description="Produit en promo",
            description_deal="Deal",
            prix_promotionnel=500,
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
            date_debut_promo=date(2000, 1, 1),
            date_fin_promo=date(2999, 1, 1),
        )

        self.assertTrue(produit.check_promotion)

    def test_check_promotion_false_when_no_dates(self):
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
