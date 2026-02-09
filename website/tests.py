from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class IndexViewTests(TestCase):

   def test_index_page_status_code(self):
       response = self.client.get(reverse('index'))
       self.assertEqual(response.status_code, 200)

   def test_index_uses_correct_template(self):
       response = self.client.get(reverse('index'))
       self.assertTemplateUsed(response, 'index.html')


class AboutViewTests(TestCase):

   def test_about_page_status_code(self):
       response = self.client.get(reverse('about'))
       self.assertEqual(response.status_code, 200)

   def test_about_uses_correct_template(self):
       response = self.client.get(reverse('about'))
       self.assertTemplateUsed(response, 'about-us.html')
