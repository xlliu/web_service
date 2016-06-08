#rm -rf edy_web_services/
#svn checkout svn://112.126.70.69/datapr edy_web_services --username yulong --password Galliano89
cd edy_web_services
nohup python tornado_server.py &
cd ..
ps -ef | grep tornado_server | grep -v "grep" | awk '{print $2}' > edy_web_services.pid
echo "===================================================================================================================================================="
echo "============================================== edy_web_services.pid was written to Success ========================================================="
echo "===================================================================================================================================================="
cd edy_web_services
tail -f nohup.out
