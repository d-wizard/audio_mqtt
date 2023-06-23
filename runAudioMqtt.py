# 
# MIT License
# 
# Copyright © 2023 Dan Williams
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
import os
import argparse

THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

EXE_PATH = os.path.join(THIS_SCRIPT_DIR, "AudioMqtt")
MQTT_PUB_PY_SCRIPT_PATH = os.path.join(THIS_SCRIPT_DIR, "mqtt_publisher.py")

parser = argparse.ArgumentParser()
parser.add_argument("-b", type=str, action="store", dest="broker", help="Broker IP Addr", default="127.0.0.1")
parser.add_argument("-p", type=int, action="store", dest="port", help="Broker Port", default=1883)
parser.add_argument("-u", type=str, action="store", dest="username", help="Auth User Name", default=None)
parser.add_argument("-w", type=str, action="store", dest="password", help="Auth Password", default=None)
parser.add_argument("-t", type=str, action="store", dest="topic", help="Topic", default=None)
args = parser.parse_args()

if args.topic == None:
   print("Topic needs to be specified")
   exit(0)

# Use os.system (i.e. don't return unless the exe being called returns)
os.system(EXE_PATH + " " + MQTT_PUB_PY_SCRIPT_PATH + " " + args.broker + " " + str(args.port) + " " + args.topic )