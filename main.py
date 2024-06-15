from PyQt5.QtWidgets import QApplication
from GUI.main_window import MainWindow
from controller.Main_controller import MainController

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    controller = MainController(main_window)
    main_window.show()
    sys.exit(app.exec_())

