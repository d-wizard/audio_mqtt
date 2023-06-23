# 
# MIT License
# 
# Copyright © 2022-2023 Dan Williams
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import re
import os
import subprocess
import argparse

THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
THIS_SCRIPT_FILENAME = os.path.split(os.path.realpath(__file__))[1] 

# Helper Functions.
class ProcInfo(object):
   def __init__(self):
      self.pid = None
      self.proc = None
      self.cmds = None

def getAllProcesses():
   retVal = []
   pidIndex = -1
   cmdIndex = -1
   
   psaxOut = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE).communicate()[0]
   psaxOut = psaxOut.decode('utf-8').strip()

   headerLine = psaxOut.split('\n')[0]
   header = re.findall(r'(\S+)', headerLine)
   for i in range(len(header)):
      if header[i] == 'PID':
         pidIndex = i
         break
   
   for i in range(len(header)):
      if header[i] == 'COMMAND':
         cmdIndex = i
         break
   
   if pidIndex == -1 or cmdIndex == -1:
      return retVal

   psaxLines = psaxOut.split('\n')[1:]
   for line in psaxLines:
      newProcess = ProcInfo()
      procInfo = re.findall(r'(\S+)', line)
      
      try:
         newProcess.pid = int(procInfo[pidIndex])
         newProcess.proc = procInfo[cmdIndex]
         newProcess.cmds = procInfo[cmdIndex+1:]
         retVal.append(newProcess)
      except:
         pass

   return retVal

def getProcInfo(procName):
   retVal = []
   allProcesses = getAllProcesses()
   for proc in allProcesses:
      match = False
      if proc.proc == procName:
         match = True
      else:
         try:
            if proc.proc[-len(procName):] == procName:
               match = True
            else:
               extraCheck = os.sep + procName
               if proc.proc[-len(extraCheck):] == extraCheck:
                  match = True
         except:
            pass
            
      if match:
         retVal.append(proc)

   return retVal

# Main start
if __name__== "__main__":
   # Config argparse
   parser = argparse.ArgumentParser()
   pathToScriptCmd = "--pathToScript"
   parser.add_argument(pathToScriptCmd,  type=str, action="store", dest="scriptPath", help="Path to the script to run.", default=None)
   parser.add_argument("--argsToScript", type=str, action="store", dest="args", help="Command line arguments.", default=None)
   args = parser.parse_args()

   if(args.scriptPath == None):
      print("Need to specify path to the script to run.")
      exit(0)

   SCRIPT_PATH = os.path.realpath(args.scriptPath)
   SCRIPT_DIR, SCRIPT_NAME = os.path.split(SCRIPT_PATH)
   ERROR_LOG_PATH = SCRIPT_PATH + '.stderr'

   ARGS = "" if args.args == None else " " + args.args # Add extra space to separate command from args.

   START_CMD = 'python3 ' + SCRIPT_PATH + ARGS + ' 2>> ' + ERROR_LOG_PATH + ' &'

   procInfo = getProcInfo('python3')

   # Check if the script is already running.
   running = False
   for p in procInfo:
      if pathToScriptCmd in p.cmds: # Don't include this process in the check.
         # Found the process running this script right now. Skip past to the next process.
         pass
      else:
         if SCRIPT_NAME in p.cmds:
            running = True
         else:
            for cmd in p.cmds:
               if SCRIPT_NAME in cmd:
                  running = True

   if not running:
      print(START_CMD)
      os.system(START_CMD)
      


   

