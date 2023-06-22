
#!/usr/bin/python3

import argparse
import paho.mqtt.publish as publish

# Main start
if __name__== "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("-b", type=str, action="store", dest="broker", help="Broker IP Addr", default="127.0.0.1")
   parser.add_argument("-p", type=int, action="store", dest="port", help="Broker Port", default=1883)
   parser.add_argument("-u", type=str, action="store", dest="username", help="Auth User Name", default=None)
   parser.add_argument("-w", type=str, action="store", dest="password", help="Auth Password", default=None)
   parser.add_argument("-t", type=str, action="store", dest="topic", help="Topic", default=None)
   parser.add_argument("-m", type=int, action="store", dest="message", help="Message to Send", default=None)
   args = parser.parse_args()

   if args.topic == None or args.message == None:
      print("Topic / message need to be specified")
      exit(0)

   try:
      publish.single(args.topic, args.message, hostname=args.broker, port=args.port)
   except:
      pass
