import sys
from PyQt6.QtWidgets import QApplication
from main_classes import SplashScreen, MainWindow

def main():
    app = QApplication(sys.argv)

    # Mostrar la pantalla de carga
    splash = SplashScreen()
    splash.show()

    # Crear la ventana principal pero no la mostramos aún
    main_window = MainWindow()

    def on_splash_finished():
        # Mostrar la ventana principal y cerrar la pantalla de carga
        main_window.show()
        splash.close()

    # Conectar la finalización de la pantalla de carga con el inicio de la ventana principal
    splash.finished.connect(on_splash_finished)

    # Ejecutar la aplicación
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
