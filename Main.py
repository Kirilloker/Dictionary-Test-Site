from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for
import os
import json
import datetime

import logging

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

@app.route('/dictionary/<path:filename>')
def download_file(filename):
    return send_from_directory('Dictionary', filename)

@app.route('/view_dictionary')
def view_dictionary_list():
    return render_template('view_dictionary.html')

@app.route('/create_test_view')
def view_create_test():
    return render_template('create_test.html')

@app.route('/take_test')
def view_take_test():
    return render_template('take_test.html')

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

@app.route('/create_dictionary/<dictionary_name>')
def create_dictionary(dictionary_name):
    return render_template('create_dictionary.html', dictionary_name=dictionary_name)

@app.route('/add_term', methods=['POST'])
def add_term():
    dictionary_name = request.form.get('dictionary_name')
    term = request.form.get('term')
    definition = request.form.get('definition')

    dictionary_folder = 'Dictionary'
    dictionary_path = os.path.join(dictionary_folder, dictionary_name)
    
    if (dictionary_path[len(dictionary_path)-5:] != ".json"):
        dictionary_path += ".json" 

    if not os.path.exists(dictionary_path):
        with open(dictionary_path, 'w', encoding='utf-8') as json_file:
            json.dump({}, json_file, ensure_ascii=False)

    try:
        with open(dictionary_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

            data[term] = definition

        with open(dictionary_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False)

        return redirect(url_for('view_dictionary_deep', dictionary_name=dictionary_name))
    except FileNotFoundError:
        return 'File not found', 404


@app.route('/create_test', methods=['POST'])
def create_test():
    name = request.form.get('name')
    num_questions = int(request.form.get('num_questions'))
    term_ratio = int(request.form.get('term_ratio'))
    acceptable_error = int(request.form.get('acceptable_error'))
    dictionaries = request.form.getlist('dictionaries[]')

    for i in range(len(dictionaries)):
        dictionaries[i] += ".json"

    test = Test(name, dictionaries, num_questions, term_ratio, acceptable_error)

    test_folder = 'Test'
    test_path = os.path.join(test_folder, f'{name}.json')

    with open(test_path, 'w', encoding='utf-8') as json_file:
        json.dump(test.__dict__, json_file, ensure_ascii=False)

    return redirect('/')

@app.route('/get_test_list')
def get_test_list():
    test_folder = 'Test'
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    test_files = [os.path.splitext(f)[0] for f in os.listdir(test_folder) if f.endswith('.json')]
    return jsonify(test_files)

@app.route('/take_test', methods=['POST'])
def take_test():
    key = request.form.get('key')

    test_folder = 'Test'
    test_path = os.path.join(test_folder, f'{key}.json')

    if os.path.exists(test_path):
        return 'Test already exists', 400

    with open(test_path, 'w', encoding='utf-8') as json_file:
        json.dump({}, json_file)

    return redirect(url_for('view_test', test_key=key))

@app.route('/view_test/<test_key>')
def view_test(test_key):
    test_name, key = test_key.rsplit('-', 1)

    test = load_test(test_name)

    if test:
        creator = TestCreator(test)
        
        test_data = creator.create_test(seed=key)
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
    print(test_path)
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

from difflib import SequenceMatcher

def calculate_similarity(str1, str2):
    matcher = SequenceMatcher(None, str1.lower(), str2.lower())
    return matcher.ratio() * 100

def evaluate_answers(correct_answers, user_answers, accuracy_threshold):
    result = ""
    correct_count = 0
    total_questions = len(correct_answers)

    for i in range(total_questions):
        correct_answer = correct_answers[i]
        user_answer = user_answers[i]

        similarity_percentage = calculate_similarity(correct_answer, user_answer)

        result += (f"|Вопрос {i + 1}:\n|")
        result += (f"Правильный ответ: {correct_answer}\n|")
        result += (f"Ответ пользователя: {user_answer}\n|")
        result += (f"Схожесть: {similarity_percentage:.2f}%\n\n|")

        if similarity_percentage >= accuracy_threshold:
            correct_count += 1

    incorrect_count = total_questions - correct_count
    accuracy_percentage = (correct_count / total_questions) * 100
    tmp = ""
    tmp += (f"||Итог:\n|")
    tmp += (f"Правильных ответов: {correct_count}\n|")
    tmp += (f"Неправильных ответов: {incorrect_count}\n|")
    tmp += (f"Процент правильности: {accuracy_percentage:.2f}%\n|")

    result = tmp + result

    return result


from flask import render_template, redirect

@app.route('/result_page')
def result_page_empty():
    result = request.args.get('result', 'Ошибка: тест не найден')  # Получаем значение параметра result из URL
    return render_template('result_page.html', result=result)

@app.route('/result_page/<result>')
def result_page(result):
    return render_template('result_page.html', result=result)

@app.route('/submit_test', methods=['POST'])
def submit_test():
    data = request.json
    answers = data.get('answers')
    current_url = data.get('currentURL')

    tmp = current_url.split('/')[-1]
    test_name = tmp.split('-')[0]
    test_name = test_name.replace("%20"," ")
    key = tmp.split('-')[1]
    test = load_test(test_name)

    if test:
        creator = TestCreator(test)
        test_data = creator.create_test(seed=key)
        result = evaluate_answers(test_data["answers"], answers, test.acceptable_error)
        
        print(datetime.datetime.now())
        print(result)
        
        return jsonify(result)

    return jsonify("Тест не найден")

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)