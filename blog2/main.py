import os
import re
import time
from string import letters
import jinja2
import webapp2



from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

        
def render_post(response, post):
    response.out.write('<b>' + post.title + '</b><br>')
    response.out.write(post.blogpost)


class MainPage(Handler):
    def get(self):
        self.write('Welcome to this blog written in python! To view the main blog page go to "\\blog".') 
        self.write("<p>")
        self.write('To submit new blog post go to "\submitpost". Upon clicking submit the new blog post will be shown!')


def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Entry(db.Model):
    title= db.StringProperty(required=True)
    blogpost =  db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now =True)
    
    def render(self):
        self._render_text= self.blogpost.replace("\n" , '<br>')
        return render_str("post.html", p=self)


class BlogMain(Handler):
    def get(self):
        posts= db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC limit 8")
        self.render('front.html', posts = posts)

class BlogPost(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Entry', int(post_id), parent = blog_key())
        post = db.get(key)
        if not post:
            self.error(404)
            return
        self.render("permalink.html", post = post)

class submitHandler(Handler):       
    def get(self):
        self.render("newpost.html")
    
    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")
        
        if blogpost and title:
            p= Entry(parent = blog_key(),title=title, blogpost=blogpost)
            p.put()          
            #time.sleep(1) # sleep for 1 second
            self.redirect('/blog/%s' % str(p.key().id()))         
        else :
            error = "we need both a title and content"
            self.render("newpost.html",title=title, blogpost=blogpost, error=error)
                       

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogMain),
                               ('/blog/submitpost', submitHandler),
                               ('/blog/([0-9]+)', BlogPost),
                               ],
                               debug=True)
