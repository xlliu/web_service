#rm -rf edy_web_services/
#svn checkout svn://112.126.70.69/datapr edy_web_services --username yulong --password Galliano89
cd edy_web_services
nohup python tornado_server.py &
cd ..
ps -ef | grep tornado_server | grep -v "grep" | awk '{print $2}' > edy_web_services.pid
echo "============================================== edy_web_services.pid was written to Success ========================================================="
cd edy_web_services.1
nohup python tornado_server_1.py &
cd ..
ps -ef | grep tornado_server_1 | grep -v "grep" | awk '{print $2}' > edy_web_services_1.pid
echo "============================================== edy_web_services_1.pid was written to Success ========================================================="