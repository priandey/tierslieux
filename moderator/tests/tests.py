from django.test import TestCase

from django.contrib.auth.models import User
from location.models import VolunteeringRequest, VolunteerBase, Location

class TestModeratorView(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(username="mod@mod.mod", password="password")
        self.basic_user = User.objects.create_user(username="basic@basic.basic", password="password")
        self.volunteer = User.objects.create_user(username="vol@vol.vol", password="password")
        self.pending_vol = User.objects.create_user(username="pvol@pvol.pvol", password="password")
        self.requested_vol = User.objects.create_user(username="reqvol@reqvol.reqvol", password="password")

        # Creating location
        self.location = Location.objects.create(
                name="La baleine verte",
                description="Une baleine ni bleue, ni rouge",
                moderator=self.moderator,
                slug="baleine")

        # Creating 3 differents volunteer's request
        self.validated_vol_request = VolunteeringRequest.objects.create(  # Validated volunteer
                sender=self.moderator,
                receiver=self.volunteer,
                validated=True
        )
        self.pending_vol_request = VolunteeringRequest.objects.create(  # Pending volunteer
                sender=self.moderator,
                receiver=self.pending_vol,
                validated=False
        )
        self.requested_vol_request = VolunteeringRequest.objects.create(  # Requested volunteer
                sender=self.moderator,
                receiver=self.requested_vol,
                validated=None
        )

        # Creating 3 differents entry for volunteers
        self.validated_vol_base = VolunteerBase.objects.create(
                volunteer=self.volunteer,
                location=self.location,
                is_active=True,
                volunteering_request=self.validated_vol_request
        )
        self.pending_vol_base = VolunteerBase.objects.create(
                volunteer=self.pending_vol,
                location=self.location,
                is_active=False,
                volunteering_request=self.pending_vol_request
        )
        self.requested_vol_base = VolunteerBase.objects.create(
                volunteer=self.requested_vol,
                location=self.location,
                is_active=False,
                volunteering_request=self.requested_vol_request
        )

    def test_volunteers_legal_get(self):
        self.client.login(username="mod@mod.mod", password="password")
        response = self.client.get("/mod/baleine/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'moderator/volunteers.html')
        self.assertTrue(response.context["validated"])
        self.assertTrue(response.context["required_by_mod"])
        self.assertTrue(response.context["required_by_vol"])

    def test_volunteers_illegal_get(self):
        self.client.login(username='basic@basic.basic', password='password')
        response = self.client.get('/mod/baleine/')
        self.assertEqual(response.status_code, 403)

    def test_change_vol_status_legal_validate(self):
        self.client.login(username="mod@mod.mod", password="password")
        response = self.client.get('/mod/baleine/{}/validated'.format(self.pending_vol_request.pk))
        self.assertRedirects(response, '/mod/baleine/')

    def test_change_vol_status_legal_remove(self):
        self.client.login(username="mod@mod.mod", password="password")
        response = self.client.get('/mod/baleine/{}/remove'.format(self.validated_vol_request.pk))
        self.assertRedirects(response, '/mod/baleine/')

    def test_change_vol_status_illegal(self):
        self.client.login(username='basic@basic.basic', password='password')
        response = self.client.get('/mod/baleine/{}/validated'.format(self.validated_vol_request.pk))
        self.assertEqual(response.status_code, 403)

    def test_request_volunteer_illegal(self):
        self.client.login(username='basic@basic.basic', password='password')
        response = self.client.get('/mod/baleine/new_vol/')
        self.assertEqual(response.status_code, 403)

    def test_request_volunteer_legal_exist(self):
        """ The volunteer's username exist in database"""
        self.client.login(username="mod@mod.mod", password='password')
        post_data = {
            'username': 'basic@basic.basic'
        }
        response = self.client.post('/mod/baleine/new_vol/', data=post_data)
        self.assertRedirects(response, '/mod/baleine/')

    def test_request_volunteer_legal_doesNotExist(self):
        """ The volunteer's username isn't found in db """
        self.client.login(username="mod@mod.mod", password='password')
        post_data = {
            'username': 'new@new.new'
        }
        response = self.client.post('/mod/baleine/new_vol/', data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('/moderator/new_user.html')
        self.assertEqual(response.context['username'], post_data['username'])

    def test_mod_create_vol_legal_post(self):
        """ Moderator's view for creating new users """
        self.client.login(username="mod@mod.mod", password='password')
        post_data = {
            'mail': 'new@new.new',
            'password': 'password'
        }
        response = self.client.post('/mod/baleine/create_vol', post_data)
        self.assertRedirects(response, '/mod/baleine/')

    def test_mod_create_vol_illegal_post(self):
        """ Moderator's view for creating new users """
        self.client.login(username="basic@basic.basic", password='password')
        post_data = {
            'mail': 'new@new.new',
            'password': 'password'
        }
        response = self.client.post('/mod/baleine/create_vol', post_data)
        self.assertEqual(response.status_code, 403)
