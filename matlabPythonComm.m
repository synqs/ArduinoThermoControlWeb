filename = 'E:\Labordaten\2017-09\2017-09-25\hdf5_data\run030.h5'

serverstr = ['GET /file/' filename ' HTTP/1.1'];
disp(str)
t = tcpip('localhost', 5000,'Timeout', 5);
fopen(t);
fwrite(t, serverstr);
bytes = fread(t, [1, t.BytesAvailable]);
char(bytes)
fclose(t);
