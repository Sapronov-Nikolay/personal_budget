from django.urls import path
from . import views

app_name = 'my_budget'

urlpatterns = [
  path('', views.base_views, name='home'),
  path('income/', views.income_list, name='income'),
  path('expense/', views.expense_list, name='expense'),
  path('summary/', views.summary_list, name='summary'),


  # AJAX-endpoints
  path('income/create/', views.create_income, name='create_income'),
  path('income-category/create/', views.create_income_category, name='create_income_category'),
  path('income/delete/<int:pk>/', views.delete_income, name='delete_income'),
  path('income-category/delete/<int:pk>/', views.delete_income_category, name='delete_income_category'),
  path('expense/create/', views.create_expense, name='create_expense'),
  path('expense-category/create/', views.create_expense_category, name='create_expense_category'),
  path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
  path('expense-category/delete/<int:pk>/', views.delete_expense_category, name='delete_expense_category'),
]