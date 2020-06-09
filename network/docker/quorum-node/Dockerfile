FROM alpine:latest

ENV PRIVATE_CONFIG "ignore"

ARG UNAME="quorum-node"
ARG UID=1000

# adding dependecies
RUN apk add git make go linux-headers

# adding new user
RUN adduser -u $UID -S $UNAME

# cloning and making quorum git repo and adding binaries to /bin
RUN git clone https://github.com/jpmorganchase/quorum.git &&\
    cd quorum &&\
    make &&\
    mv ./build/bin/* /bin &&\
    cd .. && rm -r quorum


CMD ["/bin/sh"]

