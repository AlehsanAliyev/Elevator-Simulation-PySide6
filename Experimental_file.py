import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QHBoxLayout, QButtonGroup, QWidget, QDockWidget, QGridLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QObject, QSize
from PySide6.QtGui import QPixmap
from PySide6 import QtGui
import Pygame_file

loader = QUiLoader()


class UserInterface(QObject):
    def __init__(self):
        super(UserInterface, self).__init__()
        self.ui = loader.load("Elevator_Interface_updated.ui", None)


        self.info_dialog = InfoDialog()

        self.ui.setWindowTitle("Elevatorus")
        self.ui.setCurrentIndex(0)
        self.ui.start_button.clicked.connect(self.nextus)
        self.ui.simulate_button.clicked.connect(self.simulate_button_clicked)

        self.ui.return_in_param.clicked.connect(self.previous)
        self.ui.return_in_simul.clicked.connect(self.previous)

        self.ui.info_button.clicked.connect(self.info_button_clicked)

        self.elev_but_frame_layout = QVBoxLayout()

        self.elevator_buttons = QButtonGroup()

        self.close_doors = ElevatorButton('', 'close_doors.png')
        self.close_doors.clicked.connect(self.close_clicked)

        self.elevator_simulator = Pygame_file.PygameWindow()
        self.elevator_category = None

    def create_elevator_buttons(self):
        number_of_floor = int(self.ui.lieedit_floor.text())
        first_vert = QVBoxLayout()
        second_vert = QVBoxLayout()

        for i in range(number_of_floor):

            my_elev_button = ElevatorButton(str(i + 1))

            self.elevator_buttons.addButton(my_elev_button)
            if i < number_of_floor//2:
                first_vert.addWidget(my_elev_button)
            else:
                second_vert.addWidget(my_elev_button)

        two_vert = QHBoxLayout()
        two_vert.addLayout(first_vert)
        two_vert.addLayout(second_vert)

        open_door = ElevatorButton('', 'open_doors.png')

        open_close_layout = QHBoxLayout()
        open_close_layout.addWidget(open_door)
        open_close_layout.addWidget(self.close_doors)

        self.elev_but_frame_layout.addLayout(two_vert)
        self.elev_but_frame_layout.addLayout(open_close_layout)

        # self.elev_but_frane_layout.addWidget(self.close_doors)

        self.ui.elev_but_frame.setLayout(self.elev_but_frame_layout)

    def simulate_button_clicked(self):
        self.elevator_category = self.get_elevator_category()
        self.category_design()
        number_of_floor = int(self.ui.lieedit_floor.text())
        self.nextus()
        self.create_elevator_buttons()
        self.elevator_simulator.activate(number_of_floor)

    def get_elevator_category(self) -> str:
        return self.ui.combobox_cat.currentText()

    def category_design(self):
        if self.elevator_category == "Modern Elevator(Multiple click)":
            self.ui.elev_but_frame.setStyleSheet("*{background-color: yellow;}")
            #self.ui.pygame_dock.setEnabled(False)
            '''print(isinstance(self.ui.pygame_dock, QDockWidget))
            print(self.ui.pygame_dock.isVisible())
            self.ui.pygame_dock.deleteLater()
            print(self.ui.pygame_dock.isVisible())
            print(isinstance(self.ui.pygame_dock, QDockWidget))
            print("HelloWorld")'''
            # self.ui.removeWidget(self.ui.pygame_dock)

            # print(type(self.ui))
            # print(type(self.ui.pygame_dock))
            # print(self.ui.SimulationPage.layout())
            simul_layout = QGridLayout()
            simul_layout.addWidget(self.ui.elev_but_frame, 1, 2, 1, 1)
            simul_layout.addWidget(self.ui.pygame_dock,1, 2, 2 )
            self.ui.SimulationPage.setLayout(simul_layout)

            # self.ui.pygame_dock.hide()
            # self.ui.pygame_dock.deleteLater()
            # print(type(self.ui.pygame_dock))
            # self.ui.pygame_dock.setStyleSheet("*{background-color: red;}")
            # self.ui.SimulationPage.removeWidget(self.ui.pygame_dock)



        elif self.elevator_category == "Azerbaijani Mode":
            pass
        elif self.elevator_category == "Simple Elevator":
            pass


    def close_clicked(self):
        destined_floor = int(self.elevator_buttons.checkedButton().text())

        self.elevator_simulator.define_destination_floor(destined_floor)
        print(destined_floor)
        return destined_floor

    def show(self):
        self.ui.show()

    def previous(self):
        self.ui.setCurrentIndex(self.ui.currentIndex() - 1)

    def nextus(self):
        self.ui.setCurrentIndex(self.ui.currentIndex() + 1)

    def info_button_clicked(self):
        self.info_dialog.show()


class InfoDialog(QObject):
    def __init__(self):
        super(InfoDialog, self).__init__()
        self.dialog = loader.load("Info_window_gui.ui", None)

        self.dialog.simple_button.clicked.connect(self.simple_writer)
        self.dialog.modern_button.clicked.connect(self.modern_writer)
        self.dialog.azer_button.clicked.connect(self.azer_writer)

    def show(self):
        self.dialog.show()

    def simple_writer(self):
        self.dialog.info_label.setText("Simle Elevator: only 1 call in lift,\n"
                                       "No randomly crashing")

    def modern_writer(self):
        self.dialog.info_label.setText("Modern Elevator: several calls in lift,\n"
                                       "Just imagine hotel lift or other modern one")

    def azer_writer(self):
        self.dialog.info_label.setText("Azerbaijan Elevator: Don't expect quality :)")


class ElevatorButton(QPushButton):

    _simple_stylesheet = '''QPushButton{
                           background-color: grey;
                           border-style: outset;
                           border-width: 6px;
                           border-radius: 10px;
                           border-color: beige;
                           font: bold 14px;
                           padding: 6px;
                           }
                           QPushButton:checked {
                           background-color: rgb(224, 0, 0);
                           border-style: inset;
                           border-color: red;
                           }'''

    _open_close_stylesheet = '''QPushButton{
                           background-color: grey;
                           border-style: outset;
                           border-width: 6px;
                           border-radius: 10px;
                           border-color: beige;
                           font: bold 14px;
                           padding: 6px;
                           }
                           QPushButton:pressed {
                           background-color: rgb(224, 0, 0);
                           border-style: inset;
                           border-color: red;
                           }'''

    def __init__(self, x: str, image=None):
        super(ElevatorButton, self).__init__()
        self.setFixedSize(QSize(50, 50))
        if x != ' ':
            self.setText(x)
            self.setCheckable(True)
            self.setStyleSheet(self._simple_stylesheet)
        if image:
            my_pixmap = QPixmap(image)
            self.setIcon(my_pixmap)
            self.setStyleSheet(self._open_close_stylesheet)


app = QApplication(sys.argv)
window = UserInterface()

window.show()
app.exec()
