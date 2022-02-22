#!/bin/sh
cd /fleta/fleta_symevent
export PATH=/fleta/iBRM/ibrm_agent_v1/python27/bin:$PATH
while :
do

        python fletaSymEvent.py
        sleep 300
done
