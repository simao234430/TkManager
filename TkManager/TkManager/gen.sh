for dir in   bind_thirdparty_server rc_server bank_server message_server risk_server
do
    echo $dir
    cd $dir
    thrift --gen py *.thrift
    cd -
done
