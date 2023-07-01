from django.db import models
import datetime
from django.urls import reverse
from django import forms
from gdstorage.storage import GoogleDriveStorage

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()

# Create your models here.
class Performers(models.Model):
    username = models.CharField(max_length=128, unique=True, null=False)
    first_name = models.CharField(max_length=128, null=False)
    last_name = models.CharField(max_length=128, null=False)
    email = models.CharField(max_length=128, unique=True, null=False)
    phone = models.CharField(max_length=128, unique=True, null=True, blank=True)
    email_notifications = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('getdata:profile')

    def __str__(self):
        return self.first_name[0].upper() + ". " + self.last_name

class Company(models.Model):
    username = models.CharField(max_length=128, unique=True, null=False)
    name = models.CharField(max_length=128, unique=True, null=False)
    email = models.CharField(max_length=128, unique=True, null=False)
    performers = models.ManyToManyField(Performers, blank=True, null=True)
    logo = models.FileField(null=True, blank=True, upload_to='calltime-uploads', storage=gd_storage)
    join = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('getdata:profile')

class Staff(models.Model):
    first_name = models.CharField(max_length=128, null=False)
    last_name = models.CharField(max_length=128, null=False)
    email = models.CharField(max_length=128, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def get_absolute_url(self):
            return reverse('getdata:staffinfo')

    def __str__(self):
        return self.first_name[0].upper() + ". " + self.last_name

class Shows(models.Model):
    title = models.CharField(max_length=128, null=False)
    rehearsal_start = models.DateField(null=True, blank=True)
    show_open = models.DateField(null=False)
    director_id = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    def get_absolute_url(self):
            return reverse('getdata:showinfo', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=128, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
            return reverse('getdata:profile')

    def __str__(self):
        return self.name.replace(" ", "")

class Roles(models.Model):
    name = models.CharField(max_length=128, null=False)
    show_id = models.ForeignKey(Shows, on_delete=models.CASCADE)
    performer_id = models.ForeignKey(Performers, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ManyToManyField(Category, blank=True, null=True)

    def get_absolute_url(self):
            return reverse('getdata:roleinfo', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name + " - from: " + self.show_id.title + " - performer: " + str(self.performer_id)


class RehearsalVenues(models.Model):
    name = models.CharField(max_length=128, null=False)
    location = models.CharField(max_length=128, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    def get_absolute_url(self):
            return reverse('getdata:venueinfo', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

class CallTime(models.Model):
    show_id_id = models.ForeignKey(Shows, on_delete=models.CASCADE)
    venue_id = models.ForeignKey(RehearsalVenues, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=True, blank=True)
    performers = models.ManyToManyField(Performers, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    staff = models.ManyToManyField(Staff, null=True, blank=True)
    headline = models.CharField(max_length=128, null=True, blank=True)

    def get_absolute_url(self):
            return reverse('getdata:callinfo', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.date) + ": " + str(self.start_time)  + " - " + str(self.end_time)

class QuickCall(models.Model):
    call = models.ForeignKey(CallTime, on_delete=models.CASCADE)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=True, blank=True)
    performers = models.ManyToManyField(Performers, null=True, blank=True)
    details = models.CharField(max_length=128, null=True, blank=True)

    def get_absolute_url(self):
            return reverse('getdata:callinfo', kwargs={'pk': self.call.pk})

    def __str__(self):
        return str(self.start_time)  + " - " + str(self.end_time)

class Uploads(models.Model):
    name = models.CharField(max_length=128)
    details = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='calltime-uploads', storage=gd_storage)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def get_absolute_url(self):
            return reverse('getdata:documents')

    def __str__(self):
        return self.name

class Conflict(models.Model):
    performer_id = models.ForeignKey(Performers, on_delete=models.CASCADE)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('getdata:conflictinfo', kwargs={'pk': self.pk})

    def __str__(self):
        return self.performer_id.last_name + "'s Conflict on " + str(self.start_date)