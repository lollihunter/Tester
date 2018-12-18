import sys
import os
import inspect
import time
import ui
import subprocess
import threading
import importlib
import psutil
from inspect import getmembers, isfunction
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QTextBrowser, QTableWidgetItem


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


class Run(object):
    def __init__(self, function, args):
        self.function = function
        self.args = args
        self.answer = TimeoutError

    def worker(self):
        self.answer = self.function(*self.args)

    def run(self, timeout):
        thread = threading.Thread(target=self.worker)
        thread.start()
        thread.join(timeout)
        return self.answer

        
class DirNotFoundError(Exception):
    pass


class TestNotFoundError(Exception):
    pass


class FileNotAvailable(Exception):
    pass


def launch(test, fname, TL, stdinput=subprocess.PIPE, stdoutput='tmp.txt'):
    
    g = open(stdoutput, 'w')
    p = subprocess.Popen(['type', test, '|',  'python', fname], stdout=g, stdin=stdinput, shell=True, bufsize=-1)
    
    try:
        p.communicate(timeout=TL / 1000)
    except:
        kill(p.pid)
        raise TimeoutError
    
    g.close()
    result = open('tmp.txt').read()
    return result.strip().replace('\r', '')


def unit_launch(test, fname, delim, func):
    
    import tmp
    importlib.reload(tmp)
    f = open(test).read().split(delim)
    print(f'tmp.{func}(' + ','.join(f) + ')')
    return str(eval(f'tmp.{func}(' + ','.join(f) + ')'))


def formats(string, length, long=True):
    
    if len(string) > length:
        return string[:length] + '...' + ' (answer too long to be displayed fully)' * long
    else:
        return string


def check(test, fname, num, TL, delim=';', func='', reg=True):
        try:
        begin = time.time()
        
        if reg:
            result = launch(test, fname, TL)
        else:
            func = Run(unit_launch, (test, fname, delim, func))
            result = func.run(TL / 1000)
        
        end = time.time()
        
    except TimeoutError:
        return f'Превышено ограничение по времени на тесте {num}, {TL} мс', False, 'TLE'
    
    except Exception as e:
        return f'Ошибка исполнения на тесте {num}: ' + type(e).__name__ + f', 0 мс\n{e}', False, 'RE'
    
    else:
        correct_answer = open(test[:-3] + '.out').read().strip()
        if result == correct_answer and not (result is TimeoutError):
            return f'Тест {num} успешно пройден, {int(1000* (end - begin))} мс', True, 'AC'
        else:
            
            try:
                s = formats(result, 200)
            except TypeError:
                s = ''
                
            return f'''Неправильный ответ на тесте {num}, {int(1000* (end - begin))} мс
Правильный ответ: {formats(correct_answer, 200)}
Вывод программы: {s}''', False, 'WA'


class MyWidget(QMainWindow, ui.Ui_Tester):
    
    
    def __init__(self):
        
        self.std = True
        super().__init__()
        
        self.setupUi(self)
        self.launch.clicked.connect(self.run)
        self.setFixedSize(self.size())
        self.choosefilebtn.clicked.connect(self.choose_file_to_check)
        self.addtest.clicked.connect(self.add_test)
        
        self.loadfuncs.clicked.connect(self.load_functions)
        self.explorer.clicked.connect(self.choose_directory_with_tests)
        self.stdio.clicked.connect(self.fstdio)
        self.fileio.clicked.connect(self.ffileio)
        self.showtest.clicked.connect(self.visualise_tests)
        self.remtest.clicked.connect(self.delete_tests)
        self.unitTest.clicked.connect(self.enable_utest)
        self.regularTest.clicked.connect(self.disable_utest)
        self.edit.clicked.connect(self.edit_tests)
        self.delim.clicked.connect(self.custom_delim)
        self.delimit = ';'
        
        header = self.table.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)        
    
    
    def fstdio(self):
        
        self.std = True
        self.inputfile.setText('')
        self.outputfile.setText('')
        self.inputfile.setEnabled(False)
        self.outputfile.setEnabled(False)
    
    
    def ffileio(self):
        
        self.std = False
        self.inputfile.setText('input.txt')
        self.outputfile.setText('output.txt')        
        self.inputfile.setEnabled(True)
        self.outputfile.setEnabled(True)        
    
    
    def choose_file_to_check(self):
        
        fname = str(QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()",
                                                "","Python Files (*.py)")[0])
        if fname:
            self.choosefile.setText(fname)
    
    
    def get_last(self, path):
        
        try:
            files = list(filter(lambda x: x[-3:] == '.in', sorted(os.listdir(path))))[-1][:-3]
        except:
            return '1'
        
        if not files[-1].isdigit() or os.path.isfile(path + files[:-1] + 
                                                str(int(files[-1]) + 1) + '.in'):
            return files + '1' 
        return files[:-1] + str(int(files[-1]) + 1)
    
    
    def custom_delim(self):
        
        self.delimit = self.delimiter.text()
        self.write_log(self.exportfile.text(),
    f'0 Знак-разделитель для юнит-теста изменён на {self.delimiter.text()}\n\n')
    
    
    def enable_utest(self):
        
        self.choosefuncs.setEnabled(1)
        self.loadfuncs.setEnabled(1)
        self.funclist.setEnabled(1)
        
        
    def disable_utest(self):
        
        self.choosefuncs.setEnabled(0)
        self.loadfuncs.setEnabled(0)     
        self.funclist.setEnabled(0)
    
    
    def add_test(self):
        
        self.infile = self.inpdata.toPlainText()
        self.outfile = self.outdata.toPlainText()
        
        try:
            self.path = self.testdir.text().replace('/', '\\') + '\\'
            name = self.get_last(self.path)
            
            f = open(self.path + name + '.in', 'w')
            f.write(self.infile)
            
            g = open(self.path + name + '.out', 'w')
            g.write(self.outfile)
            
            f.close()
            g.close()
            
        except Exception:
            self.write_log(self.exportfile.text(),
                           f'0 Не удалось добавить тест по указанному адресу, отказано в доступе\n\n')
        else:
            self.visualise_tests()
            self.write_log(self.exportfile.text(),
                           f'0 Добавлен тест по адресу {self.path + name} (-.in + -.out) успешно\n\n')
        
    
    def write_log(self, file, text):
        
        self.logBox.append(text)
        if len(file):
            f = open(file, 'a')
            f.write(text)
            f.close()
        
    
    def delete_tests(self):
        
        self.path = self.testdir.text().replace('/', '\\') + '\\'            
        indexes = self.table.selectionModel().selectedRows()
        print(indexes)
        for index in indexes:
            
            file = self.table.item(index.row(), 0).text()[:-8]
            
            try:
                os.remove(self.path + file + '.in')
                os.remove(self.path + file + '.out')
            except Exception:
                self.write_log(self.exportfile.text(),
                               '0 Не удалось удалить один из файлов теста(-ов)\n\n')
            else:
                self.write_log(self.exportfile.text(),
                               f'0 Успешно удалён тест {self.path + file} (.in/.out)\n\n')
        
        self.visualise_tests()
        
        
    def edit_tests(self):
        
        self.path = self.testdir.text().replace('/', '\\') + '\\'            
        indexes = self.table.selectionModel().selectedRows()

        for index in indexes:
            file = self.table.item(index.row(), 0).text()[:-8]
            try:
                f = open(self.path + file + '.in', 'w')
                g = open(self.path + file + '.out', 'w')
                
                f.write(self.inpdata.toPlainText())
                g.write(self.outdata.toPlainText())
                
                f.close()
                g.close()
                
            except Exception:
                self.write_log(self.exportfile.text(),
                               '0 Не удалось изменить один из файлов теста(-ов)\n\n')
            
            else:
                self.write_log(self.exportfile.text(),
                               f'0 Успешно изменен тест {self.path + file} (.in/.out)\n\n')
        
        self.visualise_tests()
        
        
    def visualise_tests(self):
        
        self.table.setRowCount(0);        
        self.path = self.testdir.text().replace('/', '\\') + '\\'    
        for file in os.listdir(self.path):
            if file.endswith('.in'):
                try:
                    f = open(self.path + file).read()
                    g = open(self.path + file[:-3] + '.out').read()
                    
                except Exception:
                    self.write_log(self.exportfile.text(),
                                   f'0 Не удалось отобразить один из тестов в директории {self.path}')
                    continue
                
                else:
                    rowPosition = self.table.rowCount()
                    self.table.insertRow(rowPosition)        
                    self.table.setItem(rowPosition, 0, 
                                       QTableWidgetItem(file + '/.out'))
                    self.table.setItem(rowPosition, 1, 
                                       QTableWidgetItem(formats(f, 15, long=False)))
                    self.table.setItem(rowPosition, 2, 
                                       QTableWidgetItem(formats(g, 15, long=False)))                    

    
            
    def load_functions(self):
        
        self.funclist.clear()
        
        try:
            script = open(self.choosefile.text()).read()
            f = open('tmp.py', 'w')
            f.write(script)
            f.close()            
            
            import tmp # Importing all functions to a tester
            importlib.reload(tmp)
            functions_list = [o[0] for o in inspect.getmembers(tmp) if inspect.isfunction(o[1])]
            if not functions_list:
                raise Exception
            for function in functions_list:
                self.funclist.addItem(function)
                
        except Exception:
            self.write_log(self.exportfile.text(),
                                f'0 Не удалось загрузить функции из файла {self.choosefile.text()}\n\n')
        
        else:
            self.write_log(self.exportfile.text(),
                                f'0 Успешно загружены функции из файла {self.choosefile.text()}\n\n')
            self.funclist.setCurrentRow(0)
            self.cur_func = self.funclist.currentItem().text() 
     
     
    def choose_directory_with_tests(self):
        
        directory = str(QFileDialog.getExistingDirectory(self, "Choose Directory"))
        if directory:
            self.testdir.setText(directory)
        
     
    def verdict(self, number_of_tests, number_of_passed_tests,
                last_error, terminate_in_case_of_error):

        if terminate_in_case_of_error:
            
            if number_of_tests == number_of_passed_tests:
                text = "<span style=\" color: #009900;\"><b>Полное решение</b></span>"
                
            else:
                if last_error == 'TLE':
                    text = f"<span style=\" color: #0000aa;\">Превышено ограничение времени на тесте {number_of_tests}</span>"
                elif last_error == 'WA':
                    text = f"<span style=\" color: #0000aa;\">Неправильный ответ на тесте {number_of_tests}</span>"
                elif last_error == 'RE':
                    text = f"<span style=\" color: #aa0000;\">Ошибка исполнения на тесте {number_of_tests}</span>"
        
        else:
            if number_of_tests == number_of_passed_tests:
                text = f"<span style=\" color: #009900;\"><b>Полное решение</b></span>"
                
            else:
                text = f"<span style=\" color: #999900;\">Частичное решение, пройдено {number_of_passed_tests} тестов из {number_of_tests}</span>"
        
        return text
            
    
    def tester(self, path, system_path):
        
        for test in path:
            if test.endswith('.in'):
                self.i += 1
                
                if self.regularTest.isChecked():
                    self.cur_func = ''
                
                results = check(system_path + test, self.fname,
                                self.i, self.time_limit, self.delimit, self.cur_func,
                                self.regularTest.isChecked())
                    
                res = results[0]
                self.successful += results[1] # Successful runs
                self.check_for_error = results[1] # Check if last run was successful
                self.last_error = results[2] # Display last error if exists

                text = self.logBox.toPlainText()
                self.write_log(self.exportfile.text(),
                               f'{int(1000 * (time.time() - self.begin))}' + ' ' + res + '\n\n')
                
                if self.stopiffailed.isChecked() and not self.check_for_error:
                    if self.last_error == 'WA':
                        self.status.setText(f"Статус: <span style=\" color: #0000aa;\">Неправильный ответ на тесте {self.i}</span>")
                    elif self.last_error == 'TLE':
                        self.status.setText(f"Статус: <span style=\" color: #0000aa;\">Превышено ограничение времени на тесте {self.i}</span>")
                    else:
                        self.status.setText(f"Статус: <span style=\" color: #0000aa;\">Ошибка исполнения на тесте {self.i}</span>")
                
                else:
                    self.status.setText(f"Статус: <span style=\" color: #747474;\">Выполняется на тесте {self.i}</span>")
                
                QApplication.processEvents()
                
                if not self.check_for_error and self.stopiffailed.isChecked():
                    break
        
        assert self.i
        
        if self.i == self.successful and self.regularTest.isChecked():
            self.status.setText(f"Статус:<span style=\" color: #009900;\"><b> Полное решение</span></b>")
        
        elif self.i == self.successful:
            self.status.setText(f"Статус:<span style=\" color: #009900;\"><b> Полная работоспособность</span></b>")
            
        elif not self.stopiffailed.isChecked() and self.regularTest.isChecked():
            self.status.setText(f"Статус:<span style=\" color: #999900;\"><b> Частичное решение</span></b>")
            
        elif not self.stopiffailed.isChecked():
            self.status.setText(f"Статус:<span style=\" color: #999900;\"><b> Частичная работоспособность</span></b>")

      
    def run(self):
        
        self.launch.setEnabled(False)
        self.regularTest.setEnabled(False)
        self.unitTest.setEnabled(False)
        
        self.logBox.setText('')
        self.begin = time.time()
        self.last_error = "AC"
        
        self.path = self.testdir.text().replace('/', '\\') + '\\'
        self.fname = self.choosefile.text()
        
        self.i = 0
        self.successful = 0
        self.time_limit = int(self.TL.text())
    
        try:
            if not os.path.isfile(self.fname):
                raise FileNotFoundError
            if not os.path.isdir(self.path):
                raise DirNotFoundError
            self.tester(sorted(os.listdir(self.path)), self.path)
            
        except AssertionError:
            self.write_log(self.exportfile.text(), 
                           f'{int(1000 * (time.time() - self.begin))}' + 
                           f' Директория {self.path} не содержит тестов\n\n')
            self.write_log(self.exportfile.text(),
                           f'{int(1000 * (time.time() - self.begin))}' +
                           ' ' + 'Активные задачи выполнены\n\n')
            
        except DirNotFoundError:
            self.write_log(self.exportfile.text(),
                           f'{int(1000 * (time.time() - self.begin))}' + 
                           f' На диске не удалось найти директорию {self.path}\n\n')
            self.write_log(self.exportfile.text(),
                           f'{int(1000 * (time.time() - self.begin))}' + 
                           ' ' + 'Активные задачи выполнены\n\n')
            self.resBox.setHtml(f'''Вердикт тестирования:<br><br>        
            <span style=\" color: #cc0000;\">Некорректно установлены параметры тестирования</span>''')
            
        except FileNotFoundError:
            self.write_log(self.exportfile.text(),
                           f'{int(1000 * (time.time() - self.begin))}' +
                           f' На диске не удалось найти файл {self.fname}\n')
            self.write_log(self.exportfile.text(),
                           f'{int(1000 * (time.time() - self.begin))}' +
                           ' ' + 'Активные задачи выполнены\n\n')
            self.resBox.setHtml(f'''Вердикт тестирования:<br><br>        
            <span style=\" color: #cc0000;\">Некорректно установлены параметры тестирования</span>''')    
        
        else:
            self.resBox.setHtml(f'''Вердикт тестирования:<br>        
    Пройдено {self.i} тестов за {int(1000 * (time.time() - self.begin))} мс, успешно {self.successful}<br>
    Среднее время выполнения теста - {(int(1000 * (time.time() - self.begin) / self.i)) if self.i else 0} мс<br><br>
    {self.verdict(self.i, self.successful, self.last_error, self.stopiffailed.isChecked())}''')
            
        self.launch.setEnabled(True)
        self.regularTest.setEnabled(True)
        self.unitTest.setEnabled(True)

app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())

