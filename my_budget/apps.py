from django.apps import AppConfig

"""
Конфигурация приложения 'my_budget' для Django.

Класс MyBudgetConfig наследует базовую конфигурацию приложения Django и определяет:
- default_auto_field: Тип поля для автоматического создания первичных ключей моделей 
  (BigAutoField - 64-битное целое число)
- name: Официальное имя приложения, используемое Django в внутренних механизмах

Это стандартная конфигурация, необходимая для корректной работы приложения в Django.
"""

class MyBudgetConfig(AppConfig):
    # Автоматическое создание первичных ключей типа BigAutoField
    default_auto_field = 'django.db.models.BigAutoField'
    # Системное имя приложения (должно совпадать с именем папки приложения)
    name = 'my_budget'
