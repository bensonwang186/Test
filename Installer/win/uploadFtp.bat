@echo off

::FTP login info
set server=192.168.20.199
set username=lisber
set password=lisber

::FTP command file
set ftp_upload_connect=ftp_upload_connect.txt

:: date and time
set YYYY=%date:~0,4%
set MM=%date:~5,2%
set DD=%date:~8,2%
set HH=%time:~0,2%
set Min=%time:~3,2%

::source/target
set source_file=../ppp_windows_*.exe
set target_path=build/PPP
set target_folder=%YYYY%%MM%%DD%_%HH%%Min%
set md5_file=md5sums


::generate ftp command file
echo open %server%>%ftp_upload_connect%
echo %username%>>%ftp_upload_connect%
echo %password%>>%ftp_upload_connect%
echo prompt>>%ftp_upload_connect%
echo cd %target_path%>>%ftp_upload_connect%
echo mkdir %target_folder%>>%ftp_upload_connect%
echo cd %target_folder%>>%ftp_upload_connect%

for %%a in (%source_file% %md5_file%) do echo mput ../%%a>>%ftp_upload_connect%

echo bye>>%ftp_upload_connect%

::ftp connect with command file
ftp -s:%ftp_upload_connect%

::delete ftp command file
del %ftp_upload_connect% /Q
