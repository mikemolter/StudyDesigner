#!/usr/bin/env bash

#Intended for use on Ubunty 16.04 (Xenial 64bit)
#get rid of stupid GRUB error:
sudo echo "set grub-pc/install_devices /dev/sda" | debconf-communicate
#^^didn't need the debconf-communicate after updating bento16.04 to latest version
#Update 

# sudo apt-get -y -q update 

# sudo apt-get -y -q clean

# sudo apt-get -y -q autoremove

# sudo apt-get -y -q update && sudo apt-get -y -q upgrade

# sudo dpkg --configure -a

# sudo apt-get install -f

# sudo shutdown -r now

export DEBIAN_FRONTEND=noninteractive

sudo apt-get -y -q update 
sudo apt-get -y -q upgrade

echo "---------------- LIBXML2 INSTALL______________________________"
sudo apt-get install -y libxml2 
echo "---------------- LIBXML2 INSTALL FINISH ______________________________"


# Set timezone
ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

#	Apache
echo "-------- Provisioning Apache------------"
sudo apt-get install -y -q apache2 apache2-utils 
echo "Servername localhost" > "/etc/apache2/conf-available/fqdn.conf"
a2enconf fqdn
a2enmod rewrite 
a2dissite 000-default.conf

echo "--------	set /var/www to point to /vagrant	------------"
rm -rf /var/www
ln -fs /vagrant /var/www

#Apache \ Virtual Host setup: 
echo "Provisioning Host File"
cp /vagrant/hostfile /etc/apache2/sites-available/project.conf
a2ensite project.conf
service apache2 reload


#install to get rid of some weird apache error that popped up
# error was:
# root@www:/etc/apache2# apache2ctl status
# /usr/sbin/apache2ctl: 124: www-browser: not found
sudo apt-get install -y -q links


#Restart Apache
# echo "------ Restarting apache 	--------"
service apache2 restart


echo "************	Neo4j install	***********************"
sudo wget -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
echo 'deb http://debian.neo4j.org/repo stable/' >/tmp/neo4j.list
sudo mv /tmp/neo4j.list /etc/apt/sources.list.d
echo "**********	Another apt-get update. Not sure if necessary	***************"
sudo apt-get -q update
sudo apt-get install -y -q neo4j
sudo cp /vagrant/neo4j.conf /etc/neo4j/neo4j.conf
sudo neo4j restart


echo "************	Install pips for python2&3, virtualenv and virtualenvwrapper ***********************"
sudo apt-get install -y -qq python-pip
sudo apt-get install -y -qq python3-pip
pip install --upgrade pip

# sudo apt-get install -y -qq python-virtualenv
# sudo pip install virtualenvwrapper


#try using this to install Mike's requirements as part of provisioning
sudo pip install -r /vagrant/requirements.txt
sudo pip3 install -r /vagrant/requirements.txt
#autoenv will automatically activate the appropriate virtualenv when cd-ing to 
#project directory
#nevermind. I don't want to ovveride 'cd' command unless need to, which this does
#git clone git://github.com/kennethreitz/autoenv.git ~/.autoenv
#$ echo 'source ~/.autoenv/activate.sh' >> ~/.bashrc



# echo "************  Install mod_wsgi  ***********************"
sudo apt-get install -y -qq libapache2-mod-wsgi
# sudo apt-get install -y -qq python-django 
# 

#TODO: get mod_wasgi from https://github.com/GrahamDumpleton/mod_wsgi/archive/4.5.7.tar.gz
#Don't think I need this anymore. apt installed and seemingly loaded the module into apache
#mods-enabled
#tar xvfz mod_wsgi-X.Y.tar.gz
#./configure
#make
#make install




# echo "************  clone StudyDesigner to ~/vagrant shared folder (UNTESTED) ***********************"
 # sudo git@github.com:pressleydavid/StudyDesigner.git /vagrant

# echo "************  clone lxml to ~/vagrant shared folder  ***********************"
# git clone git://github.com/lxml/lxml.git lxml
sudo apt-get install -y -q python-lxml

#Cleanup
# sudo apt-get -y autoremove
# sudo apt-get clean

#Zero out the drive to make it smaller
#(this and apt-get clean/autoremove saved about 400MB of size)
# sudo dd if=/dev/zero of=/EMPTY bs=1M
# sudo rm -f /EMPTY



