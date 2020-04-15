from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys

def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200,200,300,300) 
    win.setWindowTitle("My first window!") 
    
    label = QLabel(win)
    label.setText("my first label")
    label.move(50, 50)  

    win.show()
    sys.exit(app.exec_())

main()  # make sure to call the function
class Ui_MainWindow(object):
	...
	def show_popup(self):
		msg = QMessageBox()
		msg.setWindowTitle("Tutorial on PyQt5")
		msg.setText("This is the main text!")
		msg.setIcon(QMessageBox.Question)
		msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Retry|QMessageBox.Ignore)
		msg.setDefaultButton(QMessageBox.Retry)
		msg.setInformativeText("informative text, ya!")

		msg.setDetailedText("details")

		msg.buttonClicked.connect(self.popup_button)

	def popup_button(self, i):
		print(i.text())