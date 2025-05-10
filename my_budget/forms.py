from django import forms
from .models import Income, Expense, IncomeCategory, ExpenseCategory

class IncomeForm(forms.ModelForm):
    """
    Форма для добавления/редактирования доходов.
    Настройки:
    - Привязка к модели Income
    - Отображаемые поля: категория и сумма
    - Кастомизация виджетов:
      * Поле amount: числовой ввод с шагом 0.01 (для денежных значений)
      * Поле category: выпадающий список с стилем form-select
    """
    class Meta:
        model = Income
        fields = ['category', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.01',  # Разрешаем значения с копейками
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={  # Стиль
                'class': 'form-select'  # Стилизованный выпадающий список
            })
        }

class ExpenseForm(forms.ModelForm):
    """
    Форма для добавления/редактирования расходов.
    Аналогична IncomeForm, но работает с моделью Expense.
    """
    class Meta:
        model = Expense
        fields = ['category', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            })
        }

class IncomeCategoryForm(forms.ModelForm):
    """
    Форма для управления категориями доходов.
    Особенности:
    - Только поле name
    - Плейсхолдер с подсказкой
    - Стиль form-control для текстового ввода
    """
    class Meta:
        model = IncomeCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название категории'  # Пример для пользователя
            })
        }

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название категории'  # Пример для пользователя
            })
        }