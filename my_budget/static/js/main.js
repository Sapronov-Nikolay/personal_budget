import Chart from 'chart.js/auto';

// Основная инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
  // Обработчик для формы добавления доходов
  const incomeForm = document.getElementById('incomeForm');
  if (incomeForm) {
    incomeForm.addEventListener('submit', function(e) {
      e.preventDefault(); // Отменяем стандартное поведение формы
      const formData = new FormData(this); // Собираем данные формы
      
      // Отправка AJAX-запроса на сервер
      fetch("{% url 'my_budget:create_income' %}", {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': formData.get('csrfmiddlewaretoken') // CSRF-защита
        }
      })
      .then(response => response.json()) // Парсим JSON-ответ
      .then(data => {
        if (data.status === 'success') {
          // Показываем успешное сообщение и обновляем страницу через 1 сек
          showMessage('Доход успешно добавлен', 'success');
          setTimeout(() => window.location.reload(), 1000);
        } else {
          // Показываем ошибки валидации
          showMessage('Ошибка: ' + JSON.stringify(data.errors), 'error');
        }
      });
    });
  }

  // Аналогичный обработчик для формы расходов
  const expenseForm = document.getElementById('expenseForm');
  if (expenseForm) {
    expenseForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      
      fetch("{% url 'my_budget:create_expense' %}", {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          showMessage('Расход успешно добавлен', 'success');
          setTimeout(() => window.location.reload(), 1000);
        } else {
          showMessage('Ошибка: ' + JSON.stringify(data.errors), 'error');
        }
      });
    });
  }
});

// Функция удаления записи дохода
function deleteIncome(id) {
  if (confirm('Удалить эту запись?')) {
    fetch(`/budget/income/delete/${id}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': '{{ csrf_token }}' // CSRF-токен из шаблона
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        window.location.reload(); // Обновляем страницу после удаления
      }
    });
  }
}

// Функция удаления записи расхода (аналогичная логика)
function deleteExpense(id) {
  if (confirm('Удалить эту запись?')) {
    fetch(`/budget/expense/delete/${id}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': '{{ csrf_token }}'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        window.location.reload();
      }
    });
  }
}

/* 
  Вспомогательные функции:
  - showMessage() - должна быть определена в другом месте
  - Все URL (/budget/.../) должны соответствовать вашим маршрутам
  - CSRF-токены обрабатываются как через FormData, так и через шаблоны
  - Для работы кода требуется полифиллы для старых браузеров
*/