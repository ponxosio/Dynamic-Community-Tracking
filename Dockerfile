FROM python:3.6.4-stretch

# INSTALL ffmpeg FOR mp4 EXPORTATION
RUN apt-get -qq update

# NECCESARY FOR igraph
RUN apt-get install -y libigraph0-dev

# INSTALL PDF TO LATEX
RUN apt-get install -y texlive-latex-base
RUN apt-get install -y texlive-fonts-recommended
RUN apt-get install -y texlive-fonts-extra
RUN apt-get install -y texlive-latex-extra

# INSTALL ffmpeg FOR mp4 EXPORTATION
# RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-get install -y ffmpeg

RUN pip3 install numpy
RUN pip3 install scipy
RUN pip3 install matplotlib
RUN pip3 install pandas
RUN pip3 install python-igraph
RUN pip3 install cairocffi
RUN pip3 install Wand
RUN pip3 install git+git://github.com/IngoScholtes/pyTempNets.git
RUN pip3 install jupyter
RUN pip3 install deap

# ENV
ENV NUMBER_PROCESSES=8

# MAKE JUPYTER USER
RUN useradd -ms /bin/bash jupyter

USER jupyter
WORKDIR /home/jupyter

# MAKE DEAFULT CONFIG
RUN jupyter notebook --generate-config
RUN mkdir host_data

# ENTRYPOINT ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser"]
# ENTRYPOINT ["/bin/bash"]
