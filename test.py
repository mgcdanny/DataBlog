from appFolder.models import MainData


fj = open("data/projects.json","rb")
theJson = fj.write()

MainData(id= 0, thePage= 'test', theData=theJson)