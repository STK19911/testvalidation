"""
Tests d'intégration pour l'application customer
Ces tests vérifient les flux complets d'utilisation
"""
import json
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.urls import reverse
from django.utils import timezone

from customer.models import Customer, Panier, ProduitPanier, CodePromotionnel, Commande
from shop.models import Produit, CategorieProduit, CategorieEtablissement, Etablissement


class CompletePurchaseFlowTests(TestCase):
    """Tests d'intégration pour le flux complet d'achat"""

    def setUp(self):
        self.client = Client()
        # Créer un utilisateur client
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
        # Créer un établissement et des produits
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
        self.produit1 = Produit.objects.create(
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

    def test_complete_purchase_flow_without_coupon(self):
        """Test le flux complet d'achat sans code promotionnel"""
        # 1. Se connecter
        self.client.login(username="testuser", password="testpass123")
        
        # 2. Créer un panier (via session)
        session = Session.objects.create(
            session_key="test_session_key",
            session_data="",
            expire_date=timezone.now() + timedelta(days=1)
        )
        panier = Panier.objects.create(
            customer=self.customer,
            session_id=session
        )
        
        # 3. Ajouter des produits au panier
        data = {
            'panier': panier.id,
            'produit': self.produit1.id,
            'quantite': 2
        }
        response = self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        
        data = {
            'panier': panier.id,
            'produit': self.produit2.id,
            'quantite': 1
        }
        response = self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Vérifier le total du panier
        panier.refresh_from_db()
        expected_total = (1000 * 2) + (2000 * 1)  # 4000
        self.assertEqual(panier.total, expected_total)
        
        # 5. Créer une commande (paiement)
        data = {
            'transaction_id': 'TXN123456',
            'notify_url': 'http://example.com/notify',
            'return_url': 'http://example.com/return',
            'panier': panier.id
        }
        response = self.client.post(
            reverse('paiement_detail'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 6. Vérifier que la commande a été créée
        commande = Commande.objects.get(customer=self.customer)
        self.assertEqual(commande.prix_total, expected_total)
        self.assertEqual(commande.transaction_id, 'TXN123456')
        
        # 7. Vérifier que les produits ont été transférés à la commande
        produits_commande = ProduitPanier.objects.filter(commande=commande)
        self.assertEqual(produits_commande.count(), 2)
        
        # 8. Vérifier que le panier a été supprimé
        self.assertFalse(Panier.objects.filter(id=panier.id).exists())

    def test_complete_purchase_flow_with_coupon(self):
        """Test le flux complet d'achat avec code promotionnel"""
        # 1. Se connecter
        self.client.login(username="testuser", password="testpass123")
        
        # 2. Créer un panier
        session = Session.objects.create(
            session_key="test_session_key",
            session_data="",
            expire_date=timezone.now() + timedelta(days=1)
        )
        panier = Panier.objects.create(
            customer=self.customer,
            session_id=session
        )
        
        # 3. Ajouter un produit au panier
        data = {
            'panier': panier.id,
            'produit': self.produit1.id,
            'quantite': 2
        }
        self.client.post(
            reverse('add_to_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # 4. Créer et appliquer un code promotionnel
        code = CodePromotionnel.objects.create(
            libelle="Promo 20%",
            etat=True,
            date_fin=timezone.now().date() + timedelta(days=30),
            reduction=0.2,  # 20% de réduction
            code_promo="PROMO20"
        )
        
        data = {
            'panier': panier.id,
            'coupon': 'PROMO20'
        }
        response = self.client.post(
            reverse('add_coupon'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        
        # 5. Vérifier le total avec coupon
        panier.refresh_from_db()
        total_sans_coupon = 1000 * 2  # 2000
        reduction = 0.2 * total_sans_coupon  # 400
        total_avec_coupon = total_sans_coupon - reduction  # 1600
        self.assertEqual(panier.total_with_coupon, int(total_avec_coupon))
        
        # 6. Créer une commande
        data = {
            'transaction_id': 'TXN789',
            'notify_url': 'http://example.com/notify',
            'return_url': 'http://example.com/return',
            'panier': panier.id
        }
        response = self.client.post(
            reverse('paiement_detail'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 7. Vérifier que la commande a le bon prix total avec coupon
        commande = Commande.objects.get(customer=self.customer)
        self.assertEqual(commande.prix_total, int(total_avec_coupon))


class CompleteUserRegistrationFlowTests(TestCase):
    """Tests d'intégration pour le flux complet d'inscription"""

    def setUp(self):
        self.client = Client()

    def test_complete_registration_and_login_flow(self):
        """Test le flux complet d'inscription puis connexion"""
        # 1. S'inscrire
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
        
        # 2. Vérifier que l'utilisateur et le client ont été créés
        user = User.objects.get(username='johndoe')
        self.assertTrue(user.is_authenticated)  # L'utilisateur devrait être connecté automatiquement
        self.assertTrue(Customer.objects.filter(user=user).exists())
        
        # 3. Se déconnecter
        response = self.client.get(reverse('deconnexion'))
        self.assertEqual(response.status_code, 302)
        
        # 4. Se reconnecter
        data = {
            'username': 'john@example.com',  # Avec email
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


class CompleteCartManagementFlowTests(TestCase):
    """Tests d'intégration pour le flux complet de gestion du panier"""

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
        session = Session.objects.create(
            session_key="test_session_key",
            session_data="",
            expire_date=timezone.now() + timedelta(days=1)
        )
        self.panier = Panier.objects.create(
            customer=self.customer,
            session_id=session
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

    def test_complete_cart_management_flow(self):
        """Test le flux complet de gestion du panier (ajout, modification, suppression)"""
        self.client.login(username="testuser", password="testpass123")
        
        # 1. Ajouter un produit
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
        self.assertTrue(json.loads(response.content)['success'])
        
        # 2. Vérifier que le produit est dans le panier
        self.assertTrue(ProduitPanier.objects.filter(
            panier=self.panier,
            produit=self.produit
        ).exists())
        
        # 3. Modifier la quantité
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
        self.assertTrue(json.loads(response.content)['success'])
        
        produit_panier = ProduitPanier.objects.get(
            panier=self.panier,
            produit=self.produit
        )
        self.assertEqual(produit_panier.quantite, 5)
        
        # 4. Supprimer le produit
        data = {
            'panier': self.panier.id,
            'produit_panier': produit_panier.id
        }
        response = self.client.post(
            reverse('delete_from_cart'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertTrue(json.loads(response.content)['success'])
        
        # 5. Vérifier que le panier est vide
        self.assertFalse(ProduitPanier.objects.filter(
            panier=self.panier,
            produit=self.produit
        ).exists())
        self.assertFalse(self.panier.check_empty)

