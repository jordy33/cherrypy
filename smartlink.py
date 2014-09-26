import os, os.path
import random
import sqlite3
import string

import cherrypy

DB_STRING = "my.db"

class StringGenerator(object):
   @cherrypy.expose
   def index(self):
       address=[]
       address.clear()
       conn=sqlite3.connect(DB_STRING)
       c=conn.cursor()
       for x in range (1,11):
           c.execute("SELECT value FROM user_string WHERE session_id=?", [x])
           address.append(c.fetchone()[0])
       html= open('base.html')
       data=html.read()
       data=data.replace("{0}",address[0]).replace("{1}",address[1]).replace("{2}",address[2]).replace("{3}",address[3]).replace("{4}",address[4]).replace("{5}",address[5]).replace("{6}",address[6]).replace("{7}",address[7]).replace("{8}",address[8]).replace("{9}",address[9])
       return data 

class StringGeneratorWebService(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
    def GET(self,parametro,para2):
        conn=sqlite3.connect(DB_STRING)
        c=conn.cursor()
        c.execute("SELECT value FROM user_string WHERE session_id=?", [para2])
        nombre=c.fetchone()[0]
        return nombre

    def POST(self, parametro,para2):
        some_string = parametro
        with sqlite3.connect(DB_STRING) as c:
            c.execute("INSERT OR IGNORE INTO user_string VALUES (?, ?)",
                      [para2, some_string])
            c.execute("UPDATE user_string SET value=? WHERE session_id=?",
                      [some_string, para2])
        return some_string 

    def PUT(self, another_string):
        with sqlite3.connect(DB_STRING) as c:
            c.execute("UPDATE user_string SET value=? WHERE session_id=?",
                      [another_string, 1])

    def DELETE(self):
        with sqlite3.connect(DB_STRING) as c:
            c.execute("DELETE FROM user_string WHERE session_id=?",
                      [1])

def setup_database():
    """
    Create the `user_string` table in the database
    on server startup
    """
    conn=sqlite3.connect(DB_STRING)
    c=conn.cursor()
    c.execute("CREATE TABLE if not exists user_string (session_id integer primary key, value)")
    #with sqlite3.connect(DB_STRING) as con:
    #    con.execute(v"CREATE TABLE if not exists user_string (session_id integer primary key, value)")

def cleanup_database():
    """
    Destroy the `user_string` table from the database
    on server shutdown.
    """
   # with sqlite3.connect(DB_STRING) as con:
   #     con.execute("DROP TABLE user_string")

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/generator': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

    cherrypy.engine.subscribe('start', setup_database)
    cherrypy.engine.subscribe('stop', cleanup_database)
    cherrypy.log.access_file = None
    webapp = StringGenerator()
    webapp.generator = StringGeneratorWebService()
    cherrypy.config.update({ "environment": "embedded" })
    cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': 80}) 
    cherrypy.quickstart(webapp, '/', conf)

