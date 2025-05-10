import os

def list_directory(startpath):
  result = []

  for root, dirs, files in os.walk(startpath):
    depth = root.count(os.sep) - startpath.count(os.sep)
    indent = ':    ' * depth

    if os.path.basename(root) == 'venv':
      result.append(indent + '└── venv/')
      result.append(indent + '   └── [Содержимое venv скрыто].')
      dirs.clear()  # Очищаем список поддиректорий
      continue  # Прерываем текущую итерацию, чтобы не выводилось второй раз └── venv/
    
    if os.path.basename(root) == 'node_modules':
      result.append(indent + '└── node_modules/')
      result.append(indent + '   └── [Содержимое node_modules скрыто].')
      dirs.clear()  # Очищаем список поддиректорий
      continue  # Прерываем текущую итерацию, чтобы не выводилось второй раз └── node_modules/

    # Обработка корневой директории
    if depth == 0:
      result.append(os.path.basename(root) + '/')
    else:
      # Для поддеректорий
      result.append(indent + '└── ' + os.path.basename(root) + '/')
    # Обработка файлов (всегда с ├──)
    for file in files:
      result.append(indent + '  ├── ' + file)
      
    # Добавляем пустую строку после каждой папки для читаемости
    if files:
      result.append(indent + '  ')

  return result

def write_structure_to_file(structure):
  with open('Project_structure.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(structure))

if __name__ == "__main__":  # Исправлено на правильный синтаксис
  project_root = r'I:\Mi docum\Personal_Budget\budget'
  structure = list_directory(project_root)
  write_structure_to_file(structure)
  print('Структура проекта успешно создана в Project_structure.txt')
