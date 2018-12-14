import sys, os, subprocess, time
from PyQt5 import uic
import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QTextBrowser


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


class DirNotFoundError(Exception):
    pass



def launch(test, fname, TL):
    
    g = open('tmp.txt', 'w')
    p = subprocess.Popen(['type', test, '|',  'python', fname], stdout=g, stdin=subprocess.PIPE, shell=True, bufsize=-1)
    
    try:
        p.communicate(timeout=TL/1000)
    except:
        kill(p.pid)
        raise TimeoutError
    
    g.close()
    result = open('tmp.txt').read()
    return result.strip().replace('\r', '')


def formats(string):
    if len(string) > 200:
        return string[:200] + '... (answer too long to be displayed fully)'
    else:
        return string


def check(test, fname, num, TL):    try:
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
Правильный ответ: {formats(correct_answer)}
Вывод программы: {formats(result)}''', False, 'WA'



class MyWidget(QMainWindow):
    
    
    def __init__(self):
        self.std = True
        super().__init__()
        uic.loadUi('tester.ui', self)
        self.launch.clicked.connect(self.run)
        
        self.stdio.clicked.connect(self.fstdio)
        self.fileio.clicked.connect(self.ffileio)
    
    
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
    
    
    def choose(self):
        pass
     
     
    def verdict(self, number_of_tests, number_of_passed_tests,
                last_error, terminate_in_case_of_error):

        if terminate_in_case_of_error:
            
            if number_of_tests == number_of_passed_tests:
                text = "<span style=\" color: #00cc00;\">Полное решение</span>"
                
            else:
                if last_error == 'TLE':
                    text = f"<span style=\" color: #0000aa;\">Превышено ограничение времени на тесте {number_of_tests}</span>"
                elif last_error == 'WA':
                    text = f"<span style=\" color: #0000aa;\">Неправильный ответ на тесте {number_of_tests}</span>"
                elif last_error == 'RE':
                    text = f"<span style=\" color: #aa0000;\">Ошибка исполнения на тесте {number_of_tests}</span>"
        
        else:
            if number_of_tests == number_of_passed_tests:
                text = f"<span style=\" color: #ff0000;\">Полное решение</span>"
                
            else:
                text = f"<span style=\" color: #bbbb00;\">Частичное решение, пройдено {number_of_passed_tests} тестов из {number_of_tests}</span>"
        
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
                QApplication.processEvents()
                
                if not self.check_for_error and self.stopiffailed.isChecked():
                    break
        assert self.i
    
      
    def run(self):
        
        self.launch.setEnabled(False)
        self.logBox.setText('')
        self.begin = time.time()
        self.last_error = "AC"
        
        self.path = self.testdir.text() + '\\'
        self.fname = self.choosefile.text()
        
        self.i = 0
        self.successful = 0
        self.time_limit = int(self.TL.text())
    
        try:
            if not os.path.isfile(self.fname):
                raise FileNotFoundError
            if not os.path.isdir(self.path):
                raise DirNotFoundError
            self.tester(os.listdir(self.path), self.path)  
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

