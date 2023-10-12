-------------------------------------------------------------------
Setting up:
-------------------------------------------------------------------

1. Create a python env
- `python3 -m venv store@3.10.7`

2. Activate the env
- `source store@3.10.7/bin/activate`

3. Go to working directory
- `cd store_system/store`

4. Run `pip3 install -r requirements.txt`

5. Create a file called 'env.json'
- `touch env.json`
- Check the example.env.json format
- This is where you will put the credentials (db, api keys, etc..)

6. Run the server
- `python3 manage.py runserver`

-------------------------------------------------------------------
Deployment:
-------------------------------------------------------------------

1. Pull the latest change
- `git pull origin main`

2. Optional: If there is a change in the staticfiles.
- Add a line in `settings.py`
- `STATIC_ROOT = /var/www/<project_name>/static` or - `STATIC_ROOT = /var/www/<project_name>/`
- run `python manage.py collectstatic`

3. Optional: If there is new migration file.
- Open env: `source store@3.10.7/bin/activate`
- `python manage.py migrate`

3. Restart Gunicorn
- `sudo systemctl restart <project_name>_gunicorn`

4. Reload Nginx
- `sudo systemctl reload nginx`

-------------------------------------------------------------------
Help:
-------------------------------------------------------------------
• Nginx commands/tips:
- `sudo nginx -t`
- `sudo systemctl start nginx`
- `sudo systemctl reload nginx`
- `sudo systemctl stop nginx`
- `sudo systemctl status nginx`
- Check log: `sudo tail -F /var/log/nginx/error.log`
- If there is a new config: `sudo ln -s /etc/nginx/sites-available/app.galinduh.co.conf /etc/nginx/sites-enabled/`

• Gunicorn commands/tips:
- `sudo systemctl daemon-reload`
- `sudo systemctl enable <project_name>_gunicorn`
- `sudo systemctl start <project_name>_gunicorn`
- `sudo systemctl restart <project_name>_gunicorn`
- `sudo systemctl stop <project_name>_gunicorn`
- `sudo systemctl status <project_name>_gunicorn`

-------------------------------------------------------------------
Projects: <project_name> <port>
-------------------------------------------------------------------
1. JNS Motoshtop - jns (9000)
