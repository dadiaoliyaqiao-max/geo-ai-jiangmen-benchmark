Option Explicit

Dim args, inputPath, outputPath, wordApp, doc
Set args = WScript.Arguments
If args.Count < 2 Then
  WScript.Echo "Usage: export_word_pdf.vbs input.docx output.pdf"
  WScript.Quit 2
End If

inputPath = args(0)
outputPath = args(1)

On Error Resume Next
Set wordApp = CreateObject("Word.Application")
If Err.Number <> 0 Then
  WScript.Echo "Word start failed: " & Err.Description
  WScript.Quit 3
End If

wordApp.Visible = False
wordApp.DisplayAlerts = 0
Set doc = wordApp.Documents.Open(inputPath, False, True)
If Err.Number <> 0 Then
  WScript.Echo "Open failed: " & Err.Description
  wordApp.Quit
  WScript.Quit 4
End If

doc.ExportAsFixedFormat outputPath, 17
If Err.Number <> 0 Then
  WScript.Echo "Export failed: " & Err.Description
  doc.Close False
  wordApp.Quit
  WScript.Quit 5
End If

doc.Close False
wordApp.Quit
WScript.Echo outputPath
