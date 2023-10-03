from krita import Krita, Extension, InfoObject
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
import os

def visibleTopLevelNodes(doc):
    for node in doc.topLevelNodes():
        if node.visible():
            yield node


def forFlatGroupLeafs(node, func):
    if node.type() != "grouplayer":
        return

    has_group = False
    for n in node.childNodes():
        if n.type() == "grouplayer":
            forFlatGroupLeafs(n, func)
            has_group = True

    if not has_group:
        Krita.instance().activeDocument().setActiveNode(node)
        func(node)


def forLeafs(node, func):
    if len(node.childNodes()) == 0:
        func(node)
    else:
        for n in node.childNodes():
            forLeafs(n, func)


def addGroupWithSameName(node):
    """
    Adds the node into a group of the same name.

    We do this to maintain the group heirarchy (which is useful in Live2D) and
    to have better naming. In Krita 5.2+ there is an option to not add the
    "Merged" suffix to merged groups, but this works without user intervention.
    """
    Krita.instance().action("create_quick_group").trigger()
    Krita.instance().activeDocument().waitForDone()
    node.parentNode().setName(node.name())


def removeMergedSuffix(node):
    """
    Removes the "Merged" suffix from the node name.
    """
    if node.name().endswith(" Merged"):
        node.setName(node.name()[:-7])


def save_as_psd(node):
    application = Krita.instance()
    window = application.activeWindow()
    currentDoc = application.activeDocument()
    currentView = window.activeView()

    currentView.setVisible()
    application.setActiveDocument(currentDoc)
    currentDoc.setActiveNode(node)
    application.action("edit_copy").trigger()

    newDoc = application.createDocument(
        node.bounds().width(), node.bounds().height(),
        node.name() + ".psd",
        currentDoc.colorModel(),
        currentDoc.colorDepth(),
        currentDoc.colorProfile(),
        currentDoc.resolution()
    )
    window.addView(newDoc)
    application.setActiveDocument(newDoc)
    default_layer = newDoc.topLevelNodes()[0]
    application.action("edit_paste").trigger()
    default_layer.remove()
    Krita.instance().activeDocument().waitForDone()
    newDoc.refreshProjection()

    outfile = os.path.join(os.path.dirname(currentDoc.fileName()),
                           node.name() + ".psd")
    newDoc.saveAs(outfile)
    print(f'Saving {outfile}')
    newDoc.close()

    currentView.setVisible()
    application.setActiveDocument(currentDoc)
    currentDoc.setActiveNode(node)

class Live2DExporterExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)


    def setup(self):
        pass


    def createActions(self, window):
        action = window.createAction("live2d_export",
                                     "Live2D Export",
                                     "tools/scripts")
        action.triggered.connect(self.live2d_export)


    def showErrorWindow(self, message):
        dialog = QDialog()
        dialog.setWindowTitle("Operation Failed")
        layout = QVBoxLayout()
        label = QLabel()
        label.setText(message)
        layout.addWidget(label)
        button = QPushButton("OK")
        button.clicked.connect(lambda: dialog.close())
        layout.addWidget(button)
        dialog.setLayout(layout)
        dialog.exec_()


    def live2d_export(self):
        application = Krita.instance()
        currentDoc = application.activeDocument()

        if currentDoc.modified():
            self.showErrorWindow("Current document has unsaved changes. Aborting operation.")
            return

        # Check for name conflicts.
        node_names = [ n.name() for n in visibleTopLevelNodes(currentDoc) ]
        if len(node_names) != len(set(node_names)):
            self.showErrorWindow("There are multiple top-level layers that share a name. Aborting operation.")


        # Merging whilst editting groups was having issues with what the "activeNode"
        # resolved to. So we iterate multiple times over the node tree.
        for node in visibleTopLevelNodes(currentDoc):
            forFlatGroupLeafs(node, addGroupWithSameName)

        for node in visibleTopLevelNodes(currentDoc):
            forFlatGroupLeafs(node, lambda n: Krita.instance().action("merge_layer").trigger())

        for node in visibleTopLevelNodes(currentDoc):
            forLeafs(node, removeMergedSuffix)

        for node in visibleTopLevelNodes(currentDoc):
            save_as_psd(node)

        # Reopen the document so all changes are lost.
        # Setting the modified flag, prevents autosave/discard changes dialog.
        newDoc = application.openDocument(currentDoc.fileName())
        Krita.instance().activeWindow().addView(newDoc)
        currentDoc.setModified(False)
