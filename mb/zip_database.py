import zipfile
import glob

files = glob.glob('*.csv')
z = zipfile.ZipFile('myzip.zip', 'w')

for x in files:
    z.write(x)
    print x
z.close()
