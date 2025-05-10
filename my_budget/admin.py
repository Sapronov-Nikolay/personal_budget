from django.contrib import admin
from .models import Summary
from .utils import pluralize  # Кастомная функция для склонения существительных
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.conf import settings
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Summary

# Кастомизация заголовка админ-панели с логотипом
admin.site.site_header = format_html(
   '<img src="{}" height="40"> Админка Бюджета',
   settings.STATIC_URL + 'img/budget.png')


@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
  """Административный интерфейс для категорий доходов"""
  list_display = ('name',)  # Отображаемые поля в списке
  verbose_name = IncomeCategory._meta.verbose_name
  verbose_name_plural = IncomeCategory._meta.verbose_name_plural

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
  """Административный интерфейс для категорий расходов"""
  list_display = ('name',)  # Отображаемые поля в списке
  verbose_name = ExpenseCategory._meta.verbose_name
  verbose_name_plural = ExpenseCategory._meta.verbose_name_plural

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
  """Администрирование доходов с сортировкой по дате"""
  list_display = ('date', 'category', 'amount')  # Порядок отображения полей
  verbose_name = Income._meta.verbose_name
  verbose_name_plural = Income._meta.verbose_name_plural

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
  """Администрирование расходов с фильтрацией по категориям"""
  list_display = ('date', 'category', 'amount')  # Порядок отображения полей
  verbose_name = Expense._meta.verbose_name
  verbose_name_plural = Expense._meta.verbose_name_plural

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    """Кастомизированный интерфейс для работы со сводками"""
    actions = ["delete_selected_summaries"]  # Собственное действие для удаления
    
    # Этот код нужен для сайта
    def delete_selected_summaries(self, request, queryset):
        """Кастомное действие для удаления с обработкой исключений"""
        try:
            count = queryset.count()
            queryset.delete()
            # Показ сообщения об успехе с правильным склонением
            self.message_user(
                request, 
                f"Успешно удалена {pluralize(count, 'сводка')}", 
                messages.SUCCESS
            )
        except Exception as e:
            # Обработка и логирование ошибок
            self.message_user(
                request, 
                f"Ошибка удаления: {str(e)}", 
                messages.ERROR
            )
        return HttpResponseRedirect(request.get_full_path())
    
    delete_selected_summaries.short_description = "Удалить выбранные сводки"
    
    # Чтобы исправить дублирование действий в админ-панели для модели Summary
    def get_actions(self, request):
        #Удаляет стандартное действие 'delete_selected'
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        # Явно добавляем кастомное действие
        actions["delete_selected_summaries"]
        return actions

    # Используем только существующие поля из модели
    list_display = ["get_period", "income", "expense", "balance", "is_closed"]
    
    # Кастомный метод для отображения периода
    def get_period(self, obj):
        """Форматирование периода в виде ММ/ГГГГ"""
        return f"{obj.month}/{obj.year}"
    get_period.short_description = "Период"  # Заголовок колонки

    def changelist_view(self, request, extra_context=None):
        """Добавление кастомного контекста для отображения"""
        extra_context = extra_context or {}
        # Отображение количества выбранных элементов
        selected_count = self.get_selected_count(request)
        extra_context["selected_status"] = f"Выбрано: {pluralize(selected_count, 'сводка')}"
        return super().changelist_view(request, extra_context=extra_context)

    def get_selected_count(self, request):
        """Получение количества выбранных записей"""
        return len(request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME))