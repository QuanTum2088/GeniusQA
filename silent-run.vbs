Set objShell = CreateObject("WScript.Shell")
cmdLine = ""
For Each arg In WScript.Arguments
    If InStr(arg, " ") > 0 Then
        cmdLine = cmdLine & """" & arg & """ "
    Else
        cmdLine = cmdLine & arg & " "
    End If
Next
objShell.Run "cmd /c " & Trim(cmdLine), 0, False
