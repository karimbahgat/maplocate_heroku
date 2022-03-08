# print env variables (see also those inherited from project envs in settings)
env

# install python modules
#pip3 install -r requirements.txt

# download gazetteer data file
mkdir /data/
wget --no-verbose -O /data/gazetteers.zip https://filedn.com/lvxzpqbRuTkLnAjfFXe7FFu/Gazetteer%20DB/gazetteers%202021-12-03.zip
ls /data/ -a
unzip /data/gazetteers.zip -d /data/
#rm /home/cdsw/data/gazetteers.zip
ls /data/ -a

# test that tesseract works
tesseract --version
which tesseract
