from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save, post_delete



# Модель категорий доходов
class IncomeCategory(models.Model):
  """
  Категории для классификации доходов.
  Атрибуты:
  - name: Название категории (макс. 100 символов)
  - created_at: Дата создания (автоматически при добавлении)
    """
  name = models.CharField(
    max_length=100,
    verbose_name="Категория"
  )
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name
  
  class Meta:
    db_table = 'personal_budget'  # Кастомное имя таблицы в БД
    verbose_name = "Категория дохода"
    verbose_name_plural = "Категории доходов"




# Модель категорий расходов
class ExpenseCategory(models.Model):
  """
  Категории для классификации расходов.
  Структура аналогична IncomeCategory.
    """
  name = models.CharField(
    max_length=100,
    verbose_name="Категория"
  )
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name = "Категория расхода"
    verbose_name_plural = "Категории расходов"





# Модель таблицы доходов
class Income(models.Model):
  """
  Конкретные операции доходов.
  Особенности:
  - date: Автоматическая фиксация даты создания
  - amount: Валидация минимального значения (0.01)
  - Связь с категорией через ForeignKey
    """
  date = models.DateField(auto_now_add=True)
  category = models.ForeignKey(
    IncomeCategory,
    on_delete=models.CASCADE,
    verbose_name="Категория"
  )
  amount = models.DecimalField(
    max_digits=12,         # Макс. 12 цифр включая 2 после запятой
    decimal_places=2,
    validators=[MinValueValidator(0.01)],  # Запрет нулевых и отрицательных значений
    help_text="Формат: до 12 цифр (включая 2 знака после запятой). Пример: 1000.50",
    verbose_name="Сумма"
  )

  class Meta:
    verbose_name = "доход"
    verbose_name_plural = "доходы"

  def __str__(self):
    formatted_amount = f"{self.amount:.2f} Р"
    return f'Доход: {formatted_amount} - {self.category} на {self.date}'




# Модель таблицы расходов
class Expense(models.Model):
  """
  Конкретные операции расходов.
  Структура аналогична Income, но для расходных операций.
    """
  date = models.DateField(auto_now_add=True)
  category = models.ForeignKey(
    ExpenseCategory,
    on_delete=models.CASCADE,
    verbose_name="Категория"
  )
  amount = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    validators=[MinValueValidator(0.01)],
    help_text="Формат: до 12 цифр (включая 2 знака после запятой). Пример: 1000.50",
    verbose_name="Сумма"
  )

  class Meta:
    verbose_name = "расход"
    verbose_name_plural = "расходы"

  def __str__(self):
    formatted_amount = f"{self.amount:.2f} Р"
    return f'Расход: {formatted_amount} - {self.category} на {self.date}'

# Кортежи с названиями месяцев для русского языка 
# (именительный и родительный падежи)
MONTH_NAMES = [
  ('январь', 'января'), ('февраль', 'февраля'), ('март', 'марта'),
  ('апрель', 'апреля'), ('май', 'мая'), ('июнь', 'июня'),
  ('июль', 'июля'), ('август', 'августа'), ('сентябрь', 'сентября'),
  ('октябрь', 'октября'), ('ноябрь', 'ноября'), ('декабрь', 'декабря')
]

# Модель таблицы итогов
class Summary(models.Model):
  """
  Ежемесячные финансовые итоги.
  Основные показатели:
  - initial_balance: Начальный баланс месяца
  - income/expense: Суммарные доходы/расходы
  - balance: Конечный баланс (авторасчет)
  - is_closed: Флаг закрытия месяца
    """
  initial_balance = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
  )
  month = models.IntegerField()  # 1-12
  year = models.IntegerField()
  income = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
  )
  expense = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
  )
  balance = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
  )
  is_closed = models.BooleanField(default=False)  # Закрыт ли месяц для изменений


  def __str__(self):
    """
    Человеко-читаемое представление записи.
    Использует русские названия месяцев в родительном падеже.
    
    Пример: "Итоги за март 2025 года: Доход 15000.00 Р..."
    """
    month_num = self.month - 1  # Корректировка индекса (месяцы 1-12 -> 0-11)
    if 0 <= month_num < 12:
      # Безопасное получение названия месяца
      month_name = MONTH_NAMES[month_num][1]  # Берем родительный падеж
    else:
      month_name = 'неизвестный месяц'
    
    return (
      f"Итоги за {month_name} {self.year} года: "
      f"Доход {self.income:.2f} Р, "
      f"Расход {self.expense:.2f} Р, "
      f"Баланс {self.balance:.2f} Р"
    )

  def close_month(self):
    """Создает запись для следующего месяца с переносом баланса"""
    next_month = self.month + 1 if self.month < 12 else 1
    next_year = self.year if self.month < 12 else self.year +1
    Summary.objects.update_or_create(
      month=next_month,
      year=next_year,
      defaults={
        'initial_balance': self.balance
      }
    )
    self.is_closed = True
    self.save()

  def clean(self):
    """Валидация вводимых данных"""
    if not (1 <= self.month <= 12):
      raise ValidationError('Месяц должен быть от 1 до 12')
    if self.year < 0:
      raise ValidationError('Год не может быть отрицательным')

  def save(self, *args, **kwargs):
    """Принудительная проверка перед сохранением"""
    self.clean()
    super().save(*args, **kwargs)

  def __str__(self):
    return (
      f"Итоги за {self.month}/{self.year}: "
      f"Доход {self.income:.2f} Р, "
      f"Расход {self.expense:.2f} Р, "
      f"Баланс {self.balance:.2f} Р"
    )
  
  class Meta:
    verbose_name = "Сводку"
    verbose_name_plural = "Сводки"





  @classmethod
  def total_income(cls, year, month):
    """Сумма доходов за указанный период"""
    return Income.objects.filter(
      date__year=year,
      date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0

  @classmethod
  def total_expense(cls, year, month):
    """Сумма расходов за указанный период"""
    return Expense.objects.filter(
      date__year=year,
      date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0
  
# Сигналы для автоматического обновления сводки доходов
@receiver([post_save, post_delete], sender=Income)
@receiver([post_save, post_delete], sender=Expense)
def update_summary(sender, instance, **kwargs):
  """
  Автоматически обновляет сводку при изменении доходов/расходов.
  Действия:
  1. Определяет месяц и год операции
  2. Пересчитывает итоги
  3. Обновляет или создает запись Summary
  """
  month = instance.date.month
  year = instance.date.year
  
  # Полная пересборка данных
  total_income = Income.objects.filter(
    date__year=year, 
    date__month=month
  ).aggregate(total=Sum('amount'))['total'] or 0
  
  total_expense = Expense.objects.filter(
    date__year=year, 
    date__month=month
  ).aggregate(total=Sum('amount'))['total'] or 0

  Summary.objects.update_or_create(
    month=month,
    year=year,
    defaults={
      'income': total_income,
      'expense': total_expense,
      'balance': total_income - total_expense
    }
  )

@receiver(pre_save, sender=ExpenseCategory)
def set_created_at(sender, instance, **kwargs):
    """Устанавливает дату создания для новых категорий расходов"""
    if not instance.pk:  # Только для новых записей
        instance.created_at = timezone.now()