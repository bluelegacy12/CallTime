from django.shortcuts import render, get_object_or_404, redirect
from .forms import NameForm, UserForm, AddPerformerForm, AddStaffForm
from .models import Performers, Shows, Roles, CallTime, RehearsalVenues, Uploads, Company, Staff, Category, QuickCall, Conflict
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.http import Http404
from django.core.mail import EmailMessage
from getdata.utils import render_to_pdf
from django.http import HttpResponse
import os
import requests
from django import forms
from datetime import timedelta
import re
from django.db.models import F

baseUrl = "/home/dylanelza/theater/getdata/"
schedulename = 0
logo = "/static/images/CallTimeLogocirclebg.png/"

#used to detect if user is on mobile platform
def mobile(request):
    #Return True if the request comes from a mobile device

    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

class UserFormView(View):
    form_class = UserForm
    template_name = 'register.html'

    #display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    #register user based on input data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # unify the data into commit-ready format (cleaned data or normalized)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['retype_password']
            if (password != password2):
                return render(request, self.template_name, {'form': form})
            user.set_password(password)
            user.save()
            group = Group.objects.get(name='Artist')
            user.groups.add(group)
            performer = Performers()
            performer.username = username
            performer.first_name = form.cleaned_data['first_name']
            performer.last_name = form.cleaned_data['last_name']
            performer.email = form.cleaned_data['email']
            performer.save()

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('getdata:home')
        return render(request, self.template_name, {'form': form})

class UserUpdate(UpdateView):
    model = User
    template_name = 'password_change.html'
    fields = ['password']

    def get_form(self, *args, **kwargs):
        form = super(UserUpdate, self).get_form(*args, **kwargs)
        form.fields['password'].widget = forms.PasswordInput(attrs={'value':''})
        #form.fields['retype_password'].widget = forms.PasswordInput(attrs={'value':''})
        return form

    def post(self, request, **kwargs):
        user = self.request.user

        # unify the data into commit-ready format (cleaned data or normalized)
        password = request.POST.get('password')
        password2 = request.POST.get('retype_password')
        if (password != password2):
            for g in user.groups.all():
                if g.name == 'Company':
                    c = Company.objects.get(username=self.request.user.username)
                    return render(request, 'error.html', {
                        'error':'Passwords do not match! Please try again.',
                        'self':c,
                        'link':f'/getdata/user/{c.id}/',
                        'linkName':'Retry'
                        })
                else:
                    p = Performers.objects.get(username=self.request.user.username)
                    return render(request, 'error.html', {
                        'error':'Passwords do not match! Please try again.',
                        'self':p,
                        'link':f'/getdata/user/{p.id}/',
                        'linkName':'Retry'
                        })
        user.set_password(password)
        user.save()
        for g in user.groups.all():
            if g.name == 'Company':
                return render(request, 'error.html', {'error':'Success! Password changed.', 'self':Company.objects.get(username=self.request.user.username)})
            else:
                return render(request, 'error.html', {'error':'Success! Password changed.'})

    def get_context_data(self, *args, **kwargs):
        context = super(UserUpdate, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                context['self'] = Performers.objects.get(username=self.request.user.username)
                context['string'] = str(context['self'].email)
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
                context['string'] = str(context['self'].email)
        return context

class CompanyFormView(View):
    form_class = NameForm
    template_name = 'company_register.html'

    #display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    #register user based on input data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # unify the data into commit-ready format (cleaned data or normalized)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['retype_password']
            if (password != password2):
                return render(request, self.template_name, {'form': form})
            user.set_password(password)
            user.save()
            group = Group.objects.get(name='Company')
            user.groups.add(group)
            company = Company()
            company.username = username
            company.name = form.cleaned_data['name']
            company.email = form.cleaned_data['email']
            company.save()

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('getdata:home')
        return render(request, self.template_name, {'form': form})

class CompanyUpdate(UpdateView):
    model = Company
    fields = [ 'email']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(CompanyUpdate, self).get_form(*args, **kwargs)
        return form

    def get_context_data(self, **kwargs):
        context = super(CompanyUpdate, self).get_context_data(**kwargs)
        context['viewName'] = "Update Company Details"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class CompanyPerformersUpdate(UpdateView):
    model = Company
    fields = [ 'performers']
    template_name = 'create_form.html'


    def get_form(self, *args, **kwargs):
        form = super(CompanyPerformersUpdate, self).get_form(*args, **kwargs)
        c = Company.objects.get(id=self.object.id)
        form.fields['performers'] = forms.ModelMultipleChoiceField(
                        queryset=c.performers.order_by('last_name'),
                        label="Performers",
                        widget=forms.CheckboxSelectMultiple)
        return form

    def get_context_data(self, **kwargs):
        context = super(CompanyPerformersUpdate, self).get_context_data(**kwargs)
        context['viewName'] = "Unchecked Performers will be removed"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        company = self.object
        context['company'] = company
        context['string'] = str(company.email)
        for c in company.staff_set.all():
            context['string'] += " " + str(c.email)
        return context

    def post(self, request, *args, **kwargs):
        company = Company.objects.get(id=self.kwargs['pk'])
        list = request.POST.getlist('performers')
        p = Performers.objects.filter(id__in=list)
        company.performers.set(p)
        return redirect('getdata:artists', pk=company.id)

class CompanyPerformersDeleteAll(generic.DetailView):
    model = Company
    template_name = 'delete_confirm.html'

    def get_context_data(self, **kwargs):
        context = super(CompanyPerformersDeleteAll, self).get_context_data(**kwargs)
        context['viewName'] = "Delete All Performers"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['object'] = "all artists on file"
        company = context['self']
        context['string'] = str(company.email)
        for c in company.staff_set.all():
            context['string'] += " " + str(c.email)
        return context

    def post(self, request, *args, **kwargs):
        company = Company.objects.get(id=self.request.META['QUERY_STRING'])
        for p in company.performers.all():
            company.performers.remove(p)
        return redirect('getdata:artists', pk=company.id)

def ChangeShowPerformers(self):
    c = Company.objects.get(username=self.request.user.username)
    for show in c.shows_set.all():
        for role in show.roles_set.all():
            if role.performer_id not in c.performers.all():
                role.delete()
    for call in c.calltime_set.all():
        for performer in call.performers.all():
            if performer not in c.performers.all():
                call.performers.remove(performer)
    return

class ShowCreate(CreateView):
    model = Shows
    fields = ['company', 'title', 'rehearsal_start', 'show_open', 'director_id']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(ShowCreate, self).get_form(*args, **kwargs)
        try:
            c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        except:
            c = Company.objects.get(username=self.request.user.username)
        form.fields['director_id'].queryset = c.staff_set.all()
        form.fields['rehearsal_start'].widget = forms.DateInput(attrs={'type':'date'})
        form.fields['show_open'].widget = forms.DateInput(attrs={'type':'date'})
        return form

    def get_context_data(self, **kwargs):
        context = super(ShowCreate, self).get_context_data(**kwargs)
        context['viewName'] = "Create Show"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['link'] = 'getdata:show-add'
        try:
            company = Company.objects.get(id=self.request.META['QUERY_STRING'])
        except:
            company = Company.objects.get(username=self.request.user.username)
        context['string'] = str(company.email)
        context['object'] = company
        for c in company.staff_set.all():
            context['string'] += " " + str(c.email)
        return context

class RoleCreate(CreateView):
    model = Roles
    fields = ['name', 'show_id', 'performer_id', 'category']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(RoleCreate, self).get_form(*args, **kwargs)
        showQuery = Shows.objects.filter(id=self.request.META['QUERY_STRING'])
        show = Shows.objects.get(id=self.request.META['QUERY_STRING'])
        form.fields['show_id'].queryset = showQuery
        form.fields['name'].widget = forms.TextInput(attrs={"placeholder": "Figaro"})
        form.fields['performer_id'].queryset = show.company.performers
        form.fields['category'].queryset = show.company.category_set.all()
        form.fields['category'] = forms.ModelMultipleChoiceField(
                        queryset=show.company.category_set.all().order_by('name'),
                        label="Category",
                        required=False,
                        widget=forms.CheckboxSelectMultiple)
        return form

    def get_context_data(self, **kwargs):
        context = super(RoleCreate, self).get_context_data(**kwargs)
        context['viewName'] = "Create Role"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        # next four lines are security measure to ensure wrong profiles can't alter other profiles' data
        show = Shows.objects.get(id=self.request.META['QUERY_STRING'])
        context['string'] = str(show.company.email)
        for c in show.company.staff_set.all():
            context['string'] += " " + str(c.email)
        return context

class HomeView(generic.ListView):
    model = Shows
    template_name = 'home.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['ctLogo'] = logo
        if mobile(self.request):
            is_mobile = True
        else:
            is_mobile = False

        context['is_mobile'] = is_mobile
        try:
            context['error'] = self.kwargs['error']
        except:
            context['error'] = ""
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                context['self'] = Performers.objects.get(username=self.request.user.username)
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class InfoView(generic.DetailView):
    model = Performers
    template_name = 'info.html'

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                context['performer'] = Performers.objects.get(username=self.request.user.username)
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['performer'] = self.object
                companies = Performers.objects.get(id=self.object.id).company_set.all()
                context['string'] = ""
                for c in companies:
                    context['string'] += str(c.email)
                    for s in c.staff_set.all():
                        context['string'] += " " + str(s.email)
        return context

class ProfileView(generic.ListView):
    template_name = 'profile.html'

    def get_queryset(self):
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                return Performers.objects.get(username=self.request.user.username)
            elif g.name == "Company":
                ChangeShowPerformers(self)
                return Company.objects.get(username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                context['performer'] = Performers.objects.get(username=self.request.user.username)

            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class ShowInfoView(generic.DetailView):
    model = Shows
    template_name = 'showinfo.html'

    def get_context_data(self, **kwargs):
        context = super(ShowInfoView, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
                show = Shows.objects.get(id=self.object.id)
                context['string'] = str(show.company.email)
                for c in show.company.staff_set.all():
                    context['string'] += " " + str(c.email)
        return context

class RoleInfoView(generic.DetailView):
    model = Roles
    template_name = 'roleinfo.html'

    def get_context_data(self, **kwargs):
        context = super(RoleInfoView, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
                show = Shows.objects.get(id=self.object.show_id.id)
                context['string'] = str(show.company.email)
                for c in show.company.staff_set.all():
                    context['string'] += " " + str(c.email)
        return context

class PerformerUpdate(UpdateView):
    model = Performers
    fields = ['email', 'phone']
    template_name = 'update_performer.html'

    def get_context_data(self, **kwargs):
        context = super(PerformerUpdate, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class PerformerDelete(DeleteView):
    model = Performers
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:home')

    def get_context_data(self, **kwargs):
        context = super(PerformerDelete, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class ShowUpdate(UpdateView):
    model = Shows
    fields = ['title', 'rehearsal_start', 'show_open', 'director_id']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(ShowUpdate, self).get_form(*args, **kwargs)
        c = self.object.company
        form.fields['director_id'].queryset = c.staff_set.all()
        form.fields['rehearsal_start'].widget = forms.DateInput(attrs={'type':'date'})
        form.fields['show_open'].widget = forms.DateInput(attrs={'type':'date'})
        return form

    def get_context_data(self, **kwargs):
        context = super(ShowUpdate, self).get_context_data(**kwargs)
        context['viewName'] = "Update Show"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        show = Shows.objects.get(id=self.object.id)
        context['string'] = str(show.company.email)
        for c in show.company.staff_set.all():
            context['string'] += " " + str(c.email)
        return context

class ShowDelete(DeleteView):
    model = Shows
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:home')

    def get_context_data(self, **kwargs):
        context = super(ShowDelete, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
                show = Shows.objects.get(id=self.object.id)
                context['string'] = str(show.company.email)
                for c in show.company.staff_set.all():
                    context['string'] += " " + str(c.email)
        return context

class RoleUpdate(UpdateView):
    model = Roles
    fields = ['name', 'show_id', 'performer_id', 'category']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(RoleUpdate, self).get_form(*args, **kwargs)
        c = Company.objects.get(id=self.object.show_id.company.id)
        form.fields['show_id'].queryset = c.shows_set.all()
        form.fields['performer_id'].queryset = c.performers
        form.fields['category'].queryset = c.category_set.all()
        form.fields['category'] = forms.ModelMultipleChoiceField(
                        queryset=c.category_set.all().order_by('name'),
                        label="Category",
                        required=False,
                        widget=forms.CheckboxSelectMultiple)
        return form

    def get_context_data(self, **kwargs):
        context = super(RoleUpdate, self).get_context_data(**kwargs)
        context['viewName'] = "Update Role"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        role = Roles.objects.get(id=self.object.id)
        context['string'] = str(role.show_id.company.email)
        for c in role.show_id.company.staff_set.all():
            context['string'] += " " + str(c.email)
        return context

class RoleDelete(DeleteView):
    model = Roles
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:home')

    def get_context_data(self, **kwargs):
        context = super(RoleDelete, self).get_context_data(**kwargs)
        context['viewName'] = "Delete Role"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        role = Roles.objects.get(id=self.object.id)
        context['string'] = str(role.show_id.company.email)
        for c in role.show_id.company.staff_set.all():
            context['string'] += " " + str(c.email)
        return context

# CallGet might be pointless? Forgot if I ended up using this or not
class CallGet(generic.DetailView):
    model = CallTime
    template_name = 'create_form.html'

    def get_context_data(self, **kwargs):
        context = super(CallGet, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return redirect('getdata:calladd', object=self.kwargs['pk'])

class CallCreate(CreateView):
    model = CallTime
    template_name = 'create_form.html'
    fields = ['company', 'show_id_id', 'headline', 'venue_id', 'date', 'start_time', 'end_time', 'performers', 'staff', 'notes']

    def get_form(self, *args, **kwargs):
        form = super(CallCreate, self).get_form(*args, **kwargs)
        try:
            c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        except:
            c = Company.objects.get(username=self.request.user.username)
        form.fields['show_id_id'].queryset = Shows.objects.filter(company=c.id)
        form.fields['venue_id'].queryset = RehearsalVenues.objects.filter(company=c.id)
        form.fields['performers'] = forms.ModelMultipleChoiceField(
                        queryset=c.performers.order_by('last_name'),
                        label="Performers",
                        required=False,
                        widget=forms.CheckboxSelectMultiple)
        form.fields['staff'] = forms.ModelMultipleChoiceField(
                        queryset=c.staff_set.all().order_by('last_name'),
                        label="Staff",
                        required=False,
                        widget=forms.CheckboxSelectMultiple)
        form.fields['date'].widget = forms.DateInput(attrs={'type':'date'})
        form.fields['start_time'].widget = forms.TimeInput(attrs={'type':'time','value':'10:00'})
        form.fields['end_time'].widget = forms.TimeInput(attrs={'type':'time','value':'13:00'})
        return form

    def get_context_data(self, **kwargs):
        context = super(CallCreate, self).get_context_data(**kwargs)
        context['viewName'] = 'Create a Call Block'
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['link'] = 'getdata:call-add'
        try:
            c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        except:
            c = Company.objects.get(username=self.request.user.username)
        context['object'] = c
        context['company'] = c
        context['conflicts'] = c.conflict_set.all()
        context['dates'] = ''
        for conflict in c.conflict_set.all():
            if conflict.end_date:
                dates = conflict.end_date - conflict.start_date
                for i in range(dates.days + 1):
                    context['dates'] += str(conflict.start_date + timedelta(days=i)) + ' '
            else:
                context['dates'] += str(conflict.start_date) + ' '
        context['string'] = str(c.email)
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class CallInfoView(generic.DetailView):
    model = CallTime
    template_name = 'callinfo.html'

    def get_context_data(self, **kwargs):
        context = super(CallInfoView, self).get_context_data(**kwargs)
        context['calltimes'] = CallTime.objects.filter(company=self.object.company)
        context['is_mobile'] = mobile(self.request)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
                company = Company.objects.get(id=self.object.company.id)
                context['string'] = str(company.email)
                for c in company.staff_set.all():
                    context['string'] += " " + str(c.email)
        return context

class ViewPDF(View):
        def post(self, request, *args, **kwargs):
            global schedulename

            user = Company.objects.get(id=request.POST.get("company"))
            text = request.POST.get("schedule")
            text = f'<h1 style="text-align: center; font-size: 200%; line-height: 0%"><u>{user.name}</u></h1>' + text
            file = open(baseUrl + "templates/schedules/schedule" + str(schedulename) + ".html", "w")
            file.write(text)
            file.close()
            data = {}
            pdf = render_to_pdf(file.name, data)
            schedulename += 1
            if schedulename >= 10:
                for x in range(schedulename):
                    os.remove(baseUrl + "templates/schedules/schedule" + str(x) + ".html")

                schedulename = 0
                username = "dylanelza"
                api_token = "aff4d5c66d1091bb59d297a1d6fc6815ebd98584"
                domain_name = "dylanelza.pythonanywhere.com"

                response = requests.post(
                    'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain_name}/reload/'.format(
                        username=username, domain_name=domain_name
                    ),
                    headers={'Authorization': 'Token {token}'.format(token=api_token)}
                )
                if response.status_code == 200:
                    print('reloaded OK')
                else:
                    print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))

            return HttpResponse(pdf, content_type='application/pdf')

class CreatePDF(View):
    #Publish PDF button
    def post(self, request, *args, **kwargs):
        global schedulename

        user = Company.objects.get(id=request.POST.get("company"))
        sender = Company.objects.get(username=self.request.user.username)
        text = request.POST.get("schedule")
        current_show = request.POST.get("showtitle")
        current_date = request.POST.get("date")
        message = request.POST.get("message")
        text = f'<h1 style="text-align: center; font-size: 200%; line-height: 0%"><u>{user.name}</u></h1>' + text
        file = open(baseUrl + "templates/schedules/schedule" + str(schedulename) + ".html", "w")
        file.write(text)
        file.close()
        data = {}
        pdf = render_to_pdf(file.name, data)
        schedulename += 1
        list = []
        bcclist = []

        for performer in user.performers.all():
            for role in performer.roles_set.all():
                if role.show_id.title == current_show and performer.email_notifications:
                    list.append(performer.email)

        for staff in user.staff_set.all():
            bcclist.append(staff.email)

        if message is not None:
            mail = EmailMessage(
                f"{current_date} Daily Schedule - {user.name}",
                f"{message}\n\nHere is the schedule for {current_date}. View it online at: dylanelza.pythonanywhere.com/getdata/home",
                user.email,
                list,
                bcclist,
                reply_to=[sender.email],
            )
        else:
            mail = EmailMessage(
                f"{current_date} Daily Schedule - {user.name}",
                f"Here is the schedule for {current_date}. View it online at: dylanelza.pythonanywhere.com/getdata/home",
                user.email,
                list,
                bcclist,
                reply_to=[sender.email],
            )

        mail.attach(f'{current_date} DailySchedule.pdf', bytes(pdf), "application/pdf")

        if schedulename >= 10:
            for x in range(schedulename):
                os.remove(baseUrl + "templates/schedules/schedule" + str(x) + ".html")

            schedulename = 0
            username = "dylanelza"
            api_token = "aff4d5c66d1091bb59d297a1d6fc6815ebd98584"
            domain_name = "dylanelza.pythonanywhere.com"

            response = requests.post(
                'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain_name}/reload/'.format(
                    username=username, domain_name=domain_name
                ),
                headers={'Authorization': 'Token {token}'.format(token=api_token)}
            )
            if response.status_code == 200:
                print('reloaded OK')
            else:
                print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))

        mail.send()
        return HttpResponse(pdf, content_type='application/pdf')

class CallUpdate(UpdateView):
    model = CallTime
    fields = ['show_id_id', 'headline', 'venue_id', 'date', 'start_time', 'end_time', 'performers', 'staff', 'notes']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(CallUpdate, self).get_form(*args, **kwargs)
        c = Company.objects.get(id=self.object.company.id)
        form.fields['show_id_id'].queryset = Shows.objects.filter(company=c.id)
        form.fields['venue_id'].queryset = RehearsalVenues.objects.filter(company=c.id)
        form.fields['performers'] = forms.ModelMultipleChoiceField(
                        queryset=c.performers.order_by('last_name'),
                        label="Performers",
                        required=False,
                        widget=forms.CheckboxSelectMultiple)
        form.fields['staff'] = forms.ModelMultipleChoiceField(
                        queryset=c.staff_set.all().order_by('last_name'),
                        label="Staff",
                        required=False,
                        widget=forms.CheckboxSelectMultiple)
        form.fields['date'].widget = forms.DateInput(attrs={'type':'date'})
        form.fields['start_time'].widget = forms.TimeInput(attrs={'type':'time'})
        form.fields['end_time'].widget = forms.TimeInput(attrs={'type':'time'})
        return form

    def get_context_data(self, **kwargs):
        context = super(CallUpdate, self).get_context_data(**kwargs)
        context['viewName'] = 'Update Schedule'
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        call = self.object
        context['object'] = call.company
        context['company'] = call.company
        context['string'] = str(call.company.email)
        for s in call.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class CallDelete(DeleteView):
    model = CallTime
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:home')

    def get_context_data(self, **kwargs):
        context = super(CallDelete, self).get_context_data(**kwargs)
        context['viewName'] = 'Delete Call Block'
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        call = self.object
        context['string'] = str(call.company.email)
        for s in call.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class VenueView(generic.ListView):
    template_name = 'venues.html'
    model = RehearsalVenues

    def get_context_data(self, **kwargs):
        context = super(VenueView, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class VenueCreate(CreateView):
    model = RehearsalVenues
    fields = ['company', 'name', 'location']
    template_name = 'create_form.html'

    def get_context_data(self, **kwargs):
        context = super(VenueCreate, self).get_context_data(**kwargs)
        context['viewName'] = 'Create Venue'
        context['calltimes'] = CallTime.objects.all()
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['link'] = 'getdata:venue-add'
        context['object'] = Company.objects.get(id=self.request.META['QUERY_STRING'])
        c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        context['object'] = c
        context['string'] = str(c.email)
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class VenueInfoView(generic.DetailView):
    model = RehearsalVenues
    template_name = 'venueinfo.html'

    def get_context_data(self, **kwargs):
        context = super(VenueInfoView, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class VenueUpdate(UpdateView):
    model = RehearsalVenues
    fields = ['name', 'location']
    template_name = 'create_form.html'

    def get_context_data(self, **kwargs):
        context = super(VenueUpdate, self).get_context_data(**kwargs)
        context['viewName'] = "Update Venue"
        context['calltimes'] = CallTime.objects.all()
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        venue = self.object
        context['string'] = str(venue.company.email)
        for s in venue.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class VenueDelete(DeleteView):
    model = RehearsalVenues
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:venues')

    def get_context_data(self, **kwargs):
        context = super(VenueDelete, self).get_context_data(**kwargs)
        context['viewName'] = "Delete Venue"
        context['calltimes'] = CallTime.objects.all()
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        venue = self.object
        context['string'] = str(venue.company.email)
        for s in venue.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class UploadsView(generic.ListView):
    template_name = 'documents.html'
    model = Uploads

    def get_context_data(self, **kwargs):
        context = super(UploadsView, self).get_context_data(**kwargs)
        context['is_mobile'] = mobile(self.request)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class UploadsCreate(CreateView):
    model = Uploads
    fields = ['company', 'name', 'file', 'details']
    template_name = 'create_form.html'

    def get_context_data(self, **kwargs):
        context = super(UploadsCreate, self).get_context_data(**kwargs)
        context['viewName'] = 'Upload a Document'
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['link'] = 'getdata:documents-add'
        c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        context['object'] = c
        context['string'] = str(c.email)
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class UploadsUpdate(UpdateView):
    model = Uploads
    fields = ['name', 'file', 'details']
    template_name = 'create_form.html'

    def get_context_data(self, **kwargs):
        context = super(UploadsUpdate, self).get_context_data(**kwargs)
        context['viewName'] = "Update Document"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        doc = self.object
        context['string'] = str(doc.company.email)
        for s in doc.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class UploadsDelete(DeleteView):
    model = Uploads
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:documents')

    def get_context_data(self, **kwargs):
        context = super(UploadsDelete, self).get_context_data(**kwargs)
        context['viewName'] = "Delete Document"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        doc = self.object
        context['string'] = str(doc.company.email)
        for s in doc.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class AddPerformer(View):
    template_name = 'addperformer.html'
    form_class = AddPerformerForm

    def get_context_data(self, **kwargs):
        context = super(AddPerformer, self).get_context_data( **kwargs)
        context['viewName'] = "Add Performer"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

    #display blank form
    def get(self, request):
        form = self
        return render(request, self.template_name, {'form': form,
                                                    'viewName': "Add Performer",
                                                    'self': Company.objects.get(username=self.request.user.username),
                                                    'staff': Staff.objects.filter(email__iexact=Company.objects.get(username=self.request.user.username).email)})

    #register user based on input data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            # unify the data into commit-ready format (cleaned data or normalized)
            email = form.cleaned_data['email']
            company = Company.objects.get(id=int(form.cleaned_data['company']))
            try:
                performer = Performers.objects.get(email__iexact=email)
            except:
                return render(request, "home.html", {'error':'Could not find Performer Account with email: ' + email,
                                                    'self':Company.objects.get(username=self.request.user.username),
                                                    'staff':Staff.objects.filter(email__iexact=Company.objects.get(username=self.request.user.username).email)})
            company.performers.add(performer)
            company.save()
            return redirect('getdata:artists', pk=company.id)
        return render(request, self.template_name, {'form': form,
                                                    'viewName': "Add Performer",
                                                    'self': Company.objects.get(username=self.request.user.username),
                                                    'staff': Staff.objects.filter(email__iexact=Company.objects.get(username=self.request.user.username).email)})

class AddStaff(View):
    form_class = AddStaffForm
    template_name = 'create_form.html'

    #display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form,
                                                    'self': Company.objects.get(username=self.request.user.username),
                                                    'string': str(Company.objects.get(username=self.request.user.username).email)})

    #register user based on input data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = self.request.user

            # unify the data into commit-ready format (cleaned data or normalized)
            email = form.cleaned_data['email']
            first = form.cleaned_data['first_name']
            last = form.cleaned_data['last_name']
            company = Company.objects.get(username=user.username)
            staff = Staff()
            staff.first_name = first
            staff.last_name = last
            staff.email = email
            staff.company = company
            staff.save()
            return redirect('getdata:staffinfo')
        return render(request, self.template_name, {'form': form,
                                                    'self': Company.objects.get(username=self.request.user.username),
                                                    'string': str(Company.objects.get(username=self.request.user.username).email)})

    def get_context_data(self, **kwargs):
        context = super(AddStaff, self).get_context_data(**kwargs)
        context['viewName'] = "Add Staff"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class StaffView(generic.ListView):
    template_name = 'staff.html'

    def get_queryset(self):
        company = Company.objects.get(username=self.request.user.username)
        return Staff.objects.filter(company=company)

    def get_context_data(self, **kwargs):
        context = super(StaffView, self).get_context_data(**kwargs)
        context['viewName'] = "Staff List"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class StaffUpdate(UpdateView):
    model = Staff
    fields = ['first_name', 'last_name', 'email']
    template_name = 'create_form.html'

    def get_context_data(self, **kwargs):
        context = super(StaffUpdate, self).get_context_data(**kwargs)
        context['viewName'] = "Update Staff"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        staff = self.object
        context['string'] = str(staff.company.email)
        return context

class StaffDelete(DeleteView):
    model = Staff
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:staffinfo')

    def get_context_data(self, **kwargs):
        context = super(StaffDelete, self).get_context_data(**kwargs)
        context['viewName'] = "Delete Staff"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        staff = self.object
        context['string'] = str(staff.company.email)
        return context

class PrivacyChange(generic.ListView):
    template_name = 'profile.html'

    def get_queryset(self):
        return Performers.objects.get(username=self.request.user.username)

    def post(self, request):
        performer = Performers.objects.get(username=request.user.username)
        if performer.public_profile == True:
            performer.public_profile = False
        else:
            performer.public_profile = True
        performer.save()
        return redirect('getdata:profile')

class EmailNoticeChange(generic.ListView):
    template_name = 'profile.html'

    def get_queryset(self):
        return Performers.objects.get(username=self.request.user.username)

    def post(self, request):
        performer = Performers.objects.get(username=request.user.username)
        if performer.email_notifications == True:
            performer.email_notifications = False
        else:
            performer.email_notifications = True
        performer.save()
        return redirect('getdata:profile')

class JoinChange(generic.ListView):
    template_name = 'artists.html'

    def get_queryset(self):
        return Company.objects.get(username=self.request.user.username)

    def post(self, request):
        try:
            c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        except:
            c = Company.objects.get(username=self.request.user.username)
        if c.join == True:
            c.join = False
        else:
            c.join = True
        c.save()
        return redirect('getdata:artists', pk=c.id)

    def get_context_data(self, **kwargs):
        context = super(JoinChange, self).get_context_data(**kwargs)
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['code'] = 'http://dylanelza.pythonanywhere.com' + redirect('getdata:addme').url + "?" + self.request.META['QUERY_STRING']
        try:
            c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        except:
            c = Company.objects.get(username=self.request.user.username)
        context['string'] = str(c.email)
        context['object'] = c
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class SendAlert(generic.ListView):
    template_name = 'profile.html'

    def post(self, request):
        user = Company.objects.get(username=request.user.username)
        list = []
        bcclist = []
        for performer in user.performers.all():
            if performer.email_notifications:
                list.append(performer.email)

        for staff in user.staff_set.all():
            bcclist.append(staff.email)

        mail = EmailMessage(
            f"CallTime Alert from {user.name}",
            request.POST.get('alert'),
            user.email,
            list,
            bcclist,
            reply_to=[user.email],
        )
        mail.send()
        return redirect('getdata:profile')

class ArtistsView(generic.DetailView):
    template_name = 'artists.html'
    model = Company

    def get_context_data(self, **kwargs):
        context = super(ArtistsView, self).get_context_data(**kwargs)
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['code'] = 'https://dylanelza.pythonanywhere.com' + redirect('getdata:addme').url + "?" + str(self.object.id)
        try:
            c = Company.objects.get(id=self.object.id)
        except:
            c = Company.objects.get(username=self.request.user.username)
        context['string'] = ""
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)

        # clean up artist conflicts when artist is removed
        for conflict in c.conflict_set.all():
            if conflict.performer_id not in c.performers.all():
                conflict.delete()
        return context

class AddLink(generic.ListView):
    template_name = 'addme.html'
    model = Company

    def post(self, request, *args, **kwargs):
        user = Performers.objects.get(username=self.request.user.username)
        company = Company.objects.get(id=self.request.META['QUERY_STRING'])
        if company.join == False:
            return render(request, "home.html", {'error':'Unable to join. That company has closed their roster.', 'companies':Performers.objects.get(username=self.request.user.username).company_set.all()})
        if user is not None:
            if user not in company.performers.all():
                company.performers.add(user)
                company.save()
                return redirect('getdata:home')
            return render(request, "home.html", {'error':'You are already in this cast!', 'companies':Performers.objects.get(username=self.request.user.username).company_set.all()})
        return redirect('getdata:home')

    def get_context_data(self, **kwargs):
        context = super(AddLink, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                context['performer'] = Performers.objects.get(username=self.request.user.username)
                context['object'] = Company.objects.get(id=self.request.META['QUERY_STRING'])
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
                context['self'] = Company.objects.get(username=self.request.user.username)
        return context

class CategoryInfo(generic.DetailView):
    model = Category
    template_name = 'categoryinfo.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryInfo, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                context['performer'] = Performers.objects.get(username=self.request.user.username)
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
                context['self'] = Company.objects.get(username=self.request.user.username)
                c = self.object.company
                context['string'] = str(c.email)
                for s in c.staff_set.all():
                    context['string'] += " " + str(s.email)
        return context

class CategoryCreate(CreateView):
    model = Category
    fields = ['company', 'name', 'description']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(CategoryCreate, self).get_form(*args, **kwargs)
        form.fields['name'].widget = forms.TextInput(attrs={"placeholder": "Chorus"})
        return form

    def get_context_data(self, **kwargs):
        context = super(CategoryCreate, self).get_context_data(**kwargs)
        context['viewName'] = 'Create a Category'
        context['subName'] = 'Allows you to select cast members by their category - i.e. Chorus, YA, Principals, etc.'
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['link'] = 'getdata:category-add'
        try:
            c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        except:
            c = Company.objects.get(username=self.request.user.username)
        context['object'] = c
        context['string'] = str(c.email)
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class CategoryUpdate(UpdateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'create_form.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryUpdate, self).get_context_data(**kwargs)
        context['viewName'] = "Update Category"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        doc = self.object
        context['string'] = str(doc.company.email)
        for s in doc.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class CategoryDelete(DeleteView):
    model = Category
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:home')

    def get_context_data(self, **kwargs):
        context = super(CategoryDelete, self).get_context_data(**kwargs)
        context['viewName'] = "Delete Category"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        doc = self.object
        context['string'] = str(doc.company.email)
        for s in doc.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class QuickCreate(CreateView):
    model = QuickCall
    template_name = 'create_form.html'
    fields = ['call','start_time', 'end_time', 'performers', 'details']

    def get_form(self, *args, **kwargs):
        form = super(QuickCreate, self).get_form(*args, **kwargs)
        call = CallTime.objects.get(id=self.request.META['QUERY_STRING'])
        form.fields['performers'].queryset = call.performers
        form.fields['performers'] = forms.ModelMultipleChoiceField(
                        queryset=call.performers.order_by('last_name'),
                        label="Performers",
                        required=False,
                        widget=forms.CheckboxSelectMultiple)
        form.fields['start_time'].widget = forms.TimeInput(attrs={'type':'time','value':call.start_time})
        form.fields['end_time'].widget = forms.TimeInput(attrs={'type':'time'})
        return form

    def get_context_data(self, **kwargs):
        context = super(QuickCreate, self).get_context_data(**kwargs)
        call = CallTime.objects.get(id=self.request.META['QUERY_STRING'])
        context['viewName'] =  f'Create a Call Breakdown for {call.date}: {call.start_time} - {call.end_time}'
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['link'] = 'getdata:call-add'
        c = call.company
        context['object'] = call
        context['company'] = c
        context['string'] = str(c.email)
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class QuickUpdate(UpdateView):
    model = QuickCall
    template_name = 'create_form.html'
    fields = ['start_time', 'end_time', 'performers', 'details']

    def get_form(self, *args, **kwargs):
        form = super(QuickUpdate, self).get_form(*args, **kwargs)
        call = self.object.call
        form.fields['performers'].queryset = call.performers
        form.fields['performers'] = forms.ModelMultipleChoiceField(
                        queryset=call.performers.order_by('last_name'),
                        label="Performers",
                        required=False,
                        widget=forms.CheckboxSelectMultiple)
        form.fields['start_time'].widget = forms.TimeInput(attrs={'type':'time'})
        form.fields['end_time'].widget = forms.TimeInput(attrs={'type':'time'})
        return form

    def get_context_data(self, **kwargs):
        context = super(QuickUpdate, self).get_context_data(**kwargs)
        call = self.object.call
        context['viewName'] = f'Update Call Breakdown for {call.date}: {call.start_time} - {call.end_time}'
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['link'] = 'getdata:call-add'
        c = call.company
        context['object'] = call
        context['company'] = c
        context['string'] = str(c.email)
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class QuickDelete(DeleteView):
    model = QuickCall
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:home')

    def get_context_data(self, **kwargs):
        context = super(QuickDelete, self).get_context_data(**kwargs)
        context['viewName'] = "Delete Category"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        c = self.object.call.company
        context['string'] = str(c.email)
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class LogoUpdate(UpdateView):
    model = Company
    fields = [ 'logo']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(LogoUpdate, self).get_form(*args, **kwargs)
        return form

    def get_context_data(self, **kwargs):
        context = super(LogoUpdate, self).get_context_data(**kwargs)
        context['viewName'] = "Upload a Logo"
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class ConflictCreate(CreateView):
    model = Conflict
    fields = ['company', 'performer_id', 'start_date', 'end_date', 'start_time', 'end_time']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(ConflictCreate, self).get_form(*args, **kwargs)
        try:
            c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        except:
            c = Company.objects.get(username=self.request.user.username)
        form.fields['performer_id'].queryset = c.performers
        form.fields['start_time'].widget = forms.TimeInput(attrs={'type':'time'})
        form.fields['end_time'].widget = forms.TimeInput(attrs={'type':'time'})
        form.fields['start_date'].widget = forms.DateInput(attrs={'type':'date'})
        form.fields['end_date'].widget = forms.DateInput(attrs={'type':'date'})
        return form

    def get_context_data(self, **kwargs):
        context = super(ConflictCreate, self).get_context_data(**kwargs)
        context['viewName'] = 'Add a Conflict/Not Available Date'
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        context['link'] = 'getdata:conflict-add'
        try:
            c = Company.objects.get(id=self.request.META['QUERY_STRING'])
        except:
            c = Company.objects.get(username=self.request.user.username)
        context['object'] = c
        context['string'] = str(c.email)
        for s in c.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class ConflictUpdate(UpdateView):
    model = Conflict
    fields = ['start_date', 'end_date', 'start_time', 'end_time']
    template_name = 'create_form.html'

    def get_form(self, *args, **kwargs):
        form = super(ConflictUpdate, self).get_form(*args, **kwargs)
        form.fields['start_time'].widget = forms.TimeInput(attrs={'type':'time'})
        form.fields['end_time'].widget = forms.TimeInput(attrs={'type':'time'})
        form.fields['start_date'].widget = forms.DateInput(attrs={'type':'date'})
        form.fields['end_date'].widget = forms.DateInput(attrs={'type':'date'})
        return form

    def get_context_data(self, **kwargs):
        context = super(ConflictUpdate, self).get_context_data(**kwargs)
        context['viewName'] = 'Update a Conflict/Not Available for ' + str(self.object.performer_id)
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        c = self.object
        context['string'] = str(c.company.email)
        for s in c.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class ConflictDelete(DeleteView):
    model = Conflict
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('getdata:home')

    def get_context_data(self, **kwargs):
        context = super(ConflictDelete, self).get_context_data(**kwargs)
        context['viewName'] = 'Delete a Conflict/Not Available'
        context['self'] = Company.objects.get(username=self.request.user.username)
        context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        c = self.object
        context['string'] = str(c.company.email)
        for s in c.company.staff_set.all():
            context['string'] += " " + str(s.email)
        return context

class ConflictInfo(generic.DetailView):
    model = Conflict
    template_name = 'conflictinfo.html'

    def get_context_data(self, **kwargs):
        context = super(ConflictInfo, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                context['performer'] = Performers.objects.get(username=self.request.user.username)
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
                context['self'] = Company.objects.get(username=self.request.user.username)
                c = self.object.company
                context['string'] = str(c.email)
                for s in c.staff_set.all():
                    context['string'] += " " + str(s.email)
        return context

class ConflictView(generic.ListView):
    template_name = 'conflicts.html'
    model = Conflict

    def get_context_data(self, **kwargs):
        context = super(ConflictView, self).get_context_data(**kwargs)
        for g in self.request.user.groups.all():
            if g.name == "Artist":
                try:
                    context['companies'] = Performers.objects.get(username=self.request.user.username).company_set.all()
                except:
                    context['companies'] = ""
            elif g.name == "Company":
                context['self'] = Company.objects.get(username=self.request.user.username)
                context['staff'] = Staff.objects.filter(email__iexact=context['self'].email)
        return context

class Feedback(View):
    def post(self, request, *args, **kwargs):
        try:
            user = Company.objects.get(username=self.request.user.username)
        except:
            user = Performers.objects.get(username=self.request.user.username)
        subject = request.POST.get("subject")
        message = request.POST.get("feedbackMessage")

        #if message is not None:
        mail = EmailMessage(
            f"Feedback: {subject}",
            f"From: {user.username} - {user} - {user.email} \n\nMessage:\n{message}",
            'calltimescheduler@gmail.com',
            ['dylan.elza@gmail.com'],
            [],
            reply_to=[user.email],
        )

        mail.send()
        return HttpResponse("Success! You can close this window")