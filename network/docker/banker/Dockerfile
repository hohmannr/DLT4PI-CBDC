FROM quorum-node

RUN apk add python3 py-pip python3-dev g++ gcc && pip3 install web3

COPY cbdc.py /bin/cbdc

CMD ["/bin/sh"]
