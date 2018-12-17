import sys, os, subprocess, time
from PyQt5 import uic, QtWidgets
import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QTextBrowser, QTableWidgetItem


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


class DirNotFoundError(Exception):
    pass


def launch(test, fname, TL, stdinput=subprocess.PIPE, stdoutput='tmp.txt'):
    
    g = open(stdoutput, 'w')
    p = subprocess.Popen(['type', test, '|',  'python', fname], stdout=g, stdin=stdinput, shell=True, bufsize=-1)
    
    try:
        p.communicate(timeout=TL/1000)
    except:
        kill(p.pid)
        raise TimeoutError
    
    g.close()
    result = open('tmp.txt').read()
    return result.strip().replace('\r', '')


def formats(string, length, long=True):
    if len(string) > length:
        return string[:length] + '...' + ' (answer too long to be displayed fully)' * long
    else:
        return string


def check(test, fname, num, TL):
        try:
        begin = time.time()
        result = launch(test, fname, TL)
        end = time.time()
        
    except TimeoutError:
        return f'Превышено ограничение по времени на тесте {num}, {TL} мс', False, 'TLE'
    
    except Exception as e:
        return f'Ошибка исполнения на тесте {num}: ' + type(e).__name__ + f', 0 мс\n{e}', False, 'RE'
    
    else:
        correct_answer = open(test[:-3] + '.out').read().strip()
        if result == correct_answer:
            return f'Тест {num} успешно пройден, {int(1000* (end - begin))} мс', True, 'AC'
        else:
            return f'''Неправильный ответ на тесте {num}, {int(1000* (end - begin))} мс
Правильный ответ: {formats(correct_answer, 200)}
Вывод программы: {formats(result, 200)}''', False, 'WA'



class MyWidget(QMainWindow):
    
    
    def __init__(self):
        self.std = True
        super().__init__()
        uic.loadUi('tester.ui', self)
        self.launch.clicked.connect(self.run)
        self.setFixedSize(self.size())
        self.choosefilebtn.clicked.connect(self.choose_file_to_check)
        self.addtest.clicked.connect(self.add_test)
        self.explorer.clicked.connect(self.choose_directory_with_tests)
        self.stdio.clicked.connect(self.fstdio)
        self.fileio.clicked.connect(self.ffileio)
        self.showtest.clicked.connect(self.visualise_tests)
        self.remtest.clicked.connect(self.delete_tests)
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
        files = list(filter(lambda x: x[-3:] == '.in', sorted(os.listdir(path))))[-1][:-3]
        if not files[-1].isdigit() or os.path.isfile(path + files[:-1] + 
                                                str(int(files[-1]) + 1) + '.in'):
            return files + '1' 
        return files[:-1] + str(int(files[-1]) + 1)
    
    
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
            
            f.close(); g.close();
        except Exception:
            self.logBox.append(f'0 Не удалось добавить тест по указанному адресу, отказано в доступе\n\n')
        else:
            self.visualise_tests()
            self.logBox.append(f'0 Добавлен тест по адресу {self.path + name} (-.in + -.out) успешно\n\n')
        
    
    def write_log(self, write_to_file, file, text):
        self.logBox.append(text)
        f = open(file, 'a')
        f.write(text)
    
    
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
                self.logBox.append('0 Не удалось удалить один из файлов теста(-ов)\n\n')
            else:
                self.logBox.append(f'0 Успешно удалён тест {self.path + file} (.in/.out)\n\n')
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
                self.logBox.append('0 Не удалось изменить один из файлов теста(-ов)\n\n')
            
            else:
                self.logBox.append(f'0 Успешно изменен тест {self.path + file} (.in/.out)\n\n')
        
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
                    self.logBox.append(f'0 Не удалось отобразить один из тестов в директории {self.path}')
                    continue
                
                else:
                    rowPosition = self.table.rowCount()
                    self.table.insertRow(rowPosition)        
                    self.table.setItem(rowPosition, 0, QTableWidgetItem(file + '/.out'))
                    self.table.setItem(rowPosition, 1, QTableWidgetItem(formats(f, 15, long=False)))
                    self.table.setItem(rowPosition, 2, QTableWidgetItem(formats(g, 15, long=False)))                    

    
            
    def unittest(self):
        pass
     
     
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
                
                results = check(system_path + test, self.fname, self.i, self.time_limit)
                res = results[0]
                self.successful += results[1]
                self.check_for_error = results[1]
                self.last_error = results[2]

                text = self.logBox.toPlainText()
                self.logBox.append(f'{int(1000 * (time.time() - self.begin))}' + ' ' + res + '\n\n')
                
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
        if self.i == self.successful:
            self.status.setText(f"Статус:<span style=\" color: #009900;\"><b> Полное решение</span></b>")
        elif not self.stopiffailed.isChecked():
            self.status.setText(f"Статус:<span style=\" color: #999900;\"><b> Частичное решение</span></b>")
    
      
    def run(self):
        
        self.launch.setEnabled(False)
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
            self.logBox.append(f'{int(1000 * (time.time() - self.begin))}' + f' Директория {self.path} не содержит тестов\n\n')
            self.logBox.append(f'{int(1000 * (time.time() - self.begin))}' + ' ' + 'Активные задачи выполнены\n\n')
            
        except DirNotFoundError:
            self.logBox.append(f'{int(1000 * (time.time() - self.begin))}' + f' На диске не удалось найти директорию {self.path}\n\n')
            self.logBox.append(f'{int(1000 * (time.time() - self.begin))}' + ' ' + 'Активные задачи выполнены\n\n')
            self.resBox.setHtml(f'''Вердикт тестирования:<br><br>        
            <span style=\" color: #cc0000;\">Некорректно установлены параметры тестирования</span>''')
            
        except FileNotFoundError:
            self.logBox.append(f'{int(1000 * (time.time() - self.begin))}' + f' На диске не удалось найти файл {self.fname}\n')
            self.logBox.append(f'{int(1000 * (time.time() - self.begin))}' + ' ' + 'Активные задачи выполнены\n\n')
            self.resBox.setHtml(f'''Вердикт тестирования:<br><br>        
            <span style=\" color: #cc0000;\">Некорректно установлены параметры тестирования</span>''')
            
        else:
            self.resBox.setHtml(f'''Вердикт тестирования:<br>        
    Пройдено {self.i} тестов за {int(1000 * (time.time() - self.begin))} мс, успешно {self.successful}<br>
    Среднее время выполнения теста - {(int(1000 * (time.time() - self.begin) / self.i)) if self.i else 0} мс<br><br>
    {self.verdict(self.i, self.successful, self.last_error, self.stopiffailed.isChecked())}''')
            
        self.launch.setEnabled(True)

app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())

