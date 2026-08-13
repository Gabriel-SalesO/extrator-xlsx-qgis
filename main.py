import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject

class ExtratorXlsxPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None

    def initGui(self):
        # Caminho para o ícone do botão (opcional)
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        # Cria o botão na barra de ferramentas
        self.action = QAction(icon, 'Extrair para XLSX', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        
        # Adiciona o botão no menu de Vetor e na barra de ferramentas principal
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu('Extrator XLSX', self.action)

    def unload(self):
        # Remove o botão quando o plugin for desativado
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginVectorMenu('Extrator XLSX', self.action)

    def run(self):
        # SEU CÓDIGO PYTHON ENTRA AQUI
        layer = self.iface.activeLayer()
        
        if not layer:
            self.iface.messageBar().pushMessage("Erro", "Selecione uma camada!", level=2)
            return
            
        # Exemplo simples do processo de extração da camada ativa
        # Insira sua lógica de manipulação e salvamento em .xlsx abaixo:
        self.iface.messageBar().pushMessage("Sucesso", f"Camada {layer.name()} processada!", level=0)
