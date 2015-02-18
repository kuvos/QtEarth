# First, and before importing any Enthought packages, set the ETS_TOOLKIT
# environment variable to qt4, to tell Traits that we will use Qt.
import os
os.environ['ETS_TOOLKIT'] = 'qt4'

# To be able to use PySide or PyQt4 and not run in conflicts with traits,
# we need to import QtGui and QtCore from pyface.qt
from pyface.qt import QtGui, QtCore
from pyface.qt.QtCore import SIGNAL
from pyface.qt.QtWebKit import QWebPluginFactory, QWebView, QWebSettings
# Alternatively, you can bypass this line, but you need to make sure that
# the following lines are executed before the import of PyQT:
#   import sip
#   sip.setapi('QString', 2)

from traits.api import HasTraits, Instance, on_trait_change, \
    Int, Dict
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor
        


import QtEarthGui_package as EG


GlobalQtEarthAbsPath = '/media/DATA/PYTHON/EARTH/eart_v0/'
GlobalQtEarthAbsPath = '../'



################################################################################
#The actual visualization
class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())


        
        
    @on_trait_change('scene.activated')
    def update_plot(self):
        
        # This function is called when the view is opened. We don't
        # populate the scene when the view is not yet open, as some
        # VTK features require a GLContext.

        # We can do normal mlab calls on the embedded scene.
        fig = self.scene.mlab.gcf()
        fig.scene.disable_render = True
        fig.scene.background = (0.99,0.99,0.99)
        fig.scene.disable_render  = False
        
    # the layout of the dialog screated
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                resizable=True # We need this to resize with the parent widget
                )


################################################################################
# The QWidget containing the visualization, this is pure PyQt4 code.
class MayaviQWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.visualization = Visualization()

        # If you want to debug, beware that you need to remove the Qt
        # input hook.
        #QtCore.pyqtRemoveInputHook()
        #import pdb ; pdb.set_trace()
        #QtCore.pyqtRestoreInputHook()

        # The edit_traits call will generate the widget to embed.
        self.ui = self.visualization.edit_traits(parent=self,
                                                 kind='subpanel').control
                                                 
#        print(self.visualization.earth)
        layout.addWidget(self.ui)
        self.ui.setParent(self)

class MainWindow(QtGui.QMainWindow):
    def __init__(self,app=None,splash=None):
        super (MainWindow, self).__init__ ()
        

        self.nextsplash("Chargement de l'interface .... ",app,splash)
        self.QtEarthAbsPath = GlobalQtEarthAbsPath
        self.infoModules=''
        
        
        #    creation de l'objet contenant la figure mayavi
        self.nextsplash("Chargement des objets mayavi .... ",app,splash)
        container = QtGui.QWidget()
        layout = QtGui.QGridLayout(container)
        mayavi_widget = MayaviQWidget(container)
        self.setCentralWidget(container)
        layout.addWidget(mayavi_widget, 0, 1)
        container.show()
        
        
        self.nextsplash("Chargement des modules obligatoires .... ",app,splash)
#        from modQtEarth_Profil import profile
#        self.objProfile = profile()
        
        
        
        
        dicoWidget={}
        self.dicoWidget=dicoWidget
        dicoWidget['visbleListeWidget'] = None
        dicoWidget['colorisationWidget'] = None
        dicoWidget['profilWidget'] = None
        
        
        
#        self.dicoWidget['visbleListeWidget'].addObjet(obj=self.objProfile,
#                    name="Profile",
#                    state=QtCore.Qt.Unchecked,
#                    opacity=0.5)
                    
                    
        
        
        self.moduleToLoad=[]
        self.moduleLoaded=[]
        self.moduleDico={}
        
        
        #    creation des objets de controle
        self.nextsplash("creation des objets de controle",app,splash)
        self.createToolBar()
        self.createDockWindows()
        
     
    def nextsplash(self,message,app,splash):
        if app == None or splash == None:
            return
        
        splash.showMessage(message)
        app.processEvents()
        
    def addModuleListe(self,listeModule,app=None,splash=None):
        if app == None:
            app = QtGui.QApplication.instance()
        if splash == None:
            pixmap = QtGui.QPixmap("splash.png")
            splash = QtGui.QSplashScreen(pixmap)
            splash.show()
        
        self.nextsplash("Chargement des modules .... ",app,splash)
        
        for mo in listeModule:
            self.nextsplash("Loaded modules : "+mo,app,splash)
            self.addModule(mo,app=app,splash=splash)
        
            # ici on ajoute le globe au module de profil click pour l'affichage des images
#            if mo =="modQtEarth_Globe":
#                globe=self.moduleDico['modQtEarth_Globe']['listeObj'][0]
#                self.dicoWidget['profilWidget'].setGlobe(globe)
        
        
        
    def addModule(self,nom,app=None,splash=None):
        self.moduleToLoad.append(nom)

        
#        try:
#        exec("import "+nom+" as module")
#        exec("from modules."+nom+" import "+nom+" as module")
        exec("from modules import "+nom+" as module")
        print("Chargement de : "+nom)
        
        dicoModule = module.getModule(self.moduleDico,QtEarthAbsPath = '../',
                                      app=app,splash=splash,interface=self)
        self.addModuleDico(dicoModule,nom=nom)
        
        if dicoModule['info']['addToInfo']:
            texte = dicoModule['info']['info']
            self.infoModules = self.infoModules+'<h2> Module : '+nom+'</h2>'+texte

#        except:
#            print('#### IMPOSSIBLE DE CHARGER LE MODULE : '+nom)
        
        
        
    def addModuleDico(self,dicoModule,nom="new_module"):

        for i in dicoModule['addToGui']:
            if i['addToVisible']:
                if self.dicoWidget['visbleListeWidget']==None:
                    self.dicoWidget['visbleListeWidget'] = EG.visibleListeWidget()
                    self.dicoWidget['dock1'].setWidget(self.dicoWidget['visbleListeWidget'])
                self.dicoWidget['visbleListeWidget'].addObjet(obj=i['obj'],**i['paramVisible'])
                
            if i['addToColor']:
                if self.dicoWidget['colorisationWidget']==None:
                    self.dicoWidget['colorisationWidget'] = EG.widgetColormapSaturation()
                    self.dicoWidget['dock2'].setWidget(self.dicoWidget['colorisationWidget'])
                self.dicoWidget['colorisationWidget'].addObjet(obj=i['obj'],**i['paramColor'])

        for i in dicoModule['listePage']:
            self.toolBoxL.addItem(i,i.icone,i.name)
        
        self.moduleLoaded.append(nom)
        self.moduleDico[nom]=dicoModule
                
                
        if dicoModule['addProfilWidget'] and self.dicoWidget['profilWidget']==None:
            objProfile = dicoModule['listeObj'][0]
            self.dicoWidget['profilWidget'] = EG.widgetProfileCoord(obj=objProfile,QtEarthAbsPath=self.QtEarthAbsPath)
            self.dicoWidget['profilWidget'].onOptimViewClicked.connect(self.setRoiProfil)
            self.dicoWidget['dock3'].setWidget(self.dicoWidget['profilWidget'])
                
    def createToolBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Fichier')
        
        
# [TODO] commente pour eviter eleves. A finir

        exitAction = QtGui.QAction(QtGui.QIcon(self.QtEarthAbsPath+'ICONES/exit.png'), 
                                   'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        
        
        infoMenu = menubar.addMenu('&A propos')
        infoAction = QtGui.QAction(QtGui.QIcon(self.QtEarthAbsPath+'ICONES/exit.png'), 
                                   'References', self)
        infoAction.triggered.connect(self.dispInfo)
        
        infoLogAction = QtGui.QAction(QtGui.QIcon(self.QtEarthAbsPath+'ICONES/exit.png'), 
                                   'A propos de QtEarth', self)
        infoLogAction.triggered.connect(self.dispInfoLog)
        
        

        infoMenu.addAction(infoAction)
        infoMenu.addAction(infoLogAction)
        
    def dispInfoLog(self):
        print("info logiciel")
        self.dispInfoWindows("toto")
        
    def dispInfo(self):
        print("info donnees")
        self.dispInfoWindows("tat")
        
    def dispInfoWindows(self,html):
        print(html)
        self.view = QWebView()
        self.view.setHtml (self.infoModules)
        self.view.show()
#        view.
    def createDockWindows(self):
        
#        creation du doc de gauche et de droite
        dockL = QtGui.QDockWidget("Proprietes d'objets", self)
        dockL.setMinimumWidth(260)
        dockL.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockL)

        
#        creation de la boite a onglets contenant les controles des objets      
        self.toolBoxL = QtGui.QToolBox(dockL)
        self.toolBoxL.setFrameShape(QtGui.QFrame.Box)

#        creation du widget contenant tous le panel de controle de gauche
        MainBarreL = QtGui.QWidget()
        MainBarreL.setLayout(QtGui.QVBoxLayout())       
#        MainBarreL.layout().addWidget(Visible)
        MainBarreL.layout().setContentsMargins(0,0,0,0)
        MainBarreL.layout().addWidget(self.toolBoxL)
        dockL.setWidget(MainBarreL)
        
        
        
        
        dockR = QtGui.QDockWidget("Visibilite objet", self)
        dockR.setMinimumWidth(260)
        dockR.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockR)
        dockR.setWidget(self.dicoWidget['visbleListeWidget'])
        
        
        
#        creation du controleur de colorisation
#        liste des objet a colorisation controlable
#        mettre cette liste ici pour pouvoir modifier interface
        dockR2 = QtGui.QDockWidget("Colorisation objet", self)
        dockR2.setMinimumWidth(260)
        dockR2.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockR2)
        dockR2.setWidget(self.dicoWidget['colorisationWidget'])
        
        
        
#        creation du controleur de profil
#        mettre cette liste ici pour pouvoir modifier interface
        dockR3 = QtGui.QDockWidget("Coordonnees du profil", self)
        dockR3.setMinimumWidth(260)
        dockR3.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockR3)
        dockR3.setWidget(self.dicoWidget['profilWidget'])
        
        self.dicoWidget['dock1']=dockR
        self.dicoWidget['dock2']=dockR2
        self.dicoWidget['dock3']=dockR3

    def setRoiProfil(self,checkState):
        # il faut defiltrer les seismes quoi qu'il arrive
        
        for k in self.moduleDico.keys():
            dico=self.moduleDico[k]
            for obj in dico['listeObj']:
                obj.defiltre_profil()
                
        if checkState!=0:
            for dicoNom in self.moduleDico.keys():
                dico = self.moduleDico[dicoNom]
                for obj in dico['listeObj']:
                    obj.filtre_profil(self.dicoWidget['profilWidget'].obj)
                    
                for dicoObj in dico['addToGui']:
                    print(dicoNom)
                    if dicoObj['visibleOnRoi']==True:
                        dicoObj['obj'].visible(True)
                    elif dicoObj['visibleOnRoi']==False:
#                        rrr
                        dicoObj['obj'].visible(False)
                    else:
                        pass
if __name__ == "__main__":
    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QtGui.QApplication.instance()
    pixmap = QtGui.QPixmap("splash.png")
    splash = QtGui.QSplashScreen(pixmap)
    splash.show()
    
    
    listeModulesToLoad = [
        'modQtEarth_Globe',
        'modQtEarth_GlobeImage',
        'modQtEarth_Coast',
        'modQtEarth_Reperes',
        'modQtEarth_ProfilTrace',
        'modQtEarth_Profil',
        'modQtEarth_TomoBlob',
#        'modQtEarth_Tomo',
        'modQtEarth_Seisme',
        'modQtEarth_GPS',
        'modQtEarth_Topo3D',
#        'modQtEarth_Lithosphere',
        'modQtEarth_PaleoGeo',
        'modQtEarth_Preset'
        ]


    window = MainWindow(app=app,splash=splash)
    window.addModuleListe(listeModulesToLoad,app=app,splash=splash)
    splash.showMessage("Finalisation")
    app.processEvents()
    window.show()
    splash.destroy()
    app.exec_()
