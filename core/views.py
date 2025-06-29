import json
import datetime
import pdfkit
import os
from django.views import View
from .models import Machine
from django.shortcuts import render, redirect
from .models import Quotation, Machine, Logo
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator

User = get_user_model()

def abs_url(request, rel_url):
    return request.build_absolute_uri(rel_url)

class LoginPage(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("quotation")
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("quotation")  # Replace 'home' with your home URL name
        return render(request, self.template_name, {"form": form})


class SignUpPage(View):
    template_name = "signup.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("quotation")
        return render(request, self.template_name, {"form": UserRegistrationForm()})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect("login")
        return render(request, self.template_name, {"form": form})


class HomePage(LoginRequiredMixin, View):
    def get(self, request):
        machines = Machine.objects.all()
        context = {
            'machines': machines
        }
        return render(request, 'home.html', context=context)


class QuotationPage(LoginRequiredMixin, View):
    def get(self, request):
        machines = Machine.objects.all()
        context = {
            'machines': machines
        }
        return render(request, 'create-quotation.html', context=context)


def generate_pdf(request, quotation_id, quotation,  machines):

    html = render_to_string("quotation_pdf.html", {
        "quotation": quotation,
        "machines": machines,
        "subject": "PVC Pipe Bending Machine"
    })

    # Path to wkhtmltopdf binary (optional if already in PATH)
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

    pdf = pdfkit.from_string(html, False, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="quotation_{quotation_id}.pdf"'
    return response

@login_required
def create_quotation(request):
    if request.method == "POST":
        client_name = request.POST.get('client_name')
        client_address = request.POST.get('client_address')
        contact_num = request.POST.get('contact_num')
        client_gst = request.POST.get('client_gst')
        client_company = request.POST.get('client_company')
        total_amount = request.POST.get('total_amount')
        products_json = request.POST.get('products_data')
        terms_json = request.POST.get('terms_data')
        terms = json.loads(terms_json)
        user = User.objects.get(id=request.user.id)
        
        # Create Quotation
        quotation = Quotation.objects.create(
            created_by=user,
            client_name=client_name,
            client_address=client_address,
            client_phone=contact_num,
            client_gst=client_gst,
            client_company=client_company,
            total_amount=int(float(total_amount)),
        )

        # Parse machine data from JSON and create or match Machine entries
        machines_data = json.loads(products_json)

        for m in machines_data:
            machine = Machine.objects.get(id=m['id'])
            quotation.products.add(machine)
            if m.get("image"):
                m["image"] = abs_url(request, m["image"])
    
        quotation.save()

        logo = Logo.objects.get(id=1)
        logo_img_url =request.build_absolute_uri(logo.img.url)
        html = render_to_string("quotation_pdf.html", {
            "quotation": quotation,
            "machines": machines_data,
            "terms": terms,
            "user": user,
            'logo_url':logo_img_url,
            "date": datetime.datetime.now().strftime("%d/%m/%Y"),
            "subject": "PVC Pipe Bending Machine"
        })

        # Path to wkhtmltopdf binary (optional if already in PATH)
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

        pdf = pdfkit.from_string(html, False, configuration=config)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="quotation_{quotation.id}.pdf"'
        return response

    machines = Machine.objects.all()
    return render(request, 'create-quotation.html', {'machines': machines})


@method_decorator(login_required, name='dispatch')
class QuotationHistoryView(View):
    def get(self, request):
        quotations = Quotation.objects.filter(created_by=request.user).order_by('-created_at')
        return render(request, 'quotation_history.html', {'quotations': quotations})


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('login')