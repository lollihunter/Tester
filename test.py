import sys, os, subprocess, time, threading
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QTextBrowser

def launch(test, fname):
    p = subprocess.Popen(['type', test, '|',  'python', fname], stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    result = p.communicate()[0]      
    return result.decode('utf-8').strip().replace('\r', '')


def formats(string):
    if len(string) > 200:
        return string[:200] + '... (answer too long to be displayed fully)'
    else:
        return string


def check(test, fname, num, TL):    try:
        begin = time.time()
        result = launch(test, fname)
        end = time.time()
    except TimeoutException:
        return f'Превышено ограничение по времени на тесте {num}, {TL} мс', False
    except Exception as e:
        return f'Ошибка исполнения на тесте {num}: ' + type(e).__name__ + ', 0 мс', False
    
    else:
        
        correct_answer = open(test[:-3] + '.out').read().strip()
        if result == correct_answer:
            return f'Тест {num} успешно пройден, {int(1000* (end - begin))} мс', True
        else:
            return f'''Неправильный ответ на тесте {num}, {int(1000* (end - begin))} мс
Правильный ответ: {formats(correct_answer)}
Вывод программы: {formats(result)}''', False



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
     
        
    def run(self):
        
        self.logBox.setText('')
        begin = time.time()
        
        path = self.testdir.text() + '\\'
        fname = self.choosefile.text()
        print(os.listdir(path))
        
        self.i = 0
        self.successful = 0
        self.time_limit = int(self.TL.text())
    
        for test in os.listdir(path):
            if test.endswith('.in'):
                self.i += 1
                
                results = check(path + test, fname, self.i, self.time_limit)
                res = results[0]
                self.successful += results[1]

                text = self.logBox.toPlainText()
                self.logBox.append('\n' + f'{int(1000 * (time.time() - begin))}' + ' ' + res + '\n')
                QApplication.processEvents()

        
        text = self.logBox.toPlainText()
        self.logBox.append('\n' + f'{int(1000 * (time.time() - begin))}' + ' ' + 'Активные задачи выполнены')
        
        self.resBox.setText(f'''Вердикт тестирования:
Пройдено {self.i} тестов за {int(1000 * (time.time() - begin))} мс, успешно {self.successful}
Среднее время выполнения теста - {int(1000 * (time.time() - begin) / self.i)} мс''')

app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())

