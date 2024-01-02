from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_dictionary_list')
def get_dictionary_list():
    dictionary_folder = 'Dictionary'
    if not os.path.exists(dictionary_folder):
        os.makedirs(dictionary_folder)

    dictionary_files = [f for f in os.listdir(dictionary_folder) if f.endswith('.json')]
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
@app.route('/view_dictionary/<dictionary_name>')
def view_dictionary_deep(dictionary_name):
    dictionary_folder = 'Dictionary'
    dictionary_path = os.path.join(dictionary_folder, dictionary_name)
    print(dictionary_path)
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

    print(dictionary_path)

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


if __name__ == '__main__':
    app.run(debug=True)
