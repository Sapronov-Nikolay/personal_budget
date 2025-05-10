import json
from datetime import datetime
from calendar import monthrange
from django.db.models import Sum
from django.http import JsonResponse
from .forms import IncomeForm, ExpenseForm, IncomeCategoryForm, ExpenseCategoryForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Income, IncomeCategory, Expense, ExpenseCategory, Summary
from .utils import get_income_category_message, get_expense_category_message

def base_views(request):
  # Основные параметры текущего периода
  current_month = datetime.now().month
  current_year = datetime.now().year

  # Создание или получение текущей сводки (защита от отсутствия данных)
  current_summary, created = Summary.objects.get_or_create(
    month=current_month,
    year=current_year,
    defaults={ # Значения для новой записи
      'income': 0,
      'expense': 0,
      'balance': 0
    }
  )

  # История за последние 12 месяцев
  history = Summary.objects.order_by('-year', '-month')[:12]  # Сортировка по убыванию

  # Подготовка данных для графика (временной ряд)
  chart_data = Summary.objects.order_by('year', 'month')[:12]  # Сортировка по возрастанию

  # Формирование структур для Chart.js
  chart_labels = [f"{item.month:02d}/{item.year}" for item in chart_data]  # Формат "ММ/ГГГГ"
  income_data = [float(item.income) for item in chart_data]
  expense_data = [float(item.expense) for item in chart_data]

  # Сбор контекста с JSON-данными для графика
  context={
    'current_summary': current_summary,
    'history': history,
    'chart_labels': json.dumps(chart_labels),  # Сериализация для JS
    'income_data': json.dumps(income_data),
    'expense_data': json.dumps(expense_data),
  }
  return render(request, 'my_budget/base.html', context)





# Представление доходов
def income_list(request):
  # Парсинг параметров фильтрации из GET-запроса
  selected_month = request.GET.get('month', datetime.now().month)
  selected_year = request.GET.get('year', datetime.now().year)

  # Параметры сортировки таблицы категорий
  sort = request.GET.get('sort', 'name')   # Поле сортировки
  order = request.GET.get('order', 'asc')  # Направление (asc/desc)

  try:
    # Валидация и преобразование входных данных
    current_month = int(selected_month)
    current_year = int(selected_year)

    # Проверяем корректность месяца
    if not (1 <= current_month <= 12):
      raise ValueError("Некорректный месяц")

  except (ValueError, TypeError):
    # Фолбек на текущую дату при ошибках
    now = datetime.now()
    current_month = now.month
    current_year = now.year

  # Фильтрация доходов по периоду с сортировкой
  incomes = Income.objects.filter(
    date__month=current_month,  # Используем current_month вместо month
    date__year=current_year
  ).order_by('-date', '-id')  # Сначала новые записи

  # Сортировка категорий доходов по выбранному полю
  categories = IncomeCategory.objects.all()
  if sort == 'name':
    categories = categories.order_by('name' if order == 'asc' else '-name')
  elif sort == 'date':
    categories = categories.order_by('created_at' if order == 'asc' else '-created_at')

  # Формирование контекста с учетом всех параметров
  context = {
    'incomes': incomes,
    'total_income': Income.objects.aggregate(total=Sum('amount'))['total'] or 0,  # Общий итог
    'categories': categories,  # Используем отсортированные категории
    'category_message': get_income_category_message(IncomeCategory.objects.count()),
    #'categories': IncomeCategory.objects.all(),
    'current_month': current_month,  # Исправлено: current_month вместо cyrrent_month
    'current_year': current_year,
    'months_range': range(1, 13),  # Для селектора месяцев
    'form': IncomeForm(),  # Пустая форма для AJAX
    'sort': sort,  # Добавляем в контекст для шаблона
    'order': order  # Добавляем в контекст для шаблона
  }
  return render(request, 'my_budget/income.html', context)





# Представление расходов
def expense_list(request):
  # Аналогичная income_list логика с адаптацией для расходов
  selected_month = request.GET.get('month', datetime.now().month)
  selected_year = request.GET.get('year', datetime.now().year)
  
  # Параметры сортировки
  sort = request.GET.get('sort', 'name')
  order = request.GET.get('order', 'asc')

  try:
    # Преобразуем и проверяем месяц/год
    current_month = int(selected_month)
    current_year = int(selected_year)
    
    # Проверка диапазона месяца
    if not (1 <= current_month <= 12):
      raise ValueError("Некорректный месяц")

  except (ValueError, TypeError):
    # Устанавливаем текущие значения по умолчанию
    now = datetime.now()
    current_month = now.month
    current_year = now.year

  # Фильтрация расходов с сортировкой
  expenses = Expense.objects.filter(
    date__month=current_month,
    date__year=current_year
  ).order_by('-date', '-id')

  # Сортировка категорий расходов
  categories = ExpenseCategory.objects.all()
  if sort == 'name':
    if order == 'asc':
      categories = categories.order_by('name' if order == 'asc' else '-name')
    else:
      categories = categories.order_by('-name')
  elif sort == 'date':
    if order =='asc':
      categories = categories.order_by('created_at')
    else:
      categories = categories.order_by('-created_at')


  # Расчет временного диапазона месяца
  try:
    num_days = monthrange(current_year, current_month)[1]  # Количество дней в месяце
  except (ValueError, IndexError):
    num_days = 30  # Фолбек Запасной вариант

  start_date = datetime(current_year, current_month, 1).date()
  end_date = datetime(current_year, current_month, num_days).date()

  # Агрегация расходов по категориям
  monthly_expenses = (
    Expense.objects
    .filter(date__range=(start_date, end_date))
    .values('category__name')  # Группировка по категориям
    .annotate(total_amount=Sum('amount'))  # Суммирование
  )

  # Обработка POST-запроса (классическая форма)
  if request.method == 'POST':
    form = ExpenseForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('my_budget:expense')
  else:
    form = ExpenseForm()

  context = {
    'monthly_expenses': monthly_expenses,
    'expenses': expenses,
    'categories': categories,  # Используем отсортированные категории
    #'categories': ExpenseCategory.objects.all(),
    'category_message': get_expense_category_message(ExpenseCategory.objects.count()),
    'num_days': num_days,
    'current_month': current_month,  # Единообразное именование
    'current_year': current_year,
    'months_range': range(1, 13),
    'form': form,
    'sort': sort,  # Добавляем в контекст для шаблона
    'order': order  # Добавляем в контекст для шаблона
  }
  return render(request, 'my_budget/expense.html', context)




# Представление итогов
def summary_list(request):
  # Получение параметров периода
  try:
    month = int(request.GET.get('month', datetime.now().month))  # По умолчанию 1 (январь)
    year = int(request.GET.get('year', datetime.now().year))  # Задайте нужный год
  except (ValueError, TypeError):
    month = datetime.now().month
    year = datetime.now().year

  # Обработка закрытия месяца
  if 'close_month' in request.POST:
    try:
      summary = Summary.objects.get(month=month, year=year)
      summary.close_month()  # Вызов метода модели
      return redirect('my_budget:summary')
    except Summary.DoesNotExist:
      pass  # Обработка ошибки отсутствия сводки
  
  # Получение данных
  try:
    summary = Summary.objects.get(month=month, year=year)
  except Summary.DoesNotExist:
    summary = None

  context = {
    'summary': summary,
    "month": month,
    'year': year,
  }
  return render(request, 'my_budget/budget_summary.html', context)



#                   AJAX-обработки



# Создание дохода
@csrf_exempt
def create_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "errors": form.errors})
    return JsonResponse({"status": "invalid method"})

# Удаление дохода
@csrf_exempt
def delete_income(request, pk):
    """Удаление дохода по ID"""
    try:
        Income.objects.get(pk=pk).delete()
        return JsonResponse({"status": "success"})
    except Income.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Доход не найден!"})

# Создание расхода
@csrf_exempt
def create_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "errors": form.errors})
    return JsonResponse({"status": "invalid method"})

# Удаление расхода
@csrf_exempt
def delete_expense(request, pk):
    """Удаление расхода по ID"""
    try:
        Expense.objects.get(pk=pk).delete()
        return JsonResponse({"status": "success"})
    except Expense.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Расход не найден!"})

# Создание категории дохода
@csrf_exempt
def create_income_category(request):
    if request.method == "POST":
        form = IncomeCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Категория создана!"})
        return JsonResponse({"status": "error", "errors": form.errors})
    return JsonResponse({"status": "invalid method"})

# Удаление категории дохода
@csrf_exempt
def delete_income_category(request, pk):
    """Удаление категории дохода по ID"""
    try:
        IncomeCategory.objects.get(pk=pk).delete()
        return JsonResponse({"status": "success"})
    except IncomeCategory.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Категория не найдена!"})

# Создание категории расхода
@csrf_exempt
def create_expense_category(request):
    if request.method == "POST":
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Категория создана!"})
        return JsonResponse({"status": "error", "errors": form.errors})
    return JsonResponse({"status": "invalid method"})

# Удаление категории расхода
@csrf_exempt
def delete_expense_category(request, pk):
    """Удаление категории расхода по ID"""
    try:
        ExpenseCategory.objects.get(pk=pk).delete()
        return JsonResponse({"status": "success"})
    except ExpenseCategory.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Категория не найдена!"})