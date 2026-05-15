Option Explicit
Dim shell, fso, root, logPath, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
logPath = root & "\START_LOG.txt"

command = "cmd.exe /c " & Chr(34) & _
  "cd /d " & Chr(34) & root & Chr(34) & _
  " && echo Komchi start log > " & Chr(34) & logPath & Chr(34) & _
  " && echo Folder: %CD% >> " & Chr(34) & logPath & Chr(34) & _
  " && echo Time: %DATE% %TIME% >> " & Chr(34) & logPath & Chr(34) & _
  " && if not exist komchi_app.py echo ERROR: komchi_app.py not found >> " & Chr(34) & logPath & Chr(34) & _
  " && where py >> " & Chr(34) & logPath & Chr(34) & " 2>>&1" & _
  " && start \"\" /min py -3 komchi_app.py >> " & Chr(34) & logPath & Chr(34) & " 2>>&1" & _
  Chr(34)

shell.Run command, 0, False
WScript.Sleep 1500
shell.Run "notepad.exe " & Chr(34) & logPath & Chr(34), 1, False
