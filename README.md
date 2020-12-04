Deploying django project Heroku;
Inctruction:
1. Add file requirements.txt with library
2. Add file Procfile
<pre>web: gunicorn yourproject.wsgi --log-file -</pre>
3. Change django settings.py Add <pre>import django_heroku</pre> 
and <pre>django_heroku.settings(locals())</pre>
4. Create app on heroku and execute some commands on terminal:
<pre>heroku login</pre>
<pre>git init</pre>
<pre>heroku git:remote -a appname</pre>
<pre>git push heroku master</pre>
