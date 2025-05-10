def pluralize(n: int, word: str) -> str:
  """
  Склоняет существительные для русского языка.
  Примеры:
    pluralize(1, "сводка") → "1 сводка"
    pluralize(3, "сводка") → "3 сводки"
    pluralize(5, "сводка") → "5 сводок"
  """
  if n % 10 == 1 and n % 100 != 11:
    return f"{n} {word}"
  elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
    return f"{n} {word}и"
  else:
    return f"{n} {word}ок"

# ---------------------------------------------------------------
# Заменяем старые функции на новые, использующие pluralize
# ---------------------------------------------------------------

def get_income_category_message(count: int) -> str:
  """Возвращает сообщение о количестве категорий доходов."""
  if count == 0:
    return "Нет категорий доходов"
  return pluralize(count, "категория доходов")

def get_expense_category_message(count: int) -> str:
  """Возвращает сообщение о количестве категорий расходов."""
  if count == 0:
    return "Нет категорий расходов"
  return pluralize(count, "категория расходов")