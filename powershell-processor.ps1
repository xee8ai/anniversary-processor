$scriptPath = split-path -parent $MyInvocation.MyCommand.Definition

cd $scriptPath

py.exe src/anniversary-processor.py powershell
