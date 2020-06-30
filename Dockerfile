FROM registry.access.redhat.com/ubi8/python-36

USER root

RUN yum update-minimal --security --sec-severity=Important --sec-severity=Critical --disableplugin=subscription-manager -y && rm -rf /var/cache/yum
RUN yum update libnghttp2 kernel-headers gnutls git systemd-libs systemd-pam systemd --disableplugin=subscription-manager -y && rm -rf /var/cache/yum
RUN yum -y remove nodejs && rm -rf /var/cache/yum
USER 1001

LABEL name="isc-car-connector-tenable" \
			vendor="tenable.io" \
			summary="tenable connector to Connect Asset/Risk (CAR)" \
			release="1.2" \
			version="1.2.0.0" \
			description="Tenable connector feeds CAR with assets informations and vulnerabilities."

COPY ./configurations /usr/src/app/configurations
COPY /licenses/LA_en /licenses/LA_en

RUN pip install tenable-ibm-cp4s

CMD tenable-ibm-cp4s