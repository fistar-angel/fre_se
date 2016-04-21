#!/bin/bash


####################
#    FUNCTIONS
####################

function is_IP() {

if [ $1 == "localhost" ]; then
	return 0
fi

if [ `echo $1 | grep -o '\.' | wc -l` -ne 3 ]; then
        echo "HOST '$1' does not look like an IP Address (does not contain 3 dots).";
        exit 1;
elif [ `echo $1 | tr '.' ' ' | wc -w` -ne 4 ]; then
        echo "HOST '$1' does not look like an IP Address (does not contain 4 octets).";
        exit 1;
else
        for OCTET in `echo $1 | tr '.' ' '`; do
                if ! [[ $OCTET =~ ^[0-9]+$ ]]; then
                        echo "HOST '$1' does not look like in IP Address (octet '$OCTET' is not numeric).";
                        exit 1;
                elif [[ $OCTET -lt 0 || $OCTET -gt 255 ]]; then
                        echo "HOST '$1' does not look like in IP Address (octet '$OCTET' in not in range 0-255).";
                        exit 1;
                fi
        done
fi

return 0;
}


function check_port() {

if [ "$1" -lt 1023 ] || [ "$1" -gt 65535 ]; then
	echo "PORT '$1' is out of range 1023-65535";
	exit 1;
fi

return 0;
}


function check_args() {
if [ "$1" != 2 ]; then
    printf "Invalid number of arguments\n"
    printf "Use the command: ./orion2mysqlBroker.sh <HOST_IP> <PORT>\n"
    exit 1;
fi

return 0;
}


####################
#	MAIN
####################
check_args $#
is_IP $1 
check_port $2


url='http://'$1':'$2'/testing'
printf "GET $url\n"
curl -i -H "Accept: application/json" $url
printf "\n"

# end
