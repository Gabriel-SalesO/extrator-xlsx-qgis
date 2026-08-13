import os
from pathlib import Path

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import (
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsMessageLog,
    Qgis,
)

# Nome exato da camada que este plugin sempre procura e exporta.
NOME_CAMADA = "PONTO_IP"

# Nome do arquivo final gerado dentro da pasta Downloads.
NOME_ARQUIVO_SAIDA = "PONTO_IP.xlsx"


class ExtratorXlsxPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        self.action = QAction(icon, "Extrair PONTO_IP para XLSX", self.iface.mainWindow())
        self.action.setStatusTip("Exporta a camada PONTO_IP para a pasta Downloads em formato XLSX")
        self.action.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu("Extrator XLSX - PONTO_IP", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginVectorMenu("Extrator XLSX - PONTO_IP", self.action)

    def _obter_pasta_downloads(self) -> str:
        """Retorna o caminho da pasta Downloads do usuario, funcionando em
        Windows, Linux e macOS sem depender de bibliotecas externas."""
        pasta_downloads = os.path.join(str(Path.home()), "Downloads")
        os.makedirs(pasta_downloads, exist_ok=True)
        return pasta_downloads

    def _encontrar_camada_ponto_ip(self):
        """Procura a camada PONTO_IP em todo o projeto, nao apenas na
        camada ativa. Isso evita erro caso o usuario tenha selecionado
        outra camada por engano antes de clicar no botao."""
        camadas = QgsProject.instance().mapLayersByName(NOME_CAMADA)
        if not camadas:
            return None
        return camadas[0]

    def run(self):
        layer = self._encontrar_camada_ponto_ip()

        if layer is None:
            self.iface.messageBar().pushMessage(
                "Erro",
                f"Camada '{NOME_CAMADA}' nao foi encontrada no projeto. "
                f"Verifique se ela esta carregada e com este nome exato.",
                level=Qgis.Critical,
            )
            return

        if not isinstance(layer, QgsVectorLayer):
            self.iface.messageBar().pushMessage(
                "Erro",
                f"A camada '{NOME_CAMADA}' nao e uma camada vetorial e nao pode ser exportada para XLSX.",
                level=Qgis.Critical,
            )
            return

        if layer.featureCount() == 0:
            resposta = QMessageBox.question(
                self.iface.mainWindow(),
                "Camada vazia",
                f"A camada '{NOME_CAMADA}' nao possui nenhum registro. Deseja exportar mesmo assim?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if resposta == QMessageBox.No:
                return

        pasta_downloads = self._obter_pasta_downloads()
        caminho_saida = os.path.join(pasta_downloads, NOME_ARQUIVO_SAIDA)

        if os.path.exists(caminho_saida):
            resposta = QMessageBox.question(
                self.iface.mainWindow(),
                "Arquivo ja existe",
                f"O arquivo '{NOME_ARQUIVO_SAIDA}' ja existe em Downloads. Deseja sobrescrever?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if resposta == QMessageBox.No:
                return

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "XLSX"
        options.fileEncoding = "UTF-8"

        context = QgsProject.instance().transformContext()

        try:
            erro = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer, caminho_saida, context, options
            )
        except AttributeError:
            # Fallback para versoes mais antigas do QGIS (< 3.20) que
            # nao possuem writeAsVectorFormatV3.
            erro = QgsVectorFileWriter.writeAsVectorFormatV2(
                layer, caminho_saida, context, options
            )

        codigo_erro = erro[0] if isinstance(erro, (tuple, list)) else erro

        if codigo_erro == QgsVectorFileWriter.NoError:
            self.iface.messageBar().pushMessage(
                "Sucesso",
                f"Camada '{NOME_CAMADA}' exportada para {caminho_saida}",
                level=Qgis.Success,
            )
            QgsMessageLog.logMessage(
                f"Exportacao concluida: {caminho_saida}", "Extrator XLSX", Qgis.Info
            )
        else:
            mensagem_erro = erro[1] if isinstance(erro, (tuple, list)) and len(erro) > 1 else str(erro)
            self.iface.messageBar().pushMessage(
                "Erro",
                f"Falha ao exportar a camada: {mensagem_erro}",
                level=Qgis.Critical,
            )
            QgsMessageLog.logMessage(
                f"Erro na exportacao: {mensagem_erro}", "Extrator XLSX", Qgis.Critical
            )
