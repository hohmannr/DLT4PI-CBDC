FROM quorum-node

RUN apk add python3 py-pip python3-dev g++ gcc && pip3 install web3

COPY governing.py /bin/governing
COPY cbdc.py /bin/cbdc
COPY ccbdc.py /bin/ccbdc

CMD ["/bin/sh"]
