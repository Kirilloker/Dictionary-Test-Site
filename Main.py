from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for
import os
import json

from Test import Test
from Dictionary import Dictionary
from TestCreator import TestCreator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_dictionary_list')
def get_dictionary_list():
    dictionary_folder = 'Dictionary'
    if not os.path.exists(dictionary_folder):
        os.makedirs(dictionary_folder)

    dictionary_files =  [os.path.splitext(f)[0] for f in os.listdir(dictionary_folder) if f.endswith('.json')]
    return jsonify(dictionary_files)

# Маршрут для обслуживания статических файлов словарей
@app.route('/dictionary/<path:filename>')
def download_file(filename):
    return send_from_directory('Dictionary', filename)

# Добавлен маршрут для /view_dictionary без указания словаря
@app.route('/view_dictionary')
def view_dictionary_list():
    return render_template('view_dictionary.html')

# Добавлен маршрут для /view_dictionary без указания словаря
@app.route('/create_test_view')
def view_create_test():
    return render_template('create_test.html')

@app.route('/take_test')
def view_take_test():
    return render_template('take_test.html')

# Добавлен маршрут для /view_dictionary без указания словаря
@app.route('/view_dictionary/<dictionary_name>')
def view_dictionary_deep(dictionary_name):
    dictionary_folder = 'Dictionary'
    dictionary_path = os.path.join(dictionary_folder, dictionary_name)
    dictionary_path += '.json'
    try:
        with open(dictionary_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return render_template('view_dictionary_deep.html', dictionary_name=dictionary_name, dictionary_data=data)
    except FileNotFoundError:
        return 'File not found', 404
    
@app.route('/manage_dictionary')
def manage_dictionary():
    dictionary_folder = 'Dictionary'
    if not os.path.exists(dictionary_folder):
        os.makedirs(dictionary_folder)

    dictionary_files = [f for f in os.listdir(dictionary_folder) if f.endswith('.json')]


    return render_template('manage_dictionary.html', dictionary_list=dictionary_files)


# Добавлен маршрут для /manage_dictionary
# @app.route('/manage_dictionary')
# def manage_dictionary():
#     return render_template('manage_dictionary.html')

# Добавлен маршрут для /create_dictionary/<dictionary_name>
@app.route('/create_dictionary/<dictionary_name>')
def create_dictionary(dictionary_name):
    return render_template('create_dictionary.html', dictionary_name=dictionary_name)

# Добавлен маршрут для /add_term
@app.route('/add_term', methods=['POST'])
def add_term():
    dictionary_name = request.form.get('dictionary_name')
    term = request.form.get('term')
    definition = request.form.get('definition')

    dictionary_folder = 'Dictionary'
    dictionary_path = os.path.join(dictionary_folder, dictionary_name)


    # Создаем словарь, если его нет
    if not os.path.exists(dictionary_path):
        with open(dictionary_path, 'w', encoding='utf-8') as json_file:
            json.dump({}, json_file, ensure_ascii=False)

    try:
        with open(dictionary_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

            # Добавляем термин и определение в словарь
            data[term] = definition

        with open(dictionary_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False)

        return redirect(url_for('view_dictionary_deep', dictionary_name=dictionary_name))
    except FileNotFoundError:
        return 'File not found', 404


# Добавлен маршрут для /create_test
@app.route('/create_test', methods=['POST'])
def create_test():
    name = request.form.get('name')
    num_questions = int(request.form.get('num_questions'))
    term_ratio = int(request.form.get('term_ratio'))
    acceptable_error = int(request.form.get('acceptable_error'))
    dictionaries = request.form.getlist('dictionaries[]')

    for i in range(len(dictionaries)):
        dictionaries[i] += ".json"

    # Создаем экземпляр класса Test
    test = Test(name, dictionaries, num_questions, term_ratio, acceptable_error)

    # Сохраняем экземпляр класса Test в файл
    test_folder = 'Test'
    test_path = os.path.join(test_folder, f'{name}.json')

    with open(test_path, 'w', encoding='utf-8') as json_file:
        json.dump(test.__dict__, json_file, ensure_ascii=False)

    return redirect('/')

# Маршрут для получения списка тестов
@app.route('/get_test_list')
def get_test_list():
    test_folder = 'Test'
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    test_files = [os.path.splitext(f)[0] for f in os.listdir(test_folder) if f.endswith('.json')]
    return jsonify(test_files)

# Маршрут для создания "пустышки" теста
@app.route('/take_test', methods=['POST'])
def take_test():
    key = request.form.get('key')

    # Создаем "пустышку" теста с использованием ключа генерации
    test_folder = 'Test'
    test_path = os.path.join(test_folder, f'{key}.json')

    # Проверяем, существует ли тест с таким ключом
    if os.path.exists(test_path):
        return 'Test already exists', 400

    # Создаем пустой файл для теста
    with open(test_path, 'w', encoding='utf-8') as json_file:
        json.dump({}, json_file)

    # Перенаправляем на страницу просмотра теста
    return redirect(url_for('view_test', test_key=key))

@app.route('/view_test/<test_key>')
def view_test(test_key):
    # Получаем имя теста и ключ генерации из параметра запроса
    test_name, key = test_key.rsplit('-', 1)

    # Загружаем тест по имени
    test = load_test(test_name)

    if test:
        # Создаем экземпляр класса TestCreator
        creator = TestCreator(test)
        
        # Генерируем тест с использованием ключа генерации
        test_data = creator.create_test(seed=key)

        # Отображаем результат на странице
        return render_template('view_test.html', test_name=test_name, test_data=test_data)
    else:
        return 'Test not found', 404

def get_dictionary(dict_name):
    dict_path = os.path.join("Dictionary", f"{dict_name}")
    
    if os.path.exists(dict_path):
        with open(dict_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return Dictionary(name=dict_name, terms=data)
    
    return None

def load_test(test_name):
    test_path = os.path.join("Test", f"{test_name}.json")
    if os.path.exists(test_path):
        with open(test_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            tst = Test(**data)
            for i in range(len(tst.dictionaries)):
                tst.dictionaries[i] = get_dictionary(tst.dictionaries[i])

            return tst
    return None


def generate_test(test_name, dictionaries, num_questions, term_ratio, acceptable_error):
    test = Test(test_name, dictionaries, num_questions, term_ratio, acceptable_error)
    creator = TestCreator(test)
    test_data = creator.create_test()
    test_path = os.path.join("Test", f"{test_name}.json")
    
    with open(test_path, 'w', encoding='utf-8') as json_file:
        json.dump(test_data, json_file)

    return test


@app.route('/submit_test', methods=['POST'])
def submit_test():
    print('test')
    data = request.json
    test_name = data.get('test_name')
    key = data.get('key')
    answers = data.get('answers')

    # Вместо вывода в консоль, вы можете использовать эти данные в вашей логике
    print(f"Test Name: {test_name}")
    print(f"Key: {key}")
    print(f"Answers: {answers}")

    # Ответ клиенту
    return jsonify({"message": "Answers received successfully"})

if __name__ == '__main__':
    app.run(debug=True)