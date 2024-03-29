ANVIL BAZAAR FORGE
==================

Introduction
------------
Anvil is a software forge dedicated to bazaar. It is written in
python and web.py.

Install
-------

### Dependencies
- a Unix-like server
- MySQL
- web.py
- mako for python
- MySQLdb for python
- markdown for python

### Optional dependencies
- Apache, lighttpd or other
- mod_wsgi, mod_fcgi or mod_python, mod_rewrite, suexec for the web server

### Procedure
The setup I'm describing here uses Apache with mod_fcgid and
mod_rewrite.

Make sure all dependencies are installed. Then create a new user (I
recommend the username 'bzr'). All source code repositories will be
kept in this user's home folder. Don't assign a password to this user
(we don't need anybody to log in as him). I use the following command
in Debian:

   useradd -m -d /var/bzr/ bzr

Note that I specify the user's directory to be /var/bzr. The bzr group
will be created along with the user. If it doesn't on your system then
create the group 'bzr' manually and assign the user to it.

Checkout or extract Anvil in a directory, for instance
/var/www/anvil/. Then set up this directory as a vhost or your default
host. Make sure this directory is recursively owned by the 'bzr' user
like so:

   chown -R bzr:bzr /var/www/anvil/

Create a database and user on your MySQL server. Run the SQL script
schema.sql in your newly created MySQL database.

Copy anvil.ini.dist as /etc/anvil.ini and edit the configuration to
suit your needs.

Now we need to setup Apache so it will run anvil.py on every request
and pass it through fcgid running as bzr. Mimic the following
configuration:

    <VirtualHost *:80>
       ServerAdmin admin@localhost
       DocumentRoot /var/www/anvil

       SuexecUserGroup bzr bzr

       <Directory />
          Options FollowSymlinks
          AllowOverride None
       </Directory>

       Alias /src/ "/var/bzr/"
       <Directory "/var/bzr/">
          Options Indexes FollowSymlinks
          AllowOverride None
       </Directory>

       <Files anvil.py>
          SetHandler fcgid-script
          Options +ExecCGI
       </Files>

       <IfModule mod_rewrite.c>
          RewriteEngine on
          RewriteRule ^/src/\*(.+)$ /src/users/$1 [PT]
          RewriteRule ^/src/\(.+)$ /src/projects/$1 [PT]

          RewriteCond %{REQUEST_URI} !^/static
          RewriteCond %{REQUEST_URI} !^/favicon.ico
          RewriteCond %{REQUEST_URI} !^/pavatar.png
          RewriteCond %{REQUEST_URI} !^/anvil.py
          RewriteCond %{REQUEST_URI} !^/src
          RewriteRule ^/(.*)$ /anvil.py/$1 [PT]
       </IfModule>

       ErrorLog ${APACHE_LOG_DIR}/error.log
       LogLevel notice

       CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>

OK, now if you navigate on your vhost, you should see Anvil's welcome
screen. If you go onto http://<host>/src/, you should see a dirlist
for source access (make sure this works).

Link anvillib to your python path (careful to replace '2.x' with the
real one):

     ln -s /var/www/anvil/anvillib /usr/lib/python2.x/

You now need to install the anv-serve bazaar plugin. For this, copy or
preferably symlink the bzrplugin/anvserve directory to the 'bzr'
user's plugin directory: /var/bzr/.bazaar/plugins/.

Now we're done. You might also want to setup your server so it
provides https access to users.

