FROM ubuntu:16.04
RUN echo "Building the Statistical Computing Platform of The Future"
RUN apt-get -y update && apt-get -y install 
RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime
RUN apt-get install -y -qq apache2 apache2-utils wget vim

RUN echo -------- Provisioning Apache------------
RUN apt-get install -y -qq apache2 apache2-utils 
RUN echo "Servername localhost" > "/etc/apache2/conf-available/fqdn.conf"
RUN a2enconf fqdn
RUN a2enmod rewrite 
RUN a2dissite 000-default.conf

RUN echo Restart Apache
RUN service apache2 restart


RUN echo "************	Neo4j install	***********************"
RUN wget -O - https://debian.neo4j.org/neotechnology.gpg.key | apt-key add -
RUN echo 'deb http://debian.neo4j.org/repo stable/' >/tmp/neo4j.list
RUN mv /tmp/neo4j.list /etc/apt/sources.list.d
RUN apt-get -qq update
RUN apt-get install -y -qq neo4j 
# RUN cp /neo4j.conf /etc/neo4j/neo4j.conf
RUN neo4j restart


RUN echo -----Install pips for python 2.7 and 3, virtualenv, virtualenvwrapper-----
RUN apt-get install -y -qq python-pip 
RUN apt-get install -y -qq python3-pip 
RUN pip install --upgrade pip virtualenv virtualenvwrapper

RUN ["/bin/bash", "-c", "/usr/local/bin/virtualenvwrapper.sh"] 

#try using this to install Mike's requirements as part of provisioning
#sudo pip install -r /vagrant/requirements.txt
#sudo pip3 install -r /vagrant/requirements.txt
#autoenv will automatically activate the appropriate virtualenv when cd-ing to 
#project directory
#nevermind. I don't want to ovveride 'cd' command unless need to, which this does
#git clone git://github.com/kennethreitz/autoenv.git ~/.autoenv
#$ echo 'source ~/.autoenv/activate.sh' 1>> ~/.bashrc

RUN echo ************  Install mod_wsgi, django,lxml  ***********************
RUN  apt-get install -y -qq libapache2-mod-wsgi python-django python-lxml






