from django.urls import path
from core.views import HomePage, generate_pdf, create_quotation, LoginPage, SignUpPage, QuotationPage, LogoutView, QuotationHistoryView

urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),
    path('signup/', SignUpPage.as_view(), name='signup'),
    path('', HomePage.as_view(), name='dashboard'),
    path('quotation/', QuotationPage.as_view(), name='quotation'),
    path('quotation/<int:quotation_id>/pdf/', generate_pdf, name='generate_pdf'),
    path('quotation/create/', create_quotation, name='create_quotation'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('quotation-history/', QuotationHistoryView.as_view(), name='quotation_history'),
]
