#!/usr/bin/env python

from SimpleHTTPServer import SimpleHTTPRequestHandler
import BaseHTTPServer
import MySQLdb
import MySQLdb.cursors
import optparse
import time

'''
__author__="See Authors.txt"
__copyright__="David Busby <oneiroi@fedorapeople.org>, Percona Ireland Ltd"
__license__="GNU v3 + section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form."
__dependencies__="MySQLdb, python26-mysqldb (el5) / MySQL-python (el6)"
__description__="Provides a stand alone http service, evaluating wsrep_local_state intended for use with HAProxy"
'''

class opts:
  available_when_donor = 0
  cache_time           = 1
  last_query_time      = 0
  last_query_result    = 0
  being_updated        = False

class clustercheck(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
      ctime = time.time()
      if ((ctime - opts.last_query_time) > opts.cache_time) and opts.being_updated == False:
        #cache expired
        opts.being_updated   = True
        opts.last_query_time = ctime
       
        try:
          conn = MySQLdb.connect(
            read_default_file = '~/.my.cnf',
            host = '127.0.0.1',
            port = 3306,
            db = 'rdba',
            cursorclass = MySQLdb.cursors.DictCursor
          )
        except MySQLdb.OperationalError:
          opts.being_updated   = False #corrects a bug where the flag is never reset on communication failiure
          self.send_response(503)
          self.send_header("Content-type", "text/html")
          self.end_headers()
          self.wfile.write("Connection Failed to Percona XtraDB Cluster Node.")

        curs = conn.cursor()
        curs.execute("SHOW STATUS LIKE 'wsrep_local_state'")
        res = curs.fetchall()
                       
        if len(res) == 0:
          self.send_response(503)
          self.send_header("Content-type", "text/html")
          self.end_headers()
          self.wfile.write("Percona XtraDB Cluster Node state could not be retrieved.")

        elif res[0]['Value'] == 4 or (opts.available_when_donor == 1 and res[0]['Value'] == 2):
          opts.last_query_result = res[0]['Value']
          self.send_response(200)
          self.send_header("Content-type", "text/html")
          self.end_headers()
          self.wfile.write("Percona XtraDB Cluster Node is synced.")

        else:
          opts.last_query_result = res[0]['Value']
          self.send_response(503)
          self.send_header("Content-type", "text/html")
          self.end_headers()
          self.wfile.write("Percona XtraDB Cluster Node is not synced.")
      
        conn.close()
        opts.being_updated = False
      else:
        #use cache result
        if opts.last_query_result == 4 or (opts.available_when_donor == 1 and opts.last_query_result == 2):
          self.send_response(200)
          self.send_header("Content-type", "text/html")
          self.end_headers()
          self.wfile.write("CACHED: Percona XtraDB Cluster Node is synced.")
        else:
          self.send_response(503)
          self.send_header("Content-type", "text/html")
          self.end_headers()
          self.wfile.write("CACHED: Percona XtraDB Cluster Node is not synced.")

if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('-a','--available-when-donor', dest='awd', default=0, help="Available when donor [default: %default]")
  parser.add_option('-c','--cache-time', dest='cache', default=1, help="Cache the last response for N seconds [default: %default]")

  options, args = parser.parse_args()
  opts.available_when_donor = options.awd
  opts.cache_time = options.cache

  server_class = BaseHTTPServer.HTTPServer
  httpd = server_class(('',8000),clustercheck)
  httpd.serve_forever()