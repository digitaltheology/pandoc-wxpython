import subprocess
import wx
import os


class MainPanel(wx.Panel):
    # TODO - this needs to cater for all possible input formats the app can handle
    # TODO - set up Preferences... dialog

    def __init__(self, parent):
        '''
        Draws the main panel of the main Trinverter window;
        lays out all controls,
        sets up event managers
        '''
        wx.Panel.__init__(self, parent)

        # Variables for this class
        self.fromFileTypes = ['html', 'markdown']
        self.toFileTypes = ['html', 'markdown', 'odt', 'docx']

        self.defaultFromFileType = "markdown"
        self.defaultToFileType = "odt"
        self.defaultConversions = {"markdown":"odt", "html":"odt"}

        self.extensionByType = {"markdown":"md", "html":"html", "odt":"odt", "docx":"docx"}

        self.inputDirectory = ""
        self.inputFilename = ""
        self.outputFilename = ""
        self.outputDirectory = ""
        self.inputBrowseExtension = ""
        self.outputBrowseExtension = ""
 
        # Use some sizers to see layout options
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.topleftsizer = wx.BoxSizer(wx.VERTICAL)
        self.toprightsizer = wx.BoxSizer(wx.VERTICAL)
        self.infilesizer = wx.BoxSizer(wx.HORIZONTAL)
        self.outfilesizer = wx.BoxSizer(wx.HORIZONTAL)
        self.actionsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Initialise the controls
        
        self.leftrb = wx.RadioBox(self, label=' Input File Format ', choices=self.fromFileTypes, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.rightrb = wx.RadioBox(self, label=' Output File Format ', choices=self.toFileTypes, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.leftrb.SetStringSelection(self.defaultFromFileType)
        self.rightrb.SetStringSelection(self.defaultToFileType)
        self.rightrb.EnableItem(self.rightrb.FindString(self.leftrb.GetStringSelection()), False)  # Disable the output file type radiobutton which is the same as the selected input file type
        self.infilelbl = wx.StaticText(self, label=' Input file ', size=(80, -1))
        self.infilectrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.outfilelbl = wx.StaticText(self, label=' Output file ', size=(80, -1))
        self.outfilectrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.infilebrowse = wx.Button(self, -1, "Browse...")
        self.outfilebrowse = wx.Button(self, -1, "Browse...")
        self.actionconvert = wx.Button(self, -1, "Convert")
        self.actionexit = wx.Button(self, -1, "Quit") 

        # Add the controls to the correct sizers
        self.topleftsizer.Add(self.leftrb, 1, wx.EXPAND)
        self.toprightsizer.Add(self.rightrb, 1, wx.EXPAND)
        self.infilesizer.Add(self.infilelbl, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        self.infilesizer.Add(self.infilectrl, 1, wx.EXPAND)
        self.infilesizer.Add(self.infilebrowse, 0, wx.EXPAND)
        self.outfilesizer.Add(self.outfilelbl, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.outfilesizer.Add(self.outfilectrl, 1, wx.EXPAND)
        self.outfilesizer.Add(self.outfilebrowse, 0, wx.EXPAND)
        self.actionsizer.Add(self.actionconvert, 0, wx.CENTER)
        self.actionsizer.Add(self.actionexit, 0, wx.CENTER)

        # Add the sizers together
        self.topsizer.Add(self.topleftsizer, 1, wx.EXPAND)
        self.topsizer.Add(self.toprightsizer, 1, wx.EXPAND)
        self.mainsizer.Add(self.topsizer, 1, wx.EXPAND)
        self.mainsizer.Add(self.infilesizer, 0, wx.EXPAND)
        self.mainsizer.Add(self.outfilesizer, 0, wx.EXPAND)
        self.mainsizer.Add(self.actionsizer, 0, wx.CENTER)

        #Layout the sizers
        self.SetSizer(self.mainsizer)
        self.Layout()
        
        # Events
        self.Bind(wx.EVT_RADIOBOX, self.setInputFileType, self.leftrb)
        self.Bind(wx.EVT_RADIOBOX, self.setOutputFileType, self.rightrb)
        self.Bind(wx.EVT_BUTTON, self.BrowseInputFile, self.infilebrowse)
        self.Bind(wx.EVT_BUTTON, self.BrowseOutputFile, self.outfilebrowse)
        self.Bind(wx.EVT_BUTTON, self.exitTheApp, self.actionexit)
        self.Bind(wx.EVT_BUTTON, self.doTheConversion, self.actionconvert)

        # Run setup routines
        self.extensionSetting()


    # Event handlers

    def setInputFileType(self, event):
        '''
        Set the input file extension, based on the selection on the lh radiobutton
        and do sanity correction on output file type selection radiobox
        '''
        for i in range (0, len(self.toFileTypes)):
            self.rightrb.EnableItem(i, True)    # Enable all buttons in the output file type radiolist
        if self.leftrb.GetStringSelection() == self.rightrb.GetStringSelection():     # If the selected input file type is same as currently selected output file type
            self.rightrb.SetStringSelection(self.defaultConversions[self.leftrb.GetStringSelection()])     # Set up the output file type radiobutton for the default setting
        self.rightrb.EnableItem(self.rightrb.FindString(self.leftrb.GetStringSelection()), False)  # Now disable the output file type radiobutton which is the same as the selected file type
        self.inputFileScrub()       # Scrub the input file information
        self.outputFileScrub()      # Scrub the output file information
        self.extensionSetting()     # Set the input and output file extensions, based on the values of left and right radioboxes
 
    def setOutputFileType(self, event):
        '''Set the output file extension, based on the selection of the rh radiobox'''
        self.outputFileScrub()      # Scrub the output file information
        self.extensionSetting()     # Set the input and output file extensions, based on the values of left and right radioboxes
        if self.inputFilename != '':
            self.smartOutputFilename()  # Guess the output filename by the input filename, if it exists

    def BrowseInputFile(self, event):
        '''Create a file open dialog to set the path and filename of the input file'''

        dlg = wx.FileDialog(self, "Choose the input file", defaultFile=self.inputFilename, wildcard="*." + self.inputBrowseExtension, style=wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
                self.inputFilename = dlg.GetFilename()
                self.inputDirectory = dlg.GetDirectory()
                self.infilectrl.SetValue(self.inputFilename)
                self.smartOutputFilename()
        dlg.Destroy()

    def BrowseOutputFile(self, event):
        '''Create a file open dialog to set the path and filename of the output file'''

        dlg = wx.FileDialog(self, "Choose the output file", defaultFile=self.outputFilename, wildcard="*."+self.outputBrowseExtension, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
                self.outputFilename = dlg.GetFilename()
                self.outputDirectory = dlg.GetDirectory()
                self.outfilectrl.SetValue(self.outputFilename)
        dlg.Destroy()

    def doTheConversion(self, event):
        '''Combine the information from the panel to execute a pandoc command.'''

        # First, some checks
        if self.inputFilename == "":
            dlg = wx.MessageDialog(None, 'You have not selected an input file.', 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            return

        if self.outputFilename == "":
            dlg = wx.MessageDialog(None, 'You have not selected an output file.', 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            return

        if os.path.isfile(os.path.join(self.outputDirectory, self.outputFilename)) == True:
            dlg = wx.MessageDialog(None, 'Warning: a file named \''+self.outputFilename+'\'\nalready exists. Do you wish to overwrite it?', 'Warning', wx.YES_NO | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() != wx.ID_YES:
                return

        # OK, it looks as if we're ready to convert
        try:
            self.pandocProcess = subprocess.check_call(['pandoc', '-f', self.leftrb.GetStringSelection(), '-t', self.rightrb.GetStringSelection(), '-o', os.path.join(self.outputDirectory, self.outputFilename), os.path.join(self.inputDirectory, self.inputFilename)])
        except subprocess.CalledProcessError as self.pandoc_execute_exception:
            dlg = wx.MessageDialog(None, 'Pandoc encountered an error performing the conversion.\nThe error code was: '+ str(self.pandoc_execute_exception.returncode), 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
        else:
            dlg = wx.MessageDialog(None, 'Pandoc ran successfully. File converted.', 'Info', wx.OK)
            dlg.ShowModal()
            self.inputFileScrub()
            self.outputFileScrub()


    def exitTheApp(self, event):
            self.Close()
            frame.Close()	
            print("Goodbye!")


    # Miscellaneous Functions

    def extensionSetting(self):
        '''Sets the from- and to- file extensions by reading values of the left- and right- radiolists'''
        self.inputBrowseExtension = self.extensionByType[self.leftrb.GetStringSelection()]
        self.outputBrowseExtension = self.extensionByType[self.rightrb.GetStringSelection()]

    def inputFileScrub(self):
        '''Clears the input filename and clears the input filename TextCtrl'''
        self.inputFilename = ''
        self.inputDirectory = ''
        self.infilectrl.SetValue('')

    def outputFileScrub(self):
        '''Clears the output filename and clears the output filename TextCtrl'''
        self.outputFilename = ''
        self.outputDirectory = ''
        self.outfilectrl.SetValue('')

    def smartOutputFilename(self):
        '''
        Sets the most plausible outputFilename and outputDirectory based on the settings of the
        inputFilename, inputDirectory and outputBrowseExtension
        '''
        self.outputFilename = os.path.splitext(self.inputFilename)[0]+'.'+self.outputBrowseExtension
        self.outputDirectory = self.inputDirectory
        self.outfilectrl.SetValue(self.outputFilename)

# The main program logic

if __name__ == "__main__":

    app = wx.App(False)
    frame = wx.Frame(None, title="Trinverter: The Trinity College file format converter", size=(500,300))
    panel = MainPanel(frame)
    frame.Center()
    frame.Show()
    app.MainLoop()

