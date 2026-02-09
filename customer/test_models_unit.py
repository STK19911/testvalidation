"""
Tests unitaires pour les modèles de l'application customer
"""
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta

from customer.models import Customer, PasswordResetToken, CodePromotionnel, Panier, Commande, ProduitPanier
from shop.models import Produit, CategorieProduit, CategorieEtablissement, Etablissement


class CustomerModelTests(TestCase):
    """Tests unitaires pour le modèle Customer"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_customer_str_returns_username(self):
        """Test que __str__ retourne le nom d'utilisateur"""
        customer = Customer.objects.create(
            user=self.user,
            adresse="123 Test Street",
            contact_1="0101010101",
        )
        self.assertEqual(str(customer), "testuser")

    def test_customer_creation(self):
        """Test la création d'un client"""
        customer = Customer.objects.create(
            user=self.user,
            adresse="123 Test Street",
            contact_1="0101010101",
            contact_2="0202020202",
            pays="Côte d'Ivoire",
        )
        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.user, self.user)
        self.assertTrue(customer.status)

    def test_customer_date_fields(self):
        """Test que les champs de date sont automatiquement remplis"""
        customer = Customer.objects.create(
            user=self.user,
            adresse="123 Test Street",
            contact_1="0101010101",
        )
        self.assertIsNotNone(customer.date_add)
        self.assertIsNotNone(customer.date_update)


class PasswordResetTokenModelTests(TestCase):
    """Tests unitaires pour le modèle PasswordResetToken"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_password_reset_token_creation(self):
        """Test la création d'un token de réinitialisation"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token="test_token_12345"
        )
        self.assertIsNotNone(token.id)
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.token, "test_token_12345")

    def test_password_reset_token_is_valid(self):
        """Test que le token est valide dans la période de validité"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token="test_token_12345"
        )
        # Le token vient d'être créé, il doit être valide
        self.assertTrue(token.is_valid())

    def test_password_reset_token_expires(self):
        """Test que le token expire après 1 heure"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token="test_token_12345"
        )
        # Simuler un token créé il y a 2 heures
        token.created_at = timezone.now() - timedelta(hours=2)
        token.save()
        self.assertFalse(token.is_valid())

    def test_password_reset_token_str(self):
        """Test la représentation string du token"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token="test_token_12345"
        )
        self.assertEqual(str(token), f"Token for {self.user.username}")


class CodePromotionnelModelTests(TestCase):
    """Tests unitaires pour le modèle CodePromotionnel"""

    def setUp(self):
        # Créer les dépendances nécessaires
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
        self.produit = Produit.objects.create(
            nom="Burger",
            description="Burger test",
            description_deal="Super deal",
            prix=1000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )

    def test_code_promotionnel_creation(self):
        """Test la création d'un code promotionnel"""
        code = CodePromotionnel.objects.create(
            libelle="Promo Test",
            etat=True,
            date_fin=timezone.now().date() + timedelta(days=30),
            reduction=0.1,
            code_promo="PROMO10",
            nombre_u=100
        )
        self.assertIsNotNone(code.id)
        self.assertEqual(code.libelle, "Promo Test")
        self.assertEqual(code.reduction, 0.1)

    def test_code_promotionnel_str(self):
        """Test la représentation string du code promotionnel"""
        code = CodePromotionnel.objects.create(
            libelle="Promo Test",
            etat=True,
            date_fin=timezone.now().date() + timedelta(days=30),
            reduction=0.1,
            code_promo="PROMO10"
        )
        self.assertEqual(str(code), "Promo Test")

    def test_code_promotionnel_with_products(self):
        """Test l'ajout de produits à un code promotionnel"""
        code = CodePromotionnel.objects.create(
            libelle="Promo Test",
            etat=True,
            date_fin=timezone.now().date() + timedelta(days=30),
            reduction=0.1,
            code_promo="PROMO10"
        )
        code.forfait.add(self.produit)
        self.assertIn(self.produit, code.forfait.all())


class PanierModelTests(TestCase):
    """Tests unitaires pour le modèle Panier"""

    def setUp(self):
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
        self.produit2 = Produit.objects.create(
            nom="Pizza",
            description="Pizza test",
            description_deal="Deal pizza",
            prix=2000,
            categorie=self.categorie_produit,
            etablissement=self.etablissement,
        )

    def test_panier_creation_with_customer(self):
        """Test la création d'un panier avec un client"""
        panier = Panier.objects.create(
            customer=self.customer,
            session_id=self.session
        )
        self.assertIsNotNone(panier.id)
        self.assertEqual(panier.customer, self.customer)

    def test_panier_creation_with_session_only(self):
        """Test la création d'un panier avec seulement une session"""
        panier = Panier.objects.create(
            session_id=self.session
        )
        self.assertIsNotNone(panier.id)
        self.assertIsNone(panier.customer)

    def test_panier_total_empty(self):
        """Test le total d'un panier vide"""
        panier = Panier.objects.create(
            customer=self.customer,
            session_id=self.session
        )
        self.assertEqual(panier.total, 0)

    def test_panier_total_with_products(self):
        """Test le total d'un panier avec des produits"""
        panier = Panier.objects.create(
            customer=self.customer,
            session_id=self.session
        )
        ProduitPanier.objects.create(
            produit=self.produit,
            panier=panier,
            quantite=2
        )
        ProduitPanier.objects.create(
            produit=self.produit2,
            panier=panier,
            quantite=1
        )
        # Total attendu: (1000 * 2) + (2000 * 1) = 4000
        self.assertEqual(panier.total, 4000)

    def test_panier_total_with_coupon(self):
        """Test le total d'un panier avec un code promotionnel"""
        panier = Panier.objects.create(
            customer=self.customer,
            session_id=self.session
        )
        ProduitPanier.objects.create(
            produit=self.produit,
            panier=panier,
            quantite=2
        )
        # Total sans coupon: 2000
        code = CodePromotionnel.objects.create(
            libelle="Promo 50%",
            etat=True,
            date_fin=timezone.now().date() + timedelta(days=30),
            reduction=0.5,  # 50% de réduction
            code_promo="PROMO50"
        )
        panier.coupon = code
        panier.save()
        # Total avec coupon: 2000 - (0.5 * 2000) = 1000
        self.assertEqual(panier.total_with_coupon, 1000)

    def test_panier_check_empty(self):
        """Test la vérification si un panier est vide"""
        panier = Panier.objects.create(
            customer=self.customer,
            session_id=self.session
        )
        self.assertFalse(panier.check_empty)
        
        ProduitPanier.objects.create(
            produit=self.produit,
            panier=panier,
            quantite=1
        )
        self.assertTrue(panier.check_empty)

    def test_panier_str(self):
        """Test la représentation string du panier"""
        panier = Panier.objects.create(
            customer=self.customer,
            session_id=self.session
        )
        self.assertEqual(str(panier), "panier")


class CommandeModelTests(TestCase):
    """Tests unitaires pour le modèle Commande"""

    def setUp(self):
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

    def test_commande_creation(self):
        """Test la création d'une commande"""
        commande = Commande.objects.create(
            customer=self.customer,
            prix_total=5000.0,
            transaction_id="TXN123456",
            id_paiment="PAY123456"
        )
        self.assertIsNotNone(commande.id)
        self.assertEqual(commande.customer, self.customer)
        self.assertEqual(commande.prix_total, 5000.0)
        self.assertTrue(commande.status)

    def test_commande_check_paiement(self):
        """Test la vérification du paiement (toujours True actuellement)"""
        commande = Commande.objects.create(
            customer=self.customer,
            prix_total=5000.0
        )
        self.assertTrue(commande.check_paiement)

    def test_commande_str(self):
        """Test la représentation string de la commande"""
        commande = Commande.objects.create(
            customer=self.customer,
            prix_total=5000.0
        )
        self.assertEqual(str(commande), "commande")


class ProduitPanierModelTests(TestCase):
    """Tests unitaires pour le modèle ProduitPanier"""

    def setUp(self):
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

    def test_produit_panier_creation(self):
        """Test la création d'un produit dans un panier"""
        produit_panier = ProduitPanier.objects.create(
            produit=self.produit,
            panier=self.panier,
            quantite=3
        )
        self.assertIsNotNone(produit_panier.id)
        self.assertEqual(produit_panier.quantite, 3)
        self.assertEqual(produit_panier.produit, self.produit)

    def test_produit_panier_total_without_promotion(self):
        """Test le calcul du total sans promotion"""
        produit_panier = ProduitPanier.objects.create(
            produit=self.produit,
            panier=self.panier,
            quantite=3
        )
        # Total attendu: 1000 * 3 = 3000
        self.assertEqual(produit_panier.total, 3000)

    def test_produit_panier_total_with_promotion(self):
        """Test le calcul du total avec promotion"""
        # Ajouter une promotion au produit
        self.produit.prix_promotionnel = 700
        self.produit.date_debut_promo = timezone.now().date() - timedelta(days=1)
        self.produit.date_fin_promo = timezone.now().date() + timedelta(days=30)
        self.produit.save()
        
        produit_panier = ProduitPanier.objects.create(
            produit=self.produit,
            panier=self.panier,
            quantite=2
        )
        # Total attendu avec promotion: 700 * 2 = 1400
        self.assertEqual(produit_panier.total, 1400)

